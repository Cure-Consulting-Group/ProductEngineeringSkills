/**
 * Pure functions for parsing and verifying code line citations.
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

const CITE_REGEX = /(?:`|\[[^\]]+\]\()?(?:file:\/\/)?([a-zA-Z0-9_.\-\/]+\.[a-zA-Z0-9]+)(?:#L|:)(\d+)(?:(?:-L|-)(\d+))?(?:\)|`)?/g

export function extractCitations(text: string): Citation[] {
  if (!text || typeof text !== 'string') return []

  const citations: Citation[] = []
  const seen = new Set<string>()

  for (const match of text.matchAll(CITE_REGEX)) {
    const index = match.index ?? 0
    const prefix = text.slice(Math.max(0, index - 10), index)
    if (prefix.includes('://') || prefix.includes('http')) continue

    const raw = match[0]
    const path = match[1]
    const line = parseInt(match[2], 10)
    const endLine = match[3] ? parseInt(match[3], 10) : undefined

    // Skip urls and false positives
    if (path.startsWith('http://') || path.startsWith('https://')) continue
    // Skip if path has no extension
    if (!path.includes('.')) continue

    const key = `${path}:${line}${endLine ? `-${endLine}` : ''}`
    if (!seen.has(key)) {
      seen.add(key)
      citations.push({ raw, path, line, endLine })
    }
  }

  return citations
}

export function verifyCitation(
  citation: Citation,
  exists: boolean,
  lineCount: number,
): StaleCitation | undefined {
  if (!exists) {
    return {
      citation,
      reason: `file does not exist`,
    }
  }

  if (citation.line <= 0) {
    return {
      citation,
      reason: `line number must be positive (got ${citation.line})`,
    }
  }

  if (citation.line > lineCount) {
    return {
      citation,
      reason: `line ${citation.line} exceeds file length (${lineCount} lines)`,
    }
  }

  if (citation.endLine && citation.endLine > lineCount) {
    return {
      citation,
      reason: `end line ${citation.endLine} exceeds file length (${lineCount} lines)`,
    }
  }

  return undefined
}

export type VerificationResult = {
  total: number
  valid: number
  stale: StaleCitation[]
}

export function formatVerificationNotice(res: VerificationResult): string {
  if (res.total === 0) return ''

  if (res.stale.length === 0) {
    return `[CURE-CITE-CHECK: ${res.total} citation(s) verified ✓]`
  }

  const issues = res.stale
    .map(s => `${s.citation.path}:${s.citation.line} (${s.reason})`)
    .join(', ')

  return `[CURE-CITE-CHECK: ${res.total} checked, ${res.stale.length} stale: ${issues}]`
}
