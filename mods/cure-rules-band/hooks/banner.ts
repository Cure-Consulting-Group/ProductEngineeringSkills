/**
 * Pure functions for resolving and formatting repository house rules banner text.
 */

export const DEFAULT_REPO_RULES: Record<string, string[]> = {
  Level5: ['PHI Data (GCP BAA)', 'Vertex AI Only', 'No Consumer Gemini'],
  'initiated-recruiting': ['Minors Data', 'No New AI Vendors', 'COPPA Bounds'],
  'initiated-recruiting-nil': ['Minors Data', 'No New AI Vendors'],
  SPEDTECH: ['Student Records', 'No New AI Vendors', 'FERPA Bounds'],
  LearnLift: ['Minors Data', 'No New AI Vendors'],
  DistrictZero: ['No Cron', 'Machine State Claims'],
}

export function parseRulesJson(jsonText: string): string[] | undefined {
  if (!jsonText || typeof jsonText !== 'string') return undefined
  try {
    const parsed = JSON.parse(jsonText)
    if (Array.isArray(parsed.rules)) {
      return parsed.rules.map(String).filter((s: string) => s.length > 0)
    }
    if (Array.isArray(parsed)) {
      return parsed.map(String).filter((s: string) => s.length > 0)
    }
  } catch {
    // Malformed JSON fallback
  }
  return undefined
}

/** The repo's rules: its `.cure/rules.json` first, then the built-in table; null for a repo with neither. */
export function resolveRepoRules(
  repoName?: string,
  configFileContent?: string,
): { repo: string; rules: string[] } | null {
  const repo = (repoName || '').trim()
  if (configFileContent) {
    const fromConfig = parseRulesJson(configFileContent)
    if (fromConfig && fromConfig.length > 0) return { repo: repo || 'this repo', rules: fromConfig }
  }
  const defaultForRepo = DEFAULT_REPO_RULES[repo]
  if (defaultForRepo && defaultForRepo.length > 0) return { repo, rules: defaultForRepo }
  return null
}

/** The main checkout's name from `git rev-parse --git-common-dir` (absolute), so a worktree reads as its repo. */
export function repoNameFromCommonDir(commonDir: string): string {
  const dir = commonDir.trim().replace(/\/$/, '')
  const repoDir = dir.endsWith('/.git') ? dir.slice(0, -5) : dir
  return repoDir.split('/').pop() ?? ''
}

export function formatBannerText(repo: string, rules: string[]): string {
  if (rules.length === 0) return `rules ● ${repo}`
  return `rules ● ${repo} · ${rules.join(' · ')}`
}

export function formatRulesReport(repo: string, rules: string[]): string {
  const lines = [
    `cure-rules-band: Active house rules for '${repo}':`,
    ...rules.map(r => `  • ${r}`),
  ]
  return lines.join('\n')
}
