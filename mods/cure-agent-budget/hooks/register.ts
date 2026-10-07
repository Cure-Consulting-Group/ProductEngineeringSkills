import type { On } from 'claude-code'

import {
  DEFAULT_MAX_CONCURRENT,
  evaluateModelRouting,
  formatBudgetReport,
  type BudgetStats,
} from './budget'

const BUDGET_STATE_KEY = 'cure-agent-budget-stats'

export function register(on: On) {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'agents-budget',
      description: 'Show active subagent count, concurrency caps, and routing savings for this session',
    })
    return next(e)
  })

  on('command.run', { command: 'agents-budget' }, async $ => {
    const stats = ((await $.store.get(BUDGET_STATE_KEY)) as BudgetStats | undefined) ?? {
      activeCount: 0,
      maxLimit: DEFAULT_MAX_CONCURRENT,
      cumulativeSpawned: 0,
      downRoutedCount: 0,
    }
    return { text: formatBudgetReport(stats) }
  })

  on('tool.call', async ($, e, next) => {
    if (String(e.tool) !== 'Agent') return next(e)

    const stats = ((await $.store.get(BUDGET_STATE_KEY)) as BudgetStats | undefined) ?? {
      activeCount: 0,
      maxLimit: DEFAULT_MAX_CONCURRENT,
      cumulativeSpawned: 0,
      downRoutedCount: 0,
    }

    if (stats.activeCount >= stats.maxLimit) {
      return {
        deny: `cure-agent-budget: Maximum concurrent subagents (${stats.maxLimit}) reached. Wait for existing subagents to complete.`,
      }
    }

    stats.activeCount += 1
    stats.cumulativeSpawned += 1

    const role = typeof e.description === 'string' ? e.description : typeof e.role === 'string' ? e.role : ''
    const prompt = typeof e.prompt === 'string' ? e.prompt : ''
    const model = typeof e.model === 'string' ? e.model : ''

    const decision = evaluateModelRouting({ role, prompt, currentModel: model })
    let eventToPass = e
    if (decision.shouldRoute && decision.newModel) {
      stats.downRoutedCount += 1
      eventToPass = { ...e, model: decision.newModel }
      $.ui.toast(`cure-agent-budget: Routed subagent '${role || 'research'}' to Sonnet`)
    }

    await $.store.set(BUDGET_STATE_KEY, stats)

    try {
      const answer = await next(eventToPass)
      return answer
    } finally {
      const current = ((await $.store.get(BUDGET_STATE_KEY)) as BudgetStats | undefined) ?? stats
      if (current.activeCount > 0) {
        current.activeCount -= 1
        await $.store.set(BUDGET_STATE_KEY, current)
      }
    }
  })
}
