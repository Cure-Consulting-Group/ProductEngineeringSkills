/**
 * Pure functions for the subagent concurrency cap and the opt-in research routing.
 *
 * Live counts are never kept here or in `$.store` (shared by every session on the
 * machine): the hooks module tracks each agent by id in session-scoped `$.state`.
 */

import type { Tracked } from '../types'

export const DEFAULT_MAX_CONCURRENT = 8
export const ROUTE_OFF = 'off'
/** Model aliases the opt-in routing may pick. Never a full model id: ids retire. */
export const ROUTE_ALIASES = ['sonnet', 'haiku'] as const

/** Statuses `$.agent.list()` reports for an agent that still holds a slot. */
const LIVE_STATUSES = new Set(['pending', 'running', 'waiting'])

const RESEARCH_ROLE_WORDS = ['research', 'explore', 'lookup', 'audit', 'inspector', 'survey']
const READ_PROMPT_PREFIXES = ['search ', 'find ', 'read ', 'lookup ', 'list ']

export function isResearchTask(description?: string, prompt?: string): boolean {
  const d = (description || '').toLowerCase()
  if (RESEARCH_ROLE_WORDS.some(word => d.includes(word))) return true
  const p = (prompt || '').trim().toLowerCase()
  return READ_PROMPT_PREFIXES.some(prefix => p.startsWith(prefix))
}

/** Reads the cap from userConfig: 0 turns the cap off; anything else is held to 1..64. */
export function capFrom(value: unknown): number {
  const n = typeof value === 'number' ? value : Number(value)
  if (value === undefined || !Number.isFinite(n)) return DEFAULT_MAX_CONCURRENT
  if (n <= 0) return 0
  return Math.min(64, Math.max(1, Math.round(n)))
}

/** Reads the routing target from userConfig: an alias from ROUTE_ALIASES, or off. */
export function routeFrom(value: unknown): string {
  return typeof value === 'string' && (ROUTE_ALIASES as readonly string[]).includes(value) ? value : ROUTE_OFF
}

export type RoutingDecision = { model?: string; reason?: string }

/**
 * Opt-in only (route is 'off' by default). Routes a research-shaped spawn that
 * names no model of its own, from an Opus parent, to the configured alias.
 */
export function evaluateModelRouting(params: {
  route: string
  description?: string
  prompt?: string
  model?: string
  parentModel?: string
  isFork?: boolean
}): RoutingDecision {
  if (params.route === ROUTE_OFF) return {}
  if (params.isFork || params.model) return {}
  const p = (params.prompt || '').toLowerCase()
  if (p.includes('use opus') || p.includes('require opus') || p.includes('opus only')) return {}
  if (!(params.parentModel || '').toLowerCase().includes('opus')) return {}
  if (!isResearchTask(params.description, params.prompt)) return {}
  return { model: params.route, reason: `research subagent routed to ${params.route}` }
}

/**
 * Keeps the tracked agents that still hold a slot. `listed` is `$.agent.list()`
 * as id → status; undefined when the list could not be read, which keeps all.
 */
export function reconcile(tracked: readonly Tracked[], listed?: ReadonlyMap<string, string>): Tracked[] {
  if (!listed) return [...tracked]
  return tracked.filter(t => LIVE_STATUSES.has(listed.get(t.id) ?? ''))
}

export function denyText(active: number, cap: number): string {
  return `cure-agent-budget: ${active} subagents are already running in this session (cap ${cap}). Wait for one to finish, or raise maxConcurrent in /plugin → cure-agent-budget.`
}

export type BudgetReport = {
  active: readonly Tracked[]
  cap: number
  route: string
  spawned: number
  denied: number
  routed: number
}

export function formatBudgetReport(r: BudgetReport): string {
  const capText = r.cap === 0 ? 'no cap' : `cap ${r.cap}`
  const lines = [
    `cure-agent-budget: ${r.active.length} running (${capText}) · ${r.spawned} spawned · ${r.denied} denied this session`,
    r.route === ROUTE_OFF
      ? '  Routing: off (subagents run on their own or the session model)'
      : `  Routing: research subagents → ${r.route} (${r.routed} routed)`,
  ]
  for (const t of r.active.slice(0, 10)) lines.push(`  • ${t.id} ${t.description}`.trimEnd())
  if (r.cap > 0 && r.active.length >= r.cap) lines.push(`  Cap reached: the next spawn is refused until one finishes.`)
  return lines.join('\n')
}
