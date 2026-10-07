import { expect, mock, test } from 'claude-code/testing'

import {
  calculateCost,
  createLedgerEntry,
  formatLedgerSummary,
  resolvePricing,
} from './ledger'

// ── Pure unit tests ────────────────────────────────────────────────────────

test('resolvePricing: maps model families accurately', () => {
  expect(resolvePricing('claude-3-opus-20240229').inputPerM).toBe(15.0)
  expect(resolvePricing('claude-3-5-sonnet-20241022').inputPerM).toBe(3.0)
  expect(resolvePricing('claude-3-5-haiku-20241022').inputPerM).toBe(0.8)
  expect(resolvePricing('unknown-model').inputPerM).toBe(3.0) // default sonnet
})

test('calculateCost: computes accurate token costs', () => {
  // 10,000 input tokens on Sonnet ($3/M) = $0.03
  // 2,000 output tokens on Sonnet ($15/M) = $0.03
  // 5,000 cache read on Sonnet ($0.30/M) = $0.0015
  // Total = $0.0615
  const cost = calculateCost('claude-3-5-sonnet', {
    inputTokens: 10_000,
    cacheWriteTokens: 0,
    cacheReadTokens: 5_000,
    outputTokens: 2_000,
  })
  expect(cost).toBe(0.0615)
})

test('calculateCost: computes Opus rates correctly', () => {
  // 1M input tokens on Opus ($15/M) = $15.00
  // 1M output tokens on Opus ($75/M) = $75.00
  const cost = calculateCost('claude-3-opus', {
    inputTokens: 1_000_000,
    cacheWriteTokens: 0,
    cacheReadTokens: 0,
    outputTokens: 1_000_000,
  })
  expect(cost).toBe(90.0)
})

test('createLedgerEntry: constructs atomic record', () => {
  const entry = createLedgerEntry({
    timestamp: '2026-10-07T12:00:00Z',
    repo: 'ProductEngineeringSkills',
    branch: 'main',
    model: 'claude-3-5-sonnet',
    usage: {
      inputTokens: 1000,
      cacheWriteTokens: 500,
      cacheReadTokens: 200,
      outputTokens: 100,
    },
  })

  expect(entry.repo).toBe('ProductEngineeringSkills')
  expect(entry.cost_usd).toBeGreaterThan(0)
  expect(entry.input_tokens).toBe(1000)
})

test('formatLedgerSummary: reports empty session gracefully', () => {
  const summary = formatLedgerSummary({
    totalCostUsd: 0,
    totalInput: 0,
    totalCacheWrite: 0,
    totalCacheRead: 0,
    totalOutput: 0,
    byModel: {},
  })
  expect(summary).toContain('No model usage recorded')
})

test('formatLedgerSummary: formats multi-model breakdown', () => {
  const summary = formatLedgerSummary({
    totalCostUsd: 0.125,
    totalInput: 15000,
    totalCacheWrite: 2000,
    totalCacheRead: 8000,
    totalOutput: 1200,
    byModel: {
      'claude-3-5-sonnet': { turns: 3, costUsd: 0.085, tokens: 20000 },
      'claude-3-5-haiku': { turns: 2, costUsd: 0.04, tokens: 6200 },
    },
  })
  expect(summary).toContain('$0.1250')
  expect(summary).toContain('claude-3-5-sonnet')
  expect(summary).toContain('claude-3-5-haiku')
})

// ── Hook end-to-end tests ──────────────────────────────────────────────────

test('command: /ledger before turns reports no usage', async ($, on) => {
  mock.store(on, {})
  const r = await $.command.run({ command: 'ledger' })
  expect(r.text).toContain('No model usage recorded')
})

test('hook: turn.step updates session totals and ledger', async ($, on) => {
  mock.store(on, {})

  on('turn.step', async function* (_$: any, e: any) {
    return {
      turnId: e.turnId,
      answer: 'ok',
      toolUses: [],
      model: 'claude-3-5-sonnet',
      usage: {
        input_tokens: 10_000,
        cache_creation_input_tokens: 0,
        cache_read_input_tokens: 5_000,
        output_tokens: 2_000,
      },
    }
  })

  const stream = $.turn.step({ turnId: 't1', model: 'claude-3-5-sonnet' })
  for await (const _ of stream) void _

  const r = await $.command.run({ command: 'ledger' })
  expect(r.text).toContain('$0.0615')
  expect(r.text).toContain('10,000 in')
  expect(r.text).toContain('claude-3-5-sonnet')
})
