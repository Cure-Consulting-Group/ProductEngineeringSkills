import type { Register } from 'claude-code'

import {
  PROTECTED_REPOS,
  addedText,
  aiEgress,
  check,
  commandDir,
  dependencyNames,
  parentDirs,
  parseStateTargets,
  stateClaim,
  stateFromPath,
  targetPath,
  type Violation,
} from './rules'
import { vendorHostIn } from './shared/rules'

/**
 * cure-policy-guard: refuses a file write that breaks a written Cure house
 * rule, unless the person at the keyboard overrides it, and records every
 * override.
 *
 * Scope:
 * - Claude's own Write / Edit / MultiEdit / NotebookEdit calls: the file rules,
 *   plus state-target ownership in a repo that keeps claims (was claim-guard).
 * - Bash and WebFetch: a request to a consumer AI API from a PHI or minors'
 *   repo (was egress-guard). The host is matched first, with no subprocess, so
 *   an ordinary Bash call costs nothing here.
 * A Bash command that writes a file (`cat > x`, `sed -i`) is not read for the
 * file rules; the repos' CI and scanners remain the backstop for those.
 *
 * Fails closed on the question, open on the plumbing: if the person cannot be
 * asked (headless, dismissed), the write is refused; if the repo or
 * package.json cannot be read, the rules that need them see '' / [] and the
 * path- and text-only rules still apply.
 */

const FILE_TOOLS = ['Write', 'Edit', 'MultiEdit', 'NotebookEdit'] as const
const OVERRIDES_KEY = 'overrides'
const MAX_OVERRIDES = 200

type Override = { at: string; rule: string; path: string; repo: string }

const REFUSE = 'Refuse it'
const ALLOW = 'Allow this once (logged)'
const TARGETS_FILE = '.agents/state-targets.md'

/** This machine's host name, read once per load and only when a state claim needs it. */
let hostName: string | undefined
const DEFAULT_ASK_SECONDS = 60

/** Repository per directory, so git runs once per folder a session writes in, not per write. */
const repoCache = new Map<string, { repo: string; root: string }>()

export const register: Register = (on, options) => {
  repoCache.clear()
  hostName = undefined
  const askMs = askTimeoutMs(options.askTimeoutSeconds)

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'policy-guard',
      description: 'Show the house rules the guard enforces and the recent overrides',
    })
    return next(e)
  })

  on('command.run', { command: 'policy-guard' }, async $ => {
    const log = ((await $.store.get(OVERRIDES_KEY)) as Override[] | undefined) ?? []
    const recent = log.slice(-10).reverse()
    const lines = [
      'cure-policy-guard rules: no-cron · level5-vertex-only · minors-new-ai-vendor · hardcoded-secret · ai-egress · state-claim',
      `Protected repos: ${PROTECTED_REPOS.map(r => `${r.repo}${r.data ? ` (${r.data})` : ''}${r.stateClaims ? ' (state claims)' : ''}`).join(', ')}`,
      recent.length === 0
        ? 'No overrides recorded.'
        : 'Recent overrides:\n' +
          recent.map(o => `  ${o.at}  ${o.rule}  ${o.repo}  ${o.path}`).join('\n'),
    ]
    return { text: lines.join('\n') }
  })

  on('tool.call', { tool: ['Bash', 'WebFetch'] }, async ($, e, next) => {
    const text = String(e.tool) === 'Bash' ? String((e as any).command ?? '') : String((e as any).url ?? '')
    // No vendor host in the text: nothing to look up, no subprocess.
    if (!vendorHostIn(text)) return next(e)
    const dir = (String(e.tool) === 'Bash' && commandDir(text)) || (await $.session.cwd())
    // locateRepo walks up from a file's parent: `<dir>/.` makes it start at the folder itself.
    const { repo } = await locateRepo($, `${dir.replace(/\/+$/, '')}/.`)
    const violation = aiEgress(text, repo)
    if (!violation) return next(e)
    const answer = await askWithin(
      $,
      `cure-policy-guard: this ${String(e.tool)} in ${repo} breaks a house rule:\n[${violation.rule}] ${violation.reason}\nAllow it anyway?`,
      { options: [REFUSE, ALLOW], header: 'House rule' },
      askMs,
    )
    const refusal = refusalFor([violation], answer, askMs)
    if (refusal) return { deny: refusal }
    await recordOverride($, [violation], text.slice(0, 200), repo)
    $.ui.log(`cure-policy-guard: override recorded for ai-egress in ${repo}`)
    return next(e)
  }).catch(refuse)

  on('tool.call', { tool: [...FILE_TOOLS] }, async ($, e, next) => {
    const path = targetPath(e)
    const added = addedText(e)
    if (!path || !added) return next(e)

    const { repo, root } = await locateRepo($, path)
    const deps = await nearestDependencies($, path, root)
    const violations = check({ path, repo, added, deps })
    const claim = stateFromPath(path) ? await claimViolation($, path, repo, root) : undefined
    if (claim) violations.push(claim)
    if (violations.length === 0) return next(e)

    const summary = violations.map(v => `[${v.rule}] ${v.reason}`).join('\n')
    const answer = await askWithin(
      $,
      `cure-policy-guard: this ${String(e.tool)} to ${shortPath(path)} breaks a house rule:\n${summary}\nAllow it anyway?`,
      { options: [REFUSE, ALLOW], header: 'House rule' },
      askMs,
    )
    const refusal = refusalFor(violations, answer, askMs)
    if (refusal) return { deny: refusal }

    await recordOverride($, violations, path, repo)
    $.ui.log(`cure-policy-guard: override recorded for ${violations.map(v => v.rule).join(', ')} on ${shortPath(path)}`)
    return next(e)
  }).catch(refuse)
}

