/**
 * Pure functions for analyzing git diff file paths and estimating GitHub Actions runner costs.
 */

export type CiPreview = {
  jobs: string[]
  estimatedMinutes: number
  estimatedCostUsd: number
  warning?: string
}

const LINUX_RATE_PER_MIN = 0.008 // GitHub Actions standard 2-core Linux runner
const MACOS_RATE_PER_MIN = 0.016 // GitHub Actions standard macOS runner

const DOC_PATTERN = /\.(?:md|txt|svg|png|jpg|jpeg|gif)$|^(?:docs|design|\.agents)\//i
const CODE_PATTERN = /\.(?:ts|tsx|js|jsx|py|kt|swift|go|rs|sh|json|ya?ml)$/i
const IOS_PATTERN = /(?:^|\/)(?:ios|macos)\/|\.(?:swift|pbxproj)$|^Podfile|^Cartfile/i

export function classifyChanges(paths: string[]): CiPreview {
  const cleanPaths = paths.map(p => p.trim()).filter(p => p.length > 0)
  if (cleanPaths.length === 0) {
    return {
      jobs: ['No changes detected'],
      estimatedMinutes: 0,
      estimatedCostUsd: 0,
    }
  }

  const isDoc = (p: string) => DOC_PATTERN.test(p)
  const isCode = (p: string) => CODE_PATTERN.test(p)
  const isIos = (p: string) => IOS_PATTERN.test(p)

  const docCount = cleanPaths.filter(isDoc).length
  const codeCount = cleanPaths.filter(isCode).length
  const iosCount = cleanPaths.filter(isIos).length

  // Pure documentation change -> skips execution
  if (docCount === cleanPaths.length) {
    return {
      jobs: ['Docs Quick-Lint / Skip'],
      estimatedMinutes: 1,
      estimatedCostUsd: 0.0,
    }
  }

  const jobs: string[] = []
  let totalMinutes = 0
  let totalCost = 0.0
  let warning: string | undefined

  if (docCount > 0 && codeCount > 0) {
    warning = 'Commit mixes documentation notes with executable code; loses docs-only skip optimization.'
  }

  const nonIosCodeCount = cleanPaths.filter(p => isCode(p) && !isIos(p)).length

  if (iosCount > 0) {
    jobs.push('macOS Runner (iOS Matrix)')
    const mins = 15
    totalMinutes += mins
    totalCost += mins * MACOS_RATE_PER_MIN
  }

  if (nonIosCodeCount > 0) {
    jobs.push('Linux Runner (Test & Validate Matrix)')
    const mins = 15
    totalMinutes += mins
    totalCost += mins * LINUX_RATE_PER_MIN
  }

  return {
    jobs,
    estimatedMinutes: totalMinutes,
    estimatedCostUsd: Math.round(totalCost * 100) / 100,
    warning,
  }
}

export function formatCiPreview(preview: CiPreview): string {
  const lines = [
    `cure-ci-preview: Expected CI jobs: ${preview.jobs.join(' · ')}`,
    `  Estimated time: ~${preview.estimatedMinutes} billed min · Cost: ~$${preview.estimatedCostUsd.toFixed(2)}`,
  ]

  if (preview.warning) {
    lines.push(`  ⚠️  ${preview.warning}`)
  }

  return lines.join('\n')
}
