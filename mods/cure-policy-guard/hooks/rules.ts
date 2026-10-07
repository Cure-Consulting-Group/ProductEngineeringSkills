/**
 * The house rules the guard enforces, as pure functions of one file write.
 *
 * Each rule comes from a decision already written down in a Cure repo; the
 * `source` says where, so a refusal can be traced to the rule and argued with.
 * Rules look only at text a write ADDS, so an edit that leaves an existing
 * violation alone is not blocked here (the repo's own CI owns old debt).
 */

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

const CONSUMER_GEMINI = /@google\/generative-ai\b|generativelanguage\.googleapis\.com|\bGEMINI_API_KEY\b/

/** Level5 handles PHI: Gemini only through Vertex AI under the GCP BAA. */
export function level5VertexOnly(w: Write): Violation | undefined {
  if (w.repo !== 'Level5') return undefined
  const hit = CONSUMER_GEMINI.exec(w.added)
  if (!hit) return undefined
  return {
    rule: 'level5-vertex-only',
    reason: `introduces \`${hit[0]}\`, the consumer Gemini API path. Level5 processes PHI, and only Vertex AI is covered by the Google Cloud BAA.`,
    source: 'Level5/docs/compliance/BAA_INVENTORY.md:33-34, :48',
  }
}

/** Repos whose data is about minors or students (COPPA/FERPA-adjacent). */
export const MINORS_REPOS: ReadonlySet<string> = new Set([
  'initiated-recruiting',
  'initiated-recruiting-nil',
  'SPEDTECH',
  'LearnLift',
  'iep-and-thrive',
])

/** Model-vendor SDKs, as an import names them. */
export const AI_VENDOR_PACKAGES: readonly string[] = [
  'openai',
  '@anthropic-ai/sdk',
  '@google/genai',
  '@google/generative-ai',
  '@google-cloud/vertexai',
  'cohere-ai',
  '@mistralai/mistralai',
  'groq-sdk',
  'together-ai',
  'replicate',
  '@typesafe-ai/sdk',
  'typesafe',
]

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
  if (!MINORS_REPOS.has(w.repo)) return undefined
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

const SECRET_PATTERNS: readonly [string, RegExp][] = [
  ['Google API key', /AIza[0-9A-Za-z_-]{35}/],
  ['Anthropic API key', /sk-ant-[0-9A-Za-z_-]{20,}/],
  ['OpenAI API key', /\bsk-(?:proj-)?[0-9A-Za-z_-]{32,}/],
  ['GitHub token', /\b(?:ghp|gho|ghs|ghu)_[0-9A-Za-z]{36}\b|\bgithub_pat_[0-9A-Za-z_]{40,}/],
  ['Stripe secret key', /\b(?:sk|rk)_live_[0-9A-Za-z]{20,}/],
  ['private key', /-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----/],
  ['service-account key', /"private_key"\s*:\s*"-----BEGIN/],
]

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
