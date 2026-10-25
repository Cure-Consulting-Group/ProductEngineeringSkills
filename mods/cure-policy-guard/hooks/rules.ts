/**
 * The house rules the guard enforces, as pure functions of one file write.
 *
 * Each rule comes from a decision already written down in a Cure repo; the
 * `source` says where, so a refusal can be traced to the rule and argued with.
 * Rules look only at text a write ADDS, so an edit that leaves an existing
 * violation alone is not blocked here (the repo's own CI owns old debt).
 *
 * The repo table and the shared patterns live once, in mods/shared/rules.ts
 * (vendored here as ./shared/rules.ts).
 */

import {
  AI_VENDOR_PACKAGES,
  CONSUMER_GEMINI,
  SECRET_PATTERNS,
  protectedRepo,
  vendorHostIn,
} from './shared/rules'

export { PROTECTED_REPOS } from './shared/rules'

export type Write = {
  /** Absolute path of the file being written. */
  path: string
  /** Basename of the git repository root holding the file, or '' outside one. */
  repo: string
  /** The text this write introduces (whole file for Write, new_string for Edit). */
  added: string
  /** Dependency names in the nearest package.json, if one was found. */
  deps: readonly string[]
}

export type Violation = {
  rule: string
  reason: string
  source: string
}

const isEnvFile = (path: string) => /(^|\/)\.env(\.[^/]*)?$/.test(path)

/** Org policy since 2026-08-08: no `schedule:` trigger in any workflow. */
export function noCron(w: Write): Violation | undefined {
  if (!/(^|\/)\.github\/workflows\/[^/]+\.ya?ml$/.test(w.path)) return undefined
  if (!/^\s*schedule\s*:/m.test(w.added)) return undefined
  return {
    rule: 'no-cron',
    reason:
      'adds a `schedule:` trigger to a workflow. Org policy since 2026-08-08 bans cron in GitHub Actions; use push, PR, dispatch or an age gate on a push trigger instead.',
    source: 'DistrictZero/CLAUDE.md "No cron. Org policy since 2026-08-08"; github_policy scanner',
  }
}

/** A PHI repo (Level5) uses Gemini only through Vertex AI under the GCP BAA. */
export function level5VertexOnly(w: Write): Violation | undefined {
  const repo = protectedRepo(w.repo)
  if (repo?.data !== 'phi') return undefined
  const hit = CONSUMER_GEMINI.exec(w.added)
  if (!hit) return undefined
  return {
    rule: 'level5-vertex-only',
    reason: `introduces \`${hit[0]}\`, the consumer Gemini API path. ${w.repo} processes PHI, and only Vertex AI is covered by the Google Cloud BAA.`,
    source: repo.source,
  }
}

const importedPackages = (text: string): string[] => {
  const found = new Set<string>()
  const re = /(?:from\s+|require\(\s*|import\(\s*|import\s+)['"]([^'"]+)['"]/g
  for (const m of text.matchAll(re)) {
    const spec = m[1]
    const name = spec.startsWith('@') ? spec.split('/').slice(0, 2).join('/') : spec.split('/')[0]
    found.add(name)
  }
  return [...found]
}

/** A new AI vendor in a minors' repo needs a decision, not a default. */
export function minorsNewAiVendor(w: Write): Violation | undefined {
  if (protectedRepo(w.repo)?.data !== 'minors') return undefined
  const added = importedPackages(w.added).filter(
    p => AI_VENDOR_PACKAGES.includes(p) && !w.deps.includes(p),
  )
  if (added.length === 0) return undefined
  return {
    rule: 'minors-new-ai-vendor',
    reason: `imports ${added.map(p => `\`${p}\``).join(', ')}, an AI vendor this repo does not already depend on. ${w.repo} handles data about minors or students; a new processor needs a data-processing decision first (several vendors, TypeSafe among them, exclude under-18 data by policy).`,
    source: 'Jev / AI-vendor review 2026-10-04; SPEDTECH privacy page "de-identified prompts only"',
  }
}

/** A credential literal in a tracked file. `.env*` files are where keys belong. */
export function hardcodedSecret(w: Write): Violation | undefined {
  if (isEnvFile(w.path)) return undefined
  for (const [kind, re] of SECRET_PATTERNS) {
    if (re.test(w.added)) {
      return {
        rule: 'hardcoded-secret',
        reason: `writes what looks like a ${kind} into ${w.path.split('/').pop()}. Keep credentials in Secret Manager, a GitHub secret or a gitignored .env, and read them at run time.`,
        source: 'TIR scripts/data-fixes/*.js shipped a hard-coded Gemini key (found 2026-10-04)',
      }
    }
  }
  return undefined
}

export const RULES = [noCron, level5VertexOnly, minorsNewAiVendor, hardcodedSecret] as const

// ── Bash and WebFetch: data leaving a protected repo (was cure-egress-guard) ──

/**
 * A command or URL that reaches a consumer AI API from a PHI or minors' repo.
 * The host is matched as a whole name, not a substring.
 */
export function aiEgress(text: string, repo: string): Violation | undefined {
  const entry = protectedRepo(repo)
  if (!entry?.data) return undefined
  const host = vendorHostIn(text)
  if (!host) return undefined
  const why = entry.data === 'phi'
    ? `${repo} processes PHI; only Google Cloud Vertex AI under the GCP BAA may receive it.`
    : `${repo} processes data about minors or students; it must not go to a consumer AI endpoint.`
  return { rule: 'ai-egress', reason: `sends a request to \`${host}\`. ${why}`, source: entry.source }
}

