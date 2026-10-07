import type { On } from 'claude-code'

import { countDirty, extractClaims, formatVerdict, isEmptyCompletion, type Claims, type Evidence } from './claims'

/**
 * cure-lane-verifier: when a subagent or tri-lane lane reports back, attach
 * git's own account of the worktrees and branches the report names, so the
 * report is read against evidence. An empty diff behind a "complete" is
 * flagged loudly, to the model and to the person.
 *
 * Where reports arrive:
 *   - a foreground Agent call's result (`tool.call` for `Agent`): the note
 *     rides as `context`, which the model reads after the result;
 *   - a background agent's hand-back, delivered into the conversation as an
 *     engine attachment or a peer message (`prompt.attachment`,
 *     `session.receive`): the note is appended to the text.
 *
 * Read-only: it runs git `rev-parse`, `rev-list`, `diff --shortstat` and
 * `status`, nothing that writes. Fails open: anything git cannot answer is
 * reported as "could not verify" and the report passes through unchanged.
 */

const HANDBACK = /\[Subagent hand-back\]|<task-notification>|<agent-message\b|final report of a subagent/i

export function register(on: On) {
  on('tool.call', async ($, e, next) => {
    if (e.tool !== 'Agent') return next(e)
    const answer = await next(e)
    if (answer.deny !== undefined || e.run_in_background === true) return answer
    const text = typeof answer.text === 'string' ? answer.text : safeJson(answer.result)
    const note = await verify($, text)
    if (!note) return answer
    return { ...answer, context: [...(answer.context ?? []), note] }
  })

  on('prompt.attachment', async ($, e, next) => {
    if (e.origin.kind !== 'engine' || !HANDBACK.test(e.text)) return next(e)
    const note = await verify($, e.text)
    return note ? next({ ...e, text: `${e.text}\n\n${note}` }) : next(e)
  })

  on('session.receive', async ($, e, next) => {
    if (!HANDBACK.test(e.text)) return next(e)
    const note = await verify($, e.text)
    return note ? next({ ...e, text: `${e.text}\n\n${note}` }) : next(e)
  })
}

const safeJson = (v: unknown) => {
  try {
    return typeof v === 'string' ? v : JSON.stringify(v) ?? ''
  } catch {
    return ''
  }
}

/** The verification note for a report's text, '' when it names nothing git can check. */
async function verify($: any, text: string): Promise<string> {
  const claims = extractClaims(text)
  if (claims.paths.length === 0 && claims.branches.length === 0) return ''
  const evidence = await gather($, claims)
  const note = formatVerdict(claims, evidence)
  if (note && isEmptyCompletion(claims.claimsDone, evidence)) {
    $.ui.toast('cure-lane-verifier: a report claims completion but its branch is empty', { timeoutMs: 10000 })
  }
  if (note) $.ui.log(note.split('\n')[0])
  return note
}

async function git($: any, cwd: string, ...args: string[]) {
  return $.process.run(['git', '-C', cwd, ...args], { timeoutMs: 10000 })
}

async function baseOf($: any, cwd: string): Promise<string> {
  const head = await git($, cwd, 'rev-parse', '--abbrev-ref', 'origin/HEAD')
  if (head.exitCode === 0 && head.stdout.trim()) return head.stdout.trim()
  for (const b of ['origin/main', 'origin/master', 'main', 'master']) {
    if ((await git($, cwd, 'rev-parse', '--verify', '--quiet', b)).exitCode === 0) return b
  }
  return 'HEAD'
}

async function measure($: any, cwd: string, ref: string, target: string, withDirty: boolean): Promise<Evidence> {
  const base = await baseOf($, cwd)
  const ahead = await git($, cwd, 'rev-list', '--count', `${base}..${ref}`)
  const stat = await git($, cwd, 'diff', '--shortstat', `${base}...${ref}`)
  if (ahead.exitCode !== 0 || stat.exitCode !== 0) {
    return { target, ahead: 0, shortstat: '', dirty: 0, base, error: (ahead.stderr || stat.stderr).trim().split('\n')[0] || 'git failed' }
  }
  const dirty = withDirty ? countDirty((await git($, cwd, 'status', '--porcelain')).stdout) : 0
  return { target, ahead: Number(ahead.stdout.trim()) || 0, shortstat: stat.stdout.trim(), dirty, base }
}

async function gather($: any, claims: Claims): Promise<Evidence[]> {
  const out: Evidence[] = []
  const seenTops = new Set<string>()
  for (const path of claims.paths) {
    try {
      if (!(await $.fs.exists(path))) continue
      const top = await git($, path, 'rev-parse', '--show-toplevel')
      if (top.exitCode !== 0) continue
      const root = top.stdout.trim()
      if (seenTops.has(root)) continue
      seenTops.add(root)
      out.push({ ...(await measure($, root, 'HEAD', root, true)), kind: 'path' })
    } catch (err) {
      out.push({ target: path, ahead: 0, shortstat: '', dirty: 0, base: '?', error: String(err) })
    }
  }
  if (claims.branches.length > 0) {
    const cwd = await $.session.root()
    for (const branch of claims.branches) {
      try {
        const exists = await git($, cwd, 'rev-parse', '--verify', '--quiet', branch)
        if (exists.exitCode !== 0) {
          out.push({ target: branch, ahead: 0, shortstat: '', dirty: 0, base: '?', error: `no branch \`${branch}\` in ${cwd.split('/').pop()}` })
          continue
        }
        out.push({ ...(await measure($, cwd, branch, branch, false)), kind: 'branch' })
      } catch (err) {
        out.push({ target: branch, ahead: 0, shortstat: '', dirty: 0, base: '?', error: String(err) })
      }
    }
  }
  return out
}
