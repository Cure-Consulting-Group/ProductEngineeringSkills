/**
 * Pure functions for inspecting outbound network commands and detecting unauthorized AI vendor egress.
 */

export const PROTECTED_REPOS: ReadonlySet<string> = new Set([
  'Level5',
  'initiated-recruiting',
  'initiated-recruiting-nil',
  'SPEDTECH',
  'LearnLift',
  'iep-and-thrive',
])

export const PROHIBITED_HOSTS: readonly string[] = [
  'api.openai.com',
  'generativelanguage.googleapis.com',
  'api.anthropic.com',
  'api.groq.com',
  'api.cohere.ai',
  'api.together.xyz',
  'api.perplexity.ai',
]

export type EgressVerdict = {
  violated: boolean
  host?: string
  reason?: string
}

export function isProtectedRepo(repoName?: string): boolean {
  if (!repoName) return false
  const clean = repoName.trim()
  return PROTECTED_REPOS.has(clean)
}

export function detectEgressViolation(
  commandOrUrl: string,
  repoName?: string,
): EgressVerdict {
  if (!isProtectedRepo(repoName)) {
    return { violated: false }
  }

  const text = (commandOrUrl || '').toLowerCase()

  for (const host of PROHIBITED_HOSTS) {
    if (text.includes(host)) {
      const isPhi = repoName === 'Level5'
      const context = isPhi
        ? 'Level5 processes PHI; only Google Cloud Vertex AI under the GCP BAA is permitted.'
        : `${repoName} processes minors' or student data; direct streaming to unapproved consumer AI endpoints is prohibited.`

      return {
        violated: true,
        host,
        reason: `Outbound request to \`${host}\` detected in protected repo \`${repoName}\`. ${context}`,
      }
    }
  }

  return { violated: false }
}

export function formatEgressReport(repoName: string): string {
  const protectedStatus = isProtectedRepo(repoName)
    ? `PROTECTED (PHI/Minors Data House Rules Active)`
    : `Standard (No special AI egress restrictions)`

  const lines = [
    `cure-egress-guard status for repo '${repoName || 'unknown'}': ${protectedStatus}`,
    `Protected repos: ${[...PROTECTED_REPOS].join(', ')}`,
    `Prohibited runtime AI hosts: ${PROHIBITED_HOSTS.join(', ')}`,
  ]

  return lines.join('\n')
}
