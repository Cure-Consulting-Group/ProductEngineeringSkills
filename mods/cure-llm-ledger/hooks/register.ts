import type { On } from 'claude-code'

import {
  calculateCost,
  createLedgerEntry,
  formatLedgerSummary,
  type SessionTotals,
  type UsageCounts,
} from './ledger'

const LEDGER_STATE_KEY = 'cure-llm-ledger-totals'

export function register(on: On) {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'ledger',
      description: 'Show LLM token usage and estimated dollar cost breakdown for this session',
    })
    return next(e)
  })

  on('command.run', { command: 'ledger' }, async $ => {
    const totals = ((await $.store.get(LEDGER_STATE_KEY)) as SessionTotals | undefined) ?? {
      totalCostUsd: 0,
      totalInput: 0,
      totalCacheWrite: 0,
      totalCacheRead: 0,
      totalOutput: 0,
      byModel: {},
    }
    return { text: formatLedgerSummary(totals) }
  })

  on('turn.step', async function* ($, e, next) {
    const result = yield* next(e)
    const usage = result?.usage

    if (usage) {
      const counts: UsageCounts = {
        inputTokens: Number(usage.input_tokens || 0),
        cacheWriteTokens: Number(usage.cache_creation_input_tokens || 0),
        cacheReadTokens: Number(usage.cache_read_input_tokens || 0),
        outputTokens: Number(usage.output_tokens || 0),
      }

      const model = String(result.model || e.model || 'claude-3-5-sonnet')
      const turnCost = calculateCost(model, counts)

      // Update store
      const totals = ((await $.store.get(LEDGER_STATE_KEY)) as SessionTotals | undefined) ?? {
        totalCostUsd: 0,
        totalInput: 0,
        totalCacheWrite: 0,
        totalCacheRead: 0,
        totalOutput: 0,
        byModel: {},
      }

      totals.totalCostUsd = Math.round((totals.totalCostUsd + turnCost) * 10_000) / 10_000
      totals.totalInput += counts.inputTokens
      totals.totalCacheWrite += counts.cacheWriteTokens
      totals.totalCacheRead += counts.cacheReadTokens
      totals.totalOutput += counts.outputTokens

      const modelStats = totals.byModel[model] ?? { turns: 0, costUsd: 0, tokens: 0 }
      modelStats.turns += 1
      modelStats.costUsd = Math.round((modelStats.costUsd + turnCost) * 10_000) / 10_000
      modelStats.tokens += counts.inputTokens + counts.cacheWriteTokens + counts.cacheReadTokens + counts.outputTokens
      totals.byModel[model] = modelStats

      await $.store.set(LEDGER_STATE_KEY, totals)
    }

    return result
  })
}
