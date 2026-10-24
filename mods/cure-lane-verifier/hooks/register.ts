import type { On } from 'claude-code'

import { countDirty, extractClaims, formatVerdict, isEmptyCompletion, type Claims, type Evidence } from './claims'
import { git, gitAll } from './shared/git'

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

/** The base a ref is measured against: origin/HEAD, else the first default branch that exists. */
async function baseOf($: any, cwd: string): Promise<string> {
  const candidates = ['origin/main', 'origin/master', 'main', 'master']
  const [head, ...verified] = await gitAll($, cwd, [
    ['rev-parse', '--abbrev-ref', 'origin/HEAD'],
    ...candidates.map(b => ['rev-parse', '--verify', '--quiet', b]),
  ])
  if (head.exitCode === 0 && head.stdout.trim()) return head.stdout.trim()
  const i = verified.findIndex(r => r.exitCode === 0)
  return i >= 0 ? candidates[i] : 'HEAD'
}

async function measure($: any, cwd: string, ref: string, target: string, withDirty: boolean, base: string): Promise<Evidence> {
  const [ahead, stat, status] = await gitAll($, cwd, [
    ['rev-list', '--count', `${base}..${ref}`],
    ['diff', '--shortstat', `${base}...${ref}`],
    ...(withDirty ? [['status', '--porcelain']] : []),
  ])
  if (ahead.exitCode !== 0 || stat.exitCode !== 0) {
    return { target, ahead: 0, shortstat: '', dirty: 0, base, error: (ahead.stderr || stat.stderr).trim().split('\n')[0] || 'git failed' }
  }
  const dirty = withDirty && status ? countDirty(status.stdout) : 0
  return { target, ahead: Number(ahead.stdout.trim()) || 0, shortstat: stat.stdout.trim(), dirty, base }
}

/** git's evidence for each named path and branch, gathered in parallel (the 10 s hook limit counts our own time only). */
async function gather($: any, claims: Claims): Promise<Evidence[]> {
  const tops = await Promise.all(
    claims.paths.map(async path => {
      if (!(await $.fs.exists(path).catch(() => false))) return undefined
      const top = await git($, path, ['rev-parse', '--show-toplevel'])
      return top.exitCode === 0 ? top.stdout.trim() : undefined
    }),
  )
  const roots = [...new Set(tops.filter((t): t is string => !!t))]
  const cwd: string | undefined = claims.branches.length > 0 ? await $.session.root() : undefined
  const pathEvidence = Promise.all(
    roots.map(async root => ({ ...(await measure($, root, 'HEAD', root, true, await baseOf($, root))), kind: 'path' as const })),
  )
  const branchEvidence = cwd
    ? (async () => {
        const [base, ...exists] = await Promise.all([
          baseOf($, cwd),
          ...claims.branches.map(b => git($, cwd, ['rev-parse', '--verify', '--quiet', b])),
        ])
        return Promise.all(
          claims.branches.map(async (branch, i): Promise<Evidence> =>
            exists[i].exitCode !== 0
              ? { target: branch, ahead: 0, shortstat: '', dirty: 0, base: '?', error: `no branch \`${branch}\` in ${cwd.split('/').pop()}` }
              : { ...(await measure($, cwd, branch, branch, false, base)), kind: 'branch' as const },
          ),
        )
      })()
    : Promise.resolve([] as Evidence[])
  const [p, b] = await Promise.all([pathEvidence, branchEvidence])
  return [...p, ...b]
}
