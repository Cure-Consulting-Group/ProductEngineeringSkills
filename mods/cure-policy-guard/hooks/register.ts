import type { Register } from 'claude-code'

import { addedText, check, dependencyNames, parentDirs, targetPath, type Violation } from './rules'

/**
 * cure-policy-guard: refuses a file write that breaks a written Cure house
 * rule, unless the person at the keyboard overrides it, and records every
 * override.
 *
 * Scope: Claude's own Write / Edit / MultiEdit / NotebookEdit calls. A Bash
 * command that writes a file (`cat > x`, `sed -i`) is not read here; the
 * repos' CI and scanners remain the backstop for those.
 *
 * Fails closed on the question, open on the plumbing: if the person cannot be
 * asked (headless, dismissed), the write is refused; if the repo or
 * package.json cannot be read, the rules that need them see '' / [] and the
 * path- and text-only rules still apply.
 */

const FILE_TOOLS = new Set(['Write', 'Edit', 'MultiEdit', 'NotebookEdit'])
const OVERRIDES_KEY = 'overrides'
const MAX_OVERRIDES = 200

type Override = { at: string; rule: string; path: string; repo: string }

const REFUSE = 'Refuse the write'
const ALLOW = 'Allow this once (logged)'
const DEFAULT_ASK_SECONDS = 60

/** Repository per directory, so git runs once per folder a session writes in, not per write. */
const repoCache = new Map<string, { repo: string; root: string }>()

export const register: Register = (on, options) => {
  repoCache.clear()
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
      'cure-policy-guard rules: no-cron · level5-vertex-only · minors-new-ai-vendor · hardcoded-secret',
      recent.length === 0
        ? 'No overrides recorded.'
        : 'Recent overrides:\n' +
          recent.map(o => `  ${o.at}  ${o.rule}  ${o.repo}  ${o.path}`).join('\n'),
    ]
    return { text: lines.join('\n') }
  })

  on('tool.call', async ($, e, next) => {
    if (!FILE_TOOLS.has(String(e.tool))) return next(e)
    const path = targetPath(e)
    const added = addedText(e)
    if (!path || !added) return next(e)

    const { repo, root } = await locateRepo($, path)
    const deps = await nearestDependencies($, path, root)
    const violations = check({ path, repo, added, deps })
    if (violations.length === 0) return next(e)

    const summary = violations.map(v => `[${v.rule}] ${v.reason}`).join('\n')
    const answer = await askWithin(
      $,
      `cure-policy-guard: this ${String(e.tool)} to ${shortPath(path)} breaks a house rule:\n${summary}\nAllow it anyway?`,
      { options: [REFUSE, ALLOW], header: 'House rule' },
      askMs,
    )
    if (answer === undefined) return { deny: denial(violations, 'nobody could be asked to override it') }
    if (answer === TIMED_OUT) return { deny: denial(violations, `nobody answered within ${Math.round(askMs / 1000)}s`) }
    if (answer !== ALLOW) return { deny: denial(violations, 'the user refused it') }

    await recordOverride($, violations, path, repo)
    $.ui.log(`cure-policy-guard: override recorded for ${violations.map(v => v.rule).join(', ')} on ${shortPath(path)}`)
    return next(e)
  }).catch(($, e, next) => (next.called ? next(e) : { deny: `cure-policy-guard could not check this ${String(e.tool)} (${next.error.kind}), so it was refused. Retry once; if it fails again, ask the user.` }))
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
