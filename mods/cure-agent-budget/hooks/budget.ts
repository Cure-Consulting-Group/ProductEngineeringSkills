/**
 * Pure functions for subagent concurrency caps and cost-efficient model routing.
 */

export const DEFAULT_MAX_CONCURRENT = 4

const RESEARCH_ROLE_WORDS = [
  'research',
  'researcher',
  'explore',
  'explorer',
  'lookup',
  'audit',
  'auditor',
  'inspector',
  'survey',
]

export function isResearchTask(role?: string, prompt?: string): boolean {
  const r = (role || '').toLowerCase()
  if (RESEARCH_ROLE_WORDS.some(word => r.includes(word))) return true

  const p = (prompt || '').trim().toLowerCase()
  if (
    p.startsWith('search ') ||
    p.startsWith('find ') ||
    p.startsWith('read ') ||
    p.startsWith('lookup ') ||
    p.startsWith('list ')
  ) {
    return true
  }

  return false
}

export type RoutingDecision = {
  shouldRoute: boolean
  newModel?: string
  reason?: string
}

export function evaluateModelRouting(params: {
  role?: string
  prompt?: string
  currentModel?: string
}): RoutingDecision {
  const p = (params.prompt || '').toLowerCase()
  // Explicit user override in prompt
  if (p.includes('use opus') || p.includes('require opus') || p.includes('opus only')) {
    return { shouldRoute: false }
  }

  const model = (params.currentModel || '').toLowerCase()
  const isOpus = model.includes('opus')

  if (isResearchTask(params.role, params.prompt) && (isOpus || !params.currentModel)) {
    return {
      shouldRoute: true,
      newModel: 'claude-3-5-sonnet',
      reason: 'Down-routed read-only research subagent from Opus to Sonnet for cost efficiency.',
    }
  }

  return { shouldRoute: false }
}

export type BudgetStats = {
  activeCount: number
  maxLimit: number
  cumulativeSpawned: number
  downRoutedCount: number
}

export function formatBudgetReport(stats: BudgetStats): string {
  const lines = [
    `cure-agent-budget: ${stats.activeCount}/${stats.maxLimit} active subagents · ${stats.cumulativeSpawned} total spawned`,
    `  Model optimizations: ${stats.downRoutedCount} subagent(s) routed to Sonnet (saving ~80% per token)`,
  ]

  if (stats.activeCount >= stats.maxLimit) {
    lines.push(`  ⚠️  Concurrency cap reached (${stats.activeCount}/${stats.maxLimit}). New spawns will be queued or blocked.`)
  }

  return lines.join('\n')
}
