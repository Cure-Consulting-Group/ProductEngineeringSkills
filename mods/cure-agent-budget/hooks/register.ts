import type { $ as Engine, Register } from 'claude-code'

import type { Stats, Tracked } from '../types'
import {
  capFrom,
  denyText,
  evaluateModelRouting,
  formatBudgetReport,
  reconcile,
  routeFrom,
} from './budget'

/** 0.1.0 kept a machine-global count here; it never reset and filled the cap with ghosts. */
const LEGACY_STORE_KEY = 'cure-agent-budget-stats'

const ACTIVE = { plugin: 'cure-agent-budget', key: 'active' } as const
const STATS = { plugin: 'cure-agent-budget', key: 'stats' } as const
const NO_STATS: Stats = { spawned: 0, denied: 0, routed: 0 }

type $ = Engine

async function listed($: $): Promise<Map<string, string> | undefined> {
  try {
    const rows = await $.agent.list()
    return new Map(rows.map(r => [r.id, String(r.status)]))
  } catch {
    return undefined
  }
}

async function active($: $): Promise<Tracked[]> {
  const { value = [] } = await $.state.get(ACTIVE)
  const live = reconcile(value, await listed($))
  if (live.length !== value.length) await $.state.set(ACTIVE, live)
  return live
}

async function bump($: $, field: keyof Stats): Promise<void> {
  const { value = NO_STATS } = await $.state.get(STATS)
  await $.state.set(STATS, { ...value, [field]: value[field] + 1 })
}

export const register: Register = (on, options) => {
  const cap = capFrom(options.maxConcurrent)
  const route = routeFrom(options.routeResearchTo)

  on('session.start', async ($, e, next) => {
    await $.store.delete(LEGACY_STORE_KEY).catch(() => undefined)
    // A new session starts empty; a hot reload keeps the agents the engine still runs.
    const { value = [] } = await $.state.get(ACTIVE)
    const rows = await listed($)
    await $.state.set(ACTIVE, rows ? reconcile(value, rows) : [])
    await $.command.register({
      name: 'agents-budget',
      description: 'Show running subagents, the concurrency cap and routing for this session',
    })
    return next(e)
  })

  on('session.end', async ($, e, next) => {
    await $.state.set(ACTIVE, [])
    return next(e)
  })

  on('command.run', { command: 'agents-budget' }, async $ => {
    const { value: stats = NO_STATS } = await $.state.get(STATS)
    return { text: formatBudgetReport({ active: await active($), cap, route, ...stats }) }
  })

  on('agent.spawn', async ($, e, next) => {
    // Workflow scripts and teammates govern their own fan-out; a resume reuses its slot.
    if (e.workflow || e.isTeammate) return next(e)

    const running = await active($)
    if (!e.resume && cap > 0 && running.length >= cap) {
      await bump($, 'denied')
      return { deny: denyText(running.length, cap) }
    }

    const decision = evaluateModelRouting({
      route,
      description: e.description,
      prompt: e.prompt,
      model: e.model,
      parentModel: e.parentModel,
      isFork: e.fork,
    })
    const answer = await next(decision.model ? { ...e, model: decision.model } : e)
    if (answer.deny !== undefined || !answer.agentId) return answer

    const id = answer.agentId
    const now = await $.clock.now()
    const { value = [] } = await $.state.get(ACTIVE)
    await $.state.set(ACTIVE, [...value.filter(t => t.id !== id), { id, description: e.description, startedAt: now }].slice(-200))
    if (!e.resume) await bump($, 'spawned')
    if (decision.model) {
      await bump($, 'routed')
      $.ui.toast(`cure-agent-budget: '${e.description}' → ${decision.model}`)
    }
    return answer
  })

  on('turn.complete', async ($, e, next) => {
    if (e.agentId !== undefined) {
      const { value = [] } = await $.state.get(ACTIVE)
      if (value.some(t => t.id === e.agentId)) await $.state.set(ACTIVE, value.filter(t => t.id !== e.agentId))
    }
    return next(e)
  })
}
