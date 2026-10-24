/**
 * Pure functions for parsing, resolving and verifying file:line citations.
 *
 * Nothing here touches disk: `checkCitations` takes a Probe, so the hooks module
 * gives it `$.fs` and an offline run can give it the real file system.
 */

export type Citation = {
  raw: string
  path: string
  line: number
  endLine?: number
}

export type StaleCitation = {
  citation: Citation
  reason: string
}

/** File extensions a citation may end in. A TLD (`.com`, `.io`) is not one, so `host.tld:port` never matches. */
const EXTENSIONS = [
  'ts', 'tsx', 'mts', 'cts', 'js', 'jsx', 'mjs', 'cjs', 'py', 'pyi', 'go', 'rs', 'kt', 'kts', 'java', 'swift',
  'm', 'mm', 'c', 'h', 'cc', 'cpp', 'hpp', 'cs', 'rb', 'php', 'scala', 'dart', 'lua', 'ex', 'exs', 'sh', 'bash',
  'zsh', 'ps1', 'sql', 'md', 'mdx', 'txt', 'json', 'jsonc', 'jsonl', 'yml', 'yaml', 'toml', 'ini', 'cfg',
  'conf', 'xml', 'html', 'htm', 'css', 'scss', 'less', 'vue', 'svelte', 'tf', 'tfvars', 'hcl', 'gradle',
  'properties', 'plist', 'rules', 'proto', 'graphql', 'gql', 'csv', 'ipynb',
]

// Not preceded by a path, word, URL or `user@host:` character, so a URL's path or a
// host name never starts a match; the extension is whole (not `.json` inside `.jsonc`).
const CITE_REGEX = new RegExp(
  String.raw`(?<![\w.\-/~@:%])((?:~/|\.{1,2}/|/)?(?:[\w.\-]+/)*[\w\-][\w.\-]*\.(?:${EXTENSIONS.join('|')}))(?:#L|:)(\d+)(?:(?:-L?|–)(\d+))?(?!\w|\.\d)`,
  'g',
)

export function extractCitations(text: string): Citation[] {
  if (!text || typeof text !== 'string') return []
  const citations: Citation[] = []
  const seen = new Set<string>()
  for (const match of text.matchAll(CITE_REGEX)) {
    const path = match[1]
    const line = parseInt(match[2], 10)
    const endLine = match[3] ? parseInt(match[3], 10) : undefined
    const key = `${path}:${line}${endLine ? `-${endLine}` : ''}`
    if (seen.has(key)) continue
    seen.add(key)
    citations.push({ raw: match[0], path, line, endLine })
  }
  return citations
}

/** Where to look for a cited path: the session's roots (root, git toplevel) and the files it touched. */
export type ResolveContext = {
  roots: readonly string[]
  recent: readonly string[]
  home?: string
  /** Every file the git toplevel tracks, absolute; optional and only searched by suffix. */
  index?: readonly string[]
}

export function normalize(path: string): string {
  const isAbs = path.startsWith('/')
  const out: string[] = []
  for (const part of path.split('/')) {
    if (part === '' || part === '.') continue
    if (part === '..') out.pop()
    else out.push(part)
  }
  return (isAbs ? '/' : '') + out.join('/')
}

/** True when the citation names a directory (or is absolute): a miss is then a real miss. */
export function isExplicit(path: string): boolean {
  return path.includes('/')
}

/** Candidate absolute paths for a cited path, most likely first, without duplicates. */
export function candidates(path: string, ctx: ResolveContext): string[] {
  const out: string[] = []
  const add = (p: string) => {
    const n = normalize(p)
    if (!out.includes(n)) out.push(n)
  }
  if (path.startsWith('~/')) {
    if (ctx.home) add(`${ctx.home}/${path.slice(2)}`)
    return out
  }
  if (path.startsWith('/')) {
    add(path)
    return out
  }
  const rel = normalize(path)
  for (const root of ctx.roots) add(`${root}/${rel}`)
  const tail = `/${rel}`
  for (let i = ctx.recent.length - 1; i >= 0; i--) {
    const r = ctx.recent[i]
    if (r.endsWith(tail)) add(r)
  }
  for (const f of ctx.index ?? []) if (f.endsWith(tail)) add(f)
  return out
}

export function verifyCitation(
  citation: Citation,
  exists: boolean,
  lineCount: number,
): StaleCitation | undefined {
  if (!exists) return { citation, reason: `file not found` }
  if (citation.line <= 0) return { citation, reason: `line number must be positive (got ${citation.line})` }
  if (citation.line > lineCount) {
    return { citation, reason: `line ${citation.line} exceeds file length (${lineCount} lines)` }
  }
  if (citation.endLine && citation.endLine > lineCount) {
    return { citation, reason: `end line ${citation.endLine} exceeds file length (${lineCount} lines)` }
  }
  return undefined
}

