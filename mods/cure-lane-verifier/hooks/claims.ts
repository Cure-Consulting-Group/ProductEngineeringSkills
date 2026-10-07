/**
 * What a subagent or lane report claims about where its work landed, and the
 * verdict once git has been asked. Pure: no I/O here, so it is all testable.
 *
 * The defect this exists for (memory: verify-lane-output-by-mutation): a lane
 * reported `complete` with 42 passing tests while its branch diff was empty.
 * A report is a claim; the branch is the evidence.
 */

export type Claims = {
  /** Absolute paths the report names that may be worktrees or repos. */
  paths: string[]
  /** Branch names the report names (`lane/<task>`, or "branch `x`"). */
  branches: string[]
  /** The report says the work is finished. */
  claimsDone: boolean
}

const MAX_TARGETS = 5

/** Paths, branches and a completion claim, read off a report's text. */
export function extractClaims(text: string): Claims {
  const paths = new Set<string>()
  for (const m of text.matchAll(/(?:^|[\s'"`(\[])(\/(?:Users|private|tmp|home|var|opt|workspace|srv)\/[^\s'"`)\]]+)/g)) {
    const p = m[1].replace(/[.,:;]+$/, '').replace(/\/+$/, '')
    // A file path's directory is what git can answer for.
    paths.add(/\.[A-Za-z0-9]{1,6}$/.test(p.split('/').pop() ?? '') ? p.slice(0, p.lastIndexOf('/')) : p)
  }
  const branches = new Set<string>()
  for (const m of text.matchAll(/\b(lane\/[A-Za-z0-9._\/-]+[A-Za-z0-9])/g)) branches.add(m[1])
  for (const m of text.matchAll(/\bbranch(?:es)?\s*[:=]?\s*`([A-Za-z0-9._\/-]+)`/gi)) branches.add(m[1])
  for (const m of text.matchAll(/\bon branch\s+([A-Za-z0-9._\/-]*[A-Za-z0-9])/gi)) branches.add(m[1])
  for (const b of ['main', 'master', 'HEAD']) branches.delete(b)

  const claimsDone =
    /\b(?:status\s*[:=]\s*)?(?:complete|completed|done|finished|implemented|fixed|shipped|merged-ready)\b/i.test(text) ||
    /\ball (?:\d+ )?tests? pass(?:ed|es)?\b/i.test(text) ||
    /\bGAPS:\s*none\b/i.test(text)

  return {
    paths: [...paths].slice(0, MAX_TARGETS),
    branches: [...branches].slice(0, MAX_TARGETS),
    claimsDone,
  }
}

export type Evidence = {
  /** What was checked: a worktree path, or a branch name. */
  target: string
  /** A named branch, or a path's checkout (whose dirt may be unrelated work). */
  kind?: 'branch' | 'path'
  /** Commits on the target that its base does not have. */
  ahead: number
  /** `git diff --shortstat base...target`, '' when there is no diff. */
  shortstat: string
  /** Uncommitted files in a worktree (0 for a branch-only target). */
  dirty: number
  /** The base compared against (`origin/main`). */
  base: string
  /** Set when git could not answer for this target. */
  error?: string
}

const isEmpty = (e: Evidence) => e.ahead === 0 && e.dirty === 0 && e.shortstat === ''

/**
 * Whether the evidence contradicts a completion claim.
 *
 * A branch the report names is the strongest claim: if any named branch git
 * knows is empty, the claim is contradicted, whatever else the report names
 * (a path to the main checkout can be dirty with someone else's work). With
 * no branch named, every checked path must be empty.
 */
export function isEmptyCompletion(claimsDone: boolean, evidence: readonly Evidence[]): boolean {
  if (!claimsDone) return false
  const answered = evidence.filter(e => !e.error)
  const branches = answered.filter(e => e.kind === 'branch')
  if (branches.length > 0) return branches.some(isEmpty)
  return answered.length > 0 && answered.every(isEmpty)
}

/** The verification note: one line per target, and a loud first line on an empty completion. */
export function formatVerdict(claims: Claims, evidence: readonly Evidence[]): string {
  if (evidence.length === 0) return ''
  const lines = evidence.map(e =>
    e.error
      ? `- ${e.target}: could not verify (${e.error})`
      : `- ${e.target}: ${e.ahead} commit(s) ahead of ${e.base}; ${e.shortstat || 'no committed diff'}${e.dirty ? `; ${e.dirty} uncommitted file(s)` : ''}`,
  )
  const head = isEmptyCompletion(claims.claimsDone, evidence)
    ? 'cure-lane-verifier: EMPTY COMPLETION. The report claims the work is done, but git shows no commits and no changes on what it names. Do not accept it; inspect the worktree before anything else.'
    : 'cure-lane-verifier: git evidence for what this report names (read this, not the report, for what landed):'
  return [head, ...lines].join('\n')
}

/** Uncommitted file count from `git status --porcelain` output. */
export function countDirty(porcelain: string): number {
  return porcelain.split('\n').filter(l => l.trim() !== '').length
}
