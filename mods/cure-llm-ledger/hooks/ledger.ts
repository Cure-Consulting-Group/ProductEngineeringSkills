/**
 * Pure functions for calculating LLM token costs and formatting ledger records.
 */

export type ModelPricing = {
  inputPerM: number
  cacheWritePerM: number
  cacheReadPerM: number
  outputPerM: number
}

export const PRICING_TABLE: Record<string, ModelPricing> = {
  opus: {
    inputPerM: 15.0,
    cacheWritePerM: 18.75,
    cacheReadPerM: 1.5,
    outputPerM: 75.0,
  },
  sonnet: {
    inputPerM: 3.0,
    cacheWritePerM: 3.75,
    cacheReadPerM: 0.3,
    outputPerM: 15.0,
  },
  haiku: {
    inputPerM: 0.8,
    cacheWritePerM: 1.0,
    cacheReadPerM: 0.08,
    outputPerM: 4.0,
  },
}

export function resolvePricing(modelName?: string): ModelPricing {
  const model = (modelName || '').toLowerCase()
  if (model.includes('opus')) return PRICING_TABLE.opus
  if (model.includes('haiku')) return PRICING_TABLE.haiku
  return PRICING_TABLE.sonnet
}

export type UsageCounts = {
  inputTokens: number
  cacheWriteTokens: number
  cacheReadTokens: number
  outputTokens: number
}

export function calculateCost(model: string, usage: UsageCounts): number {
  const pricing = resolvePricing(model)
  const cost =
    (usage.inputTokens / 1_000_000) * pricing.inputPerM +
    (usage.cacheWriteTokens / 1_000_000) * pricing.cacheWritePerM +
    (usage.cacheReadTokens / 1_000_000) * pricing.cacheReadPerM +
    (usage.outputTokens / 1_000_000) * pricing.outputPerM

  return Math.round(cost * 10_000) / 10_000
}

export type LedgerEntry = {
  timestamp: string
  repo: string
  branch: string
  model: string
  input_tokens: number
  cache_write_tokens: number
  cache_read_tokens: number
  output_tokens: number
  cost_usd: number
}

export function createLedgerEntry(params: {
  timestamp: string
  repo: string
  branch: string
  model: string
  usage: UsageCounts
}): LedgerEntry {
  const cost_usd = calculateCost(params.model, params.usage)
  return {
    timestamp: params.timestamp,
    repo: params.repo,
    branch: params.branch,
    model: params.model,
    input_tokens: params.usage.inputTokens,
    cache_write_tokens: params.usage.cacheWriteTokens,
    cache_read_tokens: params.usage.cacheReadTokens,
    output_tokens: params.usage.outputTokens,
    cost_usd,
  }
}

export type SessionTotals = {
  totalCostUsd: number
  totalInput: number
  totalCacheWrite: number
  totalCacheRead: number
  totalOutput: number
  byModel: Record<string, { turns: number; costUsd: number; tokens: number }>
}

export function formatLedgerSummary(totals: SessionTotals): string {
  if (totals.totalCostUsd === 0 && totals.totalInput === 0 && totals.totalOutput === 0) {
    return 'cure-llm-ledger: No model usage recorded in this session yet.'
  }

  const lines = [
    `cure-llm-ledger: Session Spend $${totals.totalCostUsd.toFixed(4)}`,
    `  Tokens: ${totals.totalInput.toLocaleString()} in · ${totals.totalCacheRead.toLocaleString()} cache read · ${totals.totalCacheWrite.toLocaleString()} cache write · ${totals.totalOutput.toLocaleString()} out`,
  ]

  const models = Object.entries(totals.byModel)
  if (models.length > 0) {
    lines.push('  By model:')
    for (const [model, stats] of models) {
      lines.push(
        `    • ${model}: $${stats.costUsd.toFixed(4)} (${stats.turns} turns, ${stats.tokens.toLocaleString()} tokens)`,
      )
    }
  }

  return lines.join('\n')
}
