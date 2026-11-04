import { expect, mock, test } from 'claude-code/testing'

import {
  capFrom,
  evaluateModelRouting,
  formatBudgetReport,
  isResearchTask,
  reconcile,
  routeFrom,
} from './budget'

// ── Pure unit tests ────────────────────────────────────────────────────────

test('isResearchTask: recognizes research descriptions and read prompts', () => {
  expect(isResearchTask('Codebase Researcher', 'Check files')).toBe(true)
  expect(isResearchTask('Audit licenses', 'x')).toBe(true)
  expect(isResearchTask('Developer', 'search for imports in package.json')).toBe(true)
  expect(isResearchTask('Engineer', 'Write new database schema')).toBe(false)
})

test('routing is off by default and never names a full model id', () => {
  expect(routeFrom(undefined)).toBe('off')
  expect(routeFrom('claude-sonnet-x')).toBe('off')
  expect(routeFrom('sonnet')).toBe('sonnet')
  const off = evaluateModelRouting({ route: 'off', description: 'audit', prompt: 'find x', parentModel: 'opus' })
  expect(off.model).toBeUndefined()
  const on = evaluateModelRouting({ route: 'sonnet', description: 'audit', prompt: 'find x', parentModel: 'claude-opus-5-5' })
  expect(on.model).toBe('sonnet')
})

test('routing leaves explicit models, forks, non-Opus parents and "use opus" alone', () => {
  const base = { route: 'sonnet', description: 'audit', prompt: 'find x', parentModel: 'opus' }
  expect(evaluateModelRouting({ ...base, model: 'opus' }).model).toBeUndefined()
  expect(evaluateModelRouting({ ...base, isFork: true }).model).toBeUndefined()
  expect(evaluateModelRouting({ ...base, parentModel: 'sonnet' }).model).toBeUndefined()
  expect(evaluateModelRouting({ ...base, prompt: 'use opus please' }).model).toBeUndefined()
})

test('capFrom: 0 disables, others held to 1..64, junk falls back to the default', () => {
  expect(capFrom(0)).toBe(0)
  expect(capFrom(3)).toBe(3)
  expect(capFrom(999)).toBe(64)
  expect(capFrom('x')).toBe(8)
})

test('reconcile drops agents the engine lists as finished or does not list', () => {
  const t = [
    { id: 'a', description: '', startedAt: 0 },
    { id: 'b', description: '', startedAt: 0 },
    { id: 'c', description: '', startedAt: 0 },
  ]
  const listed = new Map([['a', 'running'], ['b', 'completed']])
  expect(reconcile(t, listed).map(x => x.id)).toEqual(['a'])
  expect(reconcile(t, undefined).length).toBe(3)
})

test('formatBudgetReport: shows running, cap and routing', () => {
  const text = formatBudgetReport({
    active: [{ id: 'a1', description: 'audit', startedAt: 0 }],
    cap: 4,
    route: 'off',
    spawned: 5,
    denied: 1,
    routed: 0,
  })
  expect(text).toContain('1 running (cap 4)')
  expect(text).toContain('Routing: off')
})

// ── Hook end-to-end tests ──────────────────────────────────────────────────

const LEGACY_KEY = 'cure-agent-budget-stats'

/** A machine store beneath the plugin, kept in a Map the test can read. */
function store(on: any, entries: Record<string, unknown> = {}) {
  const m = new Map<string, unknown>(Object.entries(entries))
  on('store.get', (_$: any, e: any) => ({ value: m.get(e.key) }))
  on('store.set', (_$: any, e: any) => (m.set(e.key, e.value), { value: undefined }))
  on('store.delete', (_$: any, e: any) => (m.delete(e.key), { value: undefined }))
  on('store.keys', () => ({ value: [...m.keys()] }))
  return m
}

/** The engine beneath: every spawn starts agent `a<n>`; the list reports `live`. */
function engine(on: any, live: Map<string, string>) {
  const seen: Array<{ model?: string }> = []
  let n = 0
  mock.clock(on)
  on('command.register', (_$: any, e: any) => ({ value: { command: e.name } }))
  on('session.start', (_$: any, e: any) => ({ cwd: e.cwd }))
  on('session.end', () => ({ sessionId: 's1' }))
  on('agent.list', () => ({
    value: [...live.entries()].map(([id, status]) => ({ id, status, description: '', type: 'general-purpose' })),
  }))
  on('agent.spawn', (_$: any, e: any) => {
    n += 1
    const agentId = `a${n}`
    live.set(agentId, 'running')
    seen.push({ model: e.model })
    return { model: e.model ?? e.parentModel, agentId }
  })
  on('turn.complete', () => ({ text: '' }))
  return seen
}

