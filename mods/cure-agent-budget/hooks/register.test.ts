import { expect, mock, test } from 'claude-code/testing'

import {
  DEFAULT_MAX_CONCURRENT,
  evaluateModelRouting,
  formatBudgetReport,
  isResearchTask,
} from './budget'

// ── Pure unit tests ────────────────────────────────────────────────────────

test('isResearchTask: recognizes research roles and read queries', () => {
  expect(isResearchTask('Codebase Researcher', 'Check files')).toBe(true)
  expect(isResearchTask('Explorer', 'Investigate repository')).toBe(true)
  expect(isResearchTask('Auditor', 'Audit licenses')).toBe(true)
  expect(isResearchTask('Developer', 'search for imports in package.json')).toBe(true)
  expect(isResearchTask('Engineer', 'Write new database schema')).toBe(false)
})

test('evaluateModelRouting: down-routes research tasks on Opus to Sonnet', () => {
  const decision = evaluateModelRouting({
    role: 'Codebase Researcher',
    prompt: 'Find all callers of api()',
    currentModel: 'claude-3-opus-20240229',
  })
  expect(decision.shouldRoute).toBe(true)
  expect(decision.newModel).toBe('claude-3-5-sonnet')
})

test('evaluateModelRouting: honors explicit Opus request in prompt', () => {
  const decision = evaluateModelRouting({
    role: 'Codebase Researcher',
    prompt: 'Require Opus only for this deep theoretical review',
    currentModel: 'claude-3-opus-20240229',
  })
  expect(decision.shouldRoute).toBe(false)
})

test('evaluateModelRouting: leaves engineering implementation tasks alone', () => {
  const decision = evaluateModelRouting({
    role: 'Full Stack Engineer',
    prompt: 'Refactor authentication module',
    currentModel: 'claude-3-opus-20240229',
  })
  expect(decision.shouldRoute).toBe(false)
})

test('formatBudgetReport: formats active vs limit metrics', () => {
  const text = formatBudgetReport({
    activeCount: 2,
    maxLimit: 4,
    cumulativeSpawned: 5,
    downRoutedCount: 3,
  })
  expect(text).toContain('2/4 active subagents')
  expect(text).toContain('3 subagent(s) routed to Sonnet')
})

test('formatBudgetReport: warns when concurrency cap is reached', () => {
  const text = formatBudgetReport({
    activeCount: 4,
    maxLimit: 4,
    cumulativeSpawned: 6,
    downRoutedCount: 2,
  })
  expect(text).toContain('⚠️  Concurrency cap reached')
})

// ── Hook end-to-end tests ──────────────────────────────────────────────────

test('command: /agents-budget reports initial zero active', async ($, on) => {
  mock.store(on, {})
  const r = await $.command.run({ command: 'agents-budget' })
  expect(r.text).toContain('0/4 active subagents')
})

test('hook: routes research agent and tracks active count', async ($, on) => {
  mock.store(on, {})

  let routedModel = ''
  on('tool.call', (_$: any, e: any) => {
    routedModel = e.model
    return { result: 'subagent finished' }
  })

  const r = await $.tool.call({
    tool: 'Agent',
    role: 'Codebase Researcher',
    prompt: 'search for files',
    model: 'claude-3-opus-20240229',
  })

  expect(r.result).toBe('subagent finished')
  expect(routedModel).toBe('claude-3-5-sonnet')

  const stats = await $.command.run({ command: 'agents-budget' })
  expect(stats.text).toContain('1 subagent(s) routed to Sonnet')
  expect(stats.text).toContain('1 total spawned')
  expect(stats.text).toContain('0/4 active subagents') // finished
})

test('hook: blocks spawning when concurrency cap is exceeded', async ($, on) => {
  mock.store(on, {
    'cure-agent-budget-stats': {
      activeCount: DEFAULT_MAX_CONCURRENT,
      maxLimit: DEFAULT_MAX_CONCURRENT,
      cumulativeSpawned: 4,
      downRoutedCount: 0,
    },
  })

  const r = await $.tool.call({
    tool: 'Agent',
    role: 'Worker',
    prompt: 'task',
  })

  expect(r.deny).toContain('Maximum concurrent subagents (4) reached')
})