/** A guard that failed before next() refuses the call: it fails closed. */
function refuse($: any, e: any, next: any) {
  return next.called
    ? next(e)
    : { deny: `cure-policy-guard could not check this ${String(e.tool)} (${next.error.kind}), so it was refused. Retry once; if it fails again, ask the user.` }
}

/** The deny text for an answer, or undefined when the person allowed it. */
function refusalFor(violations: Violation[], answer: string | undefined, askMs: number): string | undefined {
  if (answer === undefined) return denial(violations, 'nobody could be asked to override it')
  if (answer === TIMED_OUT) return denial(violations, `nobody answered within ${Math.round(askMs / 1000)}s`)
  if (answer !== ALLOW) return denial(violations, 'the user refused it')
  return undefined
}

/** A write to a state another machine owns, from the repo's own .agents/state-targets.md. */
async function claimViolation($: any, path: string, repo: string, root: string): Promise<Violation | undefined> {
  if (!root) return undefined
  const targets = `${root}/${TARGETS_FILE}`
  if (!(await $.fs.exists(targets))) return undefined
  const claims = parseStateTargets(String(await $.fs.read(targets)))
  if (claims.size === 0) return undefined
  if (hostName === undefined) {
    const res = await $.process.run(['hostname'], { timeoutMs: 5000 }).catch(() => undefined)
    hostName = res && res.exitCode === 0 ? res.stdout.trim() : ''
  }
  return hostName ? stateClaim(path, repo, hostName, claims) : undefined
}

const TIMED_OUT = '\u0000timed out'

function askTimeoutMs(seconds: unknown): number {
  const n = typeof seconds === 'number' && Number.isFinite(seconds) ? seconds : DEFAULT_ASK_SECONDS
  return Math.min(600, Math.max(5, n)) * 1000
}

/**
 * `$.ui.ask` raced against a clock, so an unattended session or a /loop never
 * stalls on a question: resolves the answer, TIMED_OUT, or undefined when the
 * question was dismissed or nobody can be asked (`-p`). The wait stays inside a
 * `$` call, so it does not count against the hook's own time limit.
 */
async function askWithin($: any, question: string, opts: unknown, ms: number): Promise<string | undefined> {
  let timer: { cancel: () => void } | undefined
  const clock = new Promise<string>(resolve => {
    timer = $.clock.after(ms, () => resolve(TIMED_OUT))
  })
  try {
    return await Promise.race([$.ui.ask(question, opts).catch(() => undefined), clock])
  } finally {
    timer?.cancel()
  }
}

function denial(violations: Violation[], why: string): string {
  return (
    `Blocked by cure-policy-guard (${why}). ` +
    violations.map(v => `${v.rule}: ${v.reason} Source: ${v.source}.`).join(' ') +
    ' Do not retry the same write; change the approach or ask the user.'
  )
}

export const shortPath = (p: string, maxLen = 38): string => {
  const parts = p.split('/').filter(Boolean)
  const tail = parts.slice(-3).join('/')
  if (tail.length <= maxLen) return tail
  const filename = parts[parts.length - 1] ?? ''
  if (parts.length <= 2) return tail
  const dir = parts[parts.length - 2] ?? ''
  const mid = `.../${dir}/${filename}`
  return mid.length <= maxLen ? mid : `.../${filename}`
}

/** The repository's name (main checkout's directory, also from a worktree) and root. */
async function locateRepo($: any, path: string): Promise<{ repo: string; root: string }> {
  try {
    const dir = await firstExistingDir($, path)
    if (!dir) return { repo: '', root: '' }
    const hit = repoCache.get(dir)
    if (hit) return hit
    // One git call answers both: the common dir (names the main checkout, also from a worktree) and the toplevel.
    const res = await $.process.run(['git', '-C', dir, 'rev-parse', '--path-format=absolute', '--git-common-dir', '--show-toplevel'], { timeoutMs: 5000 })
    const [common = '', top = ''] = res.exitCode === 0 ? res.stdout.trim().split('\n') : []
    const commonDir = common.trim().replace(/\/$/, '')
    const repoDir = commonDir.endsWith('/.git') ? commonDir.slice(0, -5) : commonDir
    const found = commonDir ? { repo: repoDir.split('/').pop() ?? '', root: top.trim() } : { repo: '', root: '' }
    repoCache.set(dir, found)
    if (repoCache.size > 200) repoCache.delete(repoCache.keys().next().value as string)
    return found
  } catch {
    return { repo: '', root: '' }
  }
}

async function firstExistingDir($: any, path: string): Promise<string | undefined> {
  for (const dir of parentDirs(path)) {
    if (await $.fs.exists(dir)) return dir
  }
  return undefined
}

/** Dependencies of the nearest package.json between the file and the repo root. */
async function nearestDependencies($: any, path: string, root: string): Promise<string[]> {
  if (!root) return []
  try {
    for (const dir of parentDirs(path)) {
      if (!dir.startsWith(root)) break
      const pkg = `${dir}/package.json`
      if (await $.fs.exists(pkg)) return dependencyNames(await $.fs.read(pkg))
    }
  } catch {
    // unreadable: treat as no dependencies, which makes the vendor rule stricter
  }
  return []
}

async function recordOverride($: any, violations: Violation[], path: string, repo: string) {
  const log = ((await $.store.get(OVERRIDES_KEY)) as Override[] | undefined) ?? []
  const at = new Date(await $.clock.now()).toISOString()
  for (const v of violations) log.push({ at, rule: v.rule, path, repo })
  await $.store.set(OVERRIDES_KEY, log.slice(-MAX_OVERRIDES))
}