const SPAWN = (description: string) => ({
  prompt: 'look around',
  description,
  subagentType: 'general-purpose',
  parentModel: 'claude-opus-5-5',
  background: true,
  fork: false,
})

test('a stuck machine-global count from an old session is cleared at session start', async ($, on) => {
  // The live defect: the store said 3 active with 2 real agents, and spawns were denied.
  const m = store(on, { [LEGACY_KEY]: { activeCount: 8, maxLimit: 8, cumulativeSpawned: 9, downRoutedCount: 0 } })
  engine(on, new Map())
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  const r: any = await $.agent.spawn(SPAWN('worker'))
  expect(r.deny).toBeUndefined()
  expect(m.has(LEGACY_KEY)).toBe(false)
})

test('spawn, end the session without completion, start a new session: count is 0', async ($, on) => {
  store(on)
  const live = new Map<string, string>()
  engine(on, live)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.agent.spawn(SPAWN('worker'))
  expect((await $.command.run({ command: 'agents-budget' })).text).toContain('1 running')

  await $.session.end({ reason: 'other' } as any)
  live.clear() // the old session's agents died with it
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  expect((await $.command.run({ command: 'agents-budget' })).text).toContain('0 running')
})

test('turn.complete of a tracked agent frees its slot', { options: { maxConcurrent: 1 } }, async ($, on) => {
  store(on)
  const live = new Map<string, string>()
  engine(on, live)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  const first: any = await $.agent.spawn(SPAWN('one'))
  expect(first.agentId).toBe('a1')
  const blocked: any = await $.agent.spawn(SPAWN('two'))
  expect(blocked.deny).toContain('cap 1')

  await $.turn.complete({ answer: 'done', durationMs: 1, isAborted: false, turnId: 't', agentId: 'a1', reason: 'answer' } as any)
  const second: any = await $.agent.spawn(SPAWN('two'))
  expect(second.deny).toBeUndefined()
})

test('the cap counts only agents the engine still lists as running', { options: { maxConcurrent: 2 } }, async ($, on) => {
  store(on)
  const live = new Map<string, string>()
  engine(on, live)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.agent.spawn(SPAWN('one'))
  await $.agent.spawn(SPAWN('two'))
  live.set('a1', 'killed') // no turn.complete ever arrived for it
  const third: any = await $.agent.spawn(SPAWN('three'))
  expect(third.deny).toBeUndefined()
})

test('five parallel "audit" agents all start on the session model by default', async ($, on) => {
  store(on)
  const seen = engine(on, new Map())
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  for (let i = 0; i < 5; i++) {
    const r: any = await $.agent.spawn(SPAWN(`audit lane ${i}`))
    expect(r.deny).toBeUndefined()
  }
  expect(seen.length).toBe(5)
  expect(seen.every(s => s.model === undefined)).toBe(true)
})

test('a model Agent call with "audit" in its description is not rewritten', async ($, on) => {
  // The live defect: 23 of 357 spawns were rewritten to a retired model id.
  store(on)
  engine(on, new Map())
  let model: unknown = 'unset'
  on('tool.call', (_$: any, e: any) => ((model = e.model), { result: 'ok' }))
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.tool.call({ tool: 'Agent', description: 'audit the hooks', prompt: 'find hooks', model: 'opus' } as any)
  expect(model).toBe('opus')
})

test('opt-in routing sends an Opus parent\'s research agent to the alias', { options: { routeResearchTo: 'sonnet' } }, async ($, on) => {
  store(on)
  const seen = engine(on, new Map())
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.agent.spawn(SPAWN('audit the rules'))
  expect(seen[0].model).toBe('sonnet')
})

test('workflow agents are not counted against the cap', { options: { maxConcurrent: 1 } }, async ($, on) => {
  store(on)
  engine(on, new Map())
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.agent.spawn(SPAWN('one'))
  const wf: any = await $.agent.spawn({ ...SPAWN('wf'), workflow: { runId: 'wf_1', agentIndex: 1 } } as any)
  expect(wf.deny).toBeUndefined()
})