/**
 * How the checker reaches disk: `lines` is a file's line count, or undefined when
 * the path is not a readable file; `exists` is true for any entry (file or folder).
 */
export type Probe = {
  lines: (absPath: string) => Promise<number | undefined>
  exists: (absPath: string) => Promise<boolean>
}

function parent(path: string): string {
  const cut = path.lastIndexOf('/')
  return cut <= 0 ? '/' : path.slice(0, cut)
}

/**
 * The repositories the session touched: for each recent file, the nearest folder
 * above it holding `.git`. Newest first, at most `max`. `known` caches answers.
 */
export async function discoverRoots(
  recent: readonly string[],
  probe: Probe,
  known: Map<string, boolean> = new Map(),
  max = 8,
): Promise<string[]> {
  const roots: string[] = []
  for (let i = recent.length - 1; i >= 0 && roots.length < max; i--) {
    let dir = recent[i]
    for (let depth = 0; depth < 12 && dir.split('/').length > 3; depth++) {
      let hasGit = known.get(dir)
      if (hasGit === undefined) {
        hasGit = await probe.exists(`${dir}/.git`)
        known.set(dir, hasGit)
      }
      if (hasGit) {
        if (!roots.includes(dir)) roots.push(dir)
        break
      }
      dir = parent(dir)
    }
  }
  return roots
}

export type VerificationResult = {
  total: number
  valid: number
  /**
   * Found nowhere, and nothing says it should be here: a bare file name, or a path
   * whose folder is in none of the session's roots. Not flagged: it may live in a
   * repository this session never touched.
   */
  unverified: number
  stale: StaleCitation[]
}

export async function checkCitations(
  citations: readonly Citation[],
  ctx: ResolveContext,
  probe: Probe,
): Promise<VerificationResult> {
  const res: VerificationResult = { total: citations.length, valid: 0, unverified: 0, stale: [] }
  for (const c of citations) {
    let firstIssue: StaleCitation | undefined
    let ok = false
    for (const abs of candidates(c.path, ctx)) {
      const n = await probe.lines(abs)
      if (n === undefined) continue
      const issue = verifyCitation(c, true, n)
      if (!issue) {
        ok = true
        break
      }
      // A bare file name is ambiguous (every repo has a STATE.md): its range is
      // judged only against a copy this session actually touched.
      if (isExplicit(c.path) || ctx.recent.includes(abs)) firstIssue ??= issue
    }
    if (ok) res.valid += 1
    else if (firstIssue) res.stale.push(firstIssue)
    else if (await isMissingHere(c.path, ctx, probe)) res.stale.push({ citation: c, reason: 'file not found' })
    else res.unverified += 1
  }
  return res
}

/**
 * A path found nowhere is flagged only when it should have been found: it is
 * absolute (or `~/`), or it names a folder that exists under one of the roots.
 */
async function isMissingHere(path: string, ctx: ResolveContext, probe: Probe): Promise<boolean> {
  if (path.startsWith('/') || path.startsWith('~/')) return true
  if (!isExplicit(path)) return false
  const folder = parent(normalize(path))
  for (const root of ctx.roots) if (await probe.exists(`${root}/${folder}`)) return true
  return false
}

export function formatVerificationNotice(res: VerificationResult): string {
  if (res.total === 0) return ''
  if (res.stale.length === 0) return `cure-cite-check: ${res.total} citation(s), none stale`
  const issues = res.stale
    .slice(0, 3)
    .map(s => `${s.citation.path}:${s.citation.line} (${s.reason})`)
    .join(', ')
  const more = res.stale.length > 3 ? ` +${res.stale.length - 3} more` : ''
  return `cure-cite-check: ${res.stale.length} of ${res.total} citation(s) stale: ${issues}${more}`
}

/** Appends to a bounded list, keeping the newest `cap` entries. */
export function capped<T>(list: readonly T[], add: readonly T[], cap = 200): T[] {
  return [...list, ...add].slice(-cap)
}

const ABS_PATH = /(?:^|[\s'"=(])(\/(?:[\w.\-@+]+\/?)+)/g

/**
 * Absolute paths a shell command names (`cd /x`, `git -C /x`, `cat /x/y.ts`), so a
 * repository the session reached through Bash counts as touched. Newest last, at most 20.
 */
export function pathsInCommand(command: string): string[] {
  const out: string[] = []
  for (const m of command.matchAll(ABS_PATH)) {
    const p = m[1].replace(/\/+$/, '')
    if (p.split('/').length > 3 && !out.includes(p)) out.push(p)
  }
  return out.slice(-20)
}
