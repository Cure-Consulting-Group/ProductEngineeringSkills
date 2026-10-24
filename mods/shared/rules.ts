/**
 * The one table of Cure's protected repositories and the patterns their rules
 * use. cure-policy-guard enforces it; cure-rules-band displays it.
 *
 * Mods install one folder each, so a mod cannot import across folders: this file
 * is the source, and mods/shared/vendor.py copies it into each consumer's
 * hooks/shared/. Edit it here, then run the script; CI runs it with --check.
 */

export type DataClass = 'phi' | 'minors'

export type ProtectedRepo = {
  /** The main checkout's folder name (a worktree reads as its main repo). */
  repo: string
  /** What the repo's data is, which decides the egress and vendor rules. */
  data?: DataClass
  /** Writes under scripts/ are checked against .agents/state-targets.md ownership. */
  stateClaims?: boolean
  /** What the rules band shows. */
  labels: readonly string[]
  /** Where the rule is written down. */
  source: string
}

export const PROTECTED_REPOS: readonly ProtectedRepo[] = [
  { repo: 'Level5', data: 'phi', labels: ['PHI Data (GCP BAA)', 'Vertex AI Only', 'No Consumer Gemini'], source: 'Level5/docs/compliance/BAA_INVENTORY.md:33-34, :48' },
  { repo: 'initiated-recruiting', data: 'minors', labels: ['Minors Data', 'No New AI Vendors', 'COPPA Bounds'], source: 'AI-vendor review 2026-10-04' },
  { repo: 'initiated-recruiting-nil', data: 'minors', labels: ['Minors Data', 'No New AI Vendors'], source: 'AI-vendor review 2026-10-04' },
  { repo: 'SPEDTECH', data: 'minors', labels: ['Student Records', 'No New AI Vendors', 'FERPA Bounds'], source: 'SPEDTECH privacy page "de-identified prompts only"' },
  { repo: 'LearnLift', data: 'minors', labels: ['Minors Data', 'No New AI Vendors'], source: 'AI-vendor review 2026-10-04' },
  { repo: 'iep-and-thrive', data: 'minors', labels: ['Student Records', 'No New AI Vendors'], source: 'AI-vendor review 2026-10-04' },
  { repo: 'DistrictZero', stateClaims: true, labels: ['No Cron', 'Machine State Claims'], source: 'DistrictZero/CLAUDE.md multi-machine coordination; .agents/state-targets.md' },
]

export function protectedRepo(name: string | undefined): ProtectedRepo | undefined {
  if (!name) return undefined
  return PROTECTED_REPOS.find(r => r.repo === name.trim())
}

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

/** Consumer AI API hosts a protected repo's data must not be sent to from a session. */
export const AI_VENDOR_HOSTS: readonly string[] = [
  'api.openai.com',
  'generativelanguage.googleapis.com',
  'api.anthropic.com',
  'api.groq.com',
  'api.cohere.ai',
  'api.cohere.com',
  'api.together.xyz',
  'api.perplexity.ai',
  'api.mistral.ai',
]

/** The consumer Gemini path, which Level5's BAA does not cover (Vertex AI only). */
export const CONSUMER_GEMINI = /@google\/generative-ai\b|generativelanguage\.googleapis\.com|\bGEMINI_API_KEY\b/

/** Credential literals: [kind, pattern]. */
export const SECRET_PATTERNS: readonly (readonly [string, RegExp])[] = [
  ['Google API key', /AIza[0-9A-Za-z_-]{35}/],
  ['Anthropic API key', /sk-ant-[0-9A-Za-z_-]{20,}/],
  ['OpenAI API key', /\bsk-(?:proj-)?[0-9A-Za-z_-]{32,}/],
  ['GitHub token', /\b(?:ghp|gho|ghs|ghu)_[0-9A-Za-z]{36}\b|\bgithub_pat_[0-9A-Za-z_]{40,}/],
  ['Stripe secret key', /\b(?:sk|rk)_live_[0-9A-Za-z]{20,}/],
  ['private key', /-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----/],
  ['service-account key', /"private_key"\s*:\s*"-----BEGIN/],
]

/**
 * The AI vendor host a command or URL reaches, matched as a whole host name (so
 * `notapi.openai.com.example.org` and a word inside a path do not count).
 */
export function vendorHostIn(text: string): string | undefined {
  const lower = (text || '').toLowerCase()
  for (const host of AI_VENDOR_HOSTS) {
    const escaped = host.replace(/\./g, '\\.')
    if (new RegExp(`(?:^|[^a-z0-9.-])${escaped}(?![a-z0-9-]|\\.[a-z0-9])`).test(lower)) return host
  }
  return undefined
}