/**
 * The directory a shell command runs in when it says so: a leading `cd <dir>`
 * or `git -C <dir>`; undefined when it names none (the caller uses the shell's).
 */
export function commandDir(command: string): string | undefined {
  const cd = /^\s*cd\s+("([^"]+)"|'([^']+)'|(\S+))\s*(?:&&|;|$)/.exec(command)
  if (cd) return cd[2] ?? cd[3] ?? cd[4]
  const c = /\bgit\s+-C\s+("([^"]+)"|'([^']+)'|(\S+))/.exec(command)
  return c ? c[2] ?? c[3] ?? c[4] : undefined
}

// ── File writes: multi-machine state ownership (was cure-claim-guard) ──────

/** The two-letter state a build script path is about (`scripts/build-ny-...`), if any. */
export function stateFromPath(path: string): string | undefined {
  const m = /(?:^|\/)scripts\/(?:build|lib|data)[-_/]([a-zA-Z]{2})(?:[-_./]|$)/.exec(path || '')
  return m ? m[1].toUpperCase() : undefined
}

/** `| NY | machine-name | ... |` rows of .agents/state-targets.md, as state → owner. */
export function parseStateTargets(content: string): Map<string, string> {
  const claims = new Map<string, string>()
  for (const line of (content || '').split('\n')) {
    const t = line.trim()
    if (!t.startsWith('|')) continue
    const cells = t.split('|').map(c => c.trim()).filter(c => c.length > 0)
    if (cells.length < 2) continue
    const state = cells[0].toUpperCase()
    if (/^[A-Z]{2}$/.test(state)) claims.set(state, cells[1])
  }
  return claims
}

/** A host name as a claim names it: lower case, without a domain (`Mac-Mini.local` → `mac-mini`). */
export function shortHost(name: string): string {
  return (name || '').trim().toLowerCase().split('.')[0]
}

/** A write to a state another machine owns. Exact host match, never a substring either way. */
export function stateClaim(path: string, repo: string, host: string, claims: ReadonlyMap<string, string>): Violation | undefined {
  const entry = protectedRepo(repo)
  if (!entry?.stateClaims) return undefined
  const state = stateFromPath(path)
  if (!state) return undefined
  const owner = claims.get(state)
  if (!owner || shortHost(owner) === shortHost(host)) return undefined
  return {
    rule: 'state-claim',
    reason: `writes ${state} build files, but .agents/state-targets.md gives ${state} to \`${owner}\` and this machine is \`${shortHost(host)}\`. Never build a row another machine owns.`,
    source: entry.source,
  }
}

/** Every rule the write breaks, in RULES order. */
export function check(w: Write): Violation[] {
  return RULES.map(rule => rule(w)).filter((v): v is Violation => v !== undefined)
}

/** The text a built-in file tool call adds; '' for a call this guard does not read. */
export function addedText(e: Record<string, unknown>): string {
  const str = (v: unknown) => (typeof v === 'string' ? v : '')
  switch (e.tool) {
    case 'Write':
      return str(e.content)
    case 'Edit':
      return str(e.new_string)
    case 'MultiEdit':
      return Array.isArray(e.edits)
        ? e.edits.map(x => str((x as Record<string, unknown>)?.new_string)).join('\n')
        : ''
    case 'NotebookEdit':
      return str(e.new_source)
    default:
      return ''
  }
}

/** The path a built-in file tool call writes; '' when it names none. */
export function targetPath(e: Record<string, unknown>): string {
  const p = e.file_path ?? e.notebook_path
  return typeof p === 'string' ? p : ''
}

/** Dependency names from a package.json's text; [] when it does not parse. */
export function dependencyNames(packageJson: string | undefined): string[] {
  if (!packageJson) return []
  try {
    const pkg = JSON.parse(packageJson) as Record<string, Record<string, string> | undefined>
    return [
      ...Object.keys(pkg.dependencies ?? {}),
      ...Object.keys(pkg.devDependencies ?? {}),
      ...Object.keys(pkg.optionalDependencies ?? {}),
      ...Object.keys(pkg.peerDependencies ?? {}),
    ]
  } catch {
    return []
  }
}

/** The directories above a path, nearest first, ending at '/'. */
export function parentDirs(path: string): string[] {
  const out: string[] = []
  let dir = path.replace(/\/+$/, '')
  while (dir.includes('/')) {
    dir = dir.slice(0, dir.lastIndexOf('/'))
    out.push(dir === '' ? '/' : dir)
    if (dir === '') break
  }
  return out
}
