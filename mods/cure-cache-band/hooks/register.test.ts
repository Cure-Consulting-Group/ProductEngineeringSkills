import { expect, mock, test } from 'claude-code/testing'

import type { CacheState } from '../types'
import { EMPTY, TTL_MS, bandText, bar, hitPercent, inferTtl, leftText, recordStep, reportText, tokensText, view, type StepUsage } from './cache'

const usage = (over: Partial<StepUsage>): StepUsage => ({
  input_tokens: 0,
  output_tokens: 0,
  cache_read_input_tokens: 0,
  cache_creation_input_tokens: 0,
  ...over,
})

const T0 = Date.UTC(2026, 9, 7, 12)

// ── the TTL is inferred, and the override wins ─────────────────────────────

test('inferTtl: override, then subscription limits, then API key', async () => {
  expect(inferTtl('5m', [{ kind: 'five_hour', percentUsed: 10 }])).toBe('5m')
  expect(inferTtl('1h', [])).toBe('1h')
  expect(inferTtl(undefined, [{ kind: 'five_hour', percentUsed: 10 }])).toBe('1h')
  expect(inferTtl(undefined, [{ kind: 'five_hour', percentUsed: 100 }])).toBe('5m')
  expect(inferTtl(undefined, [])).toBe('5m')
  expect(inferTtl('nonsense', [])).toBe('5m')
})

// ── the arithmetic ─────────────────────────────────────────────────────────

test('the first request writes the cache and is not a miss', async () => {
  const s = recordStep(EMPTY, usage({ input_tokens: 10, cache_creation_input_tokens: 40_000, output_tokens: 500 }), T0, '1h')
  expect(s.misses).toBe(0)
  expect(s.requests).toBe(1)
  expect(s.prefixTokens).toBe(40_010)
  expect(s.nextTokens).toBe(40_510)
  expect(hitPercent(s)).toBe(0)
})

test('a request that reads the prefix is a hit; the rate is read over all prompt tokens', async () => {
  let s = recordStep(EMPTY, usage({ cache_creation_input_tokens: 40_000 }), T0, '1h')
  s = recordStep(s, usage({ cache_read_input_tokens: 40_000, cache_creation_input_tokens: 2_000, input_tokens: 0 }), T0 + 1000, '1h')
  expect(s.misses).toBe(0)
  // 40k read of 82k prompt tokens seen.
  expect(hitPercent(s)).toBe(49)
})

test('a request that reads under half the previous prefix is a miss', async () => {
  let s = recordStep(EMPTY, usage({ cache_creation_input_tokens: 40_000 }), T0, '5m')
  s = recordStep(s, usage({ cache_read_input_tokens: 19_999, cache_creation_input_tokens: 21_000 }), T0 + 1000, '5m')
  expect(s.misses).toBe(1)
  s = recordStep(s, usage({ cache_read_input_tokens: 20_500, cache_creation_input_tokens: 21_000 }), T0 + 2000, '5m')
  expect(s.misses).toBe(1)
})

test('a prefix too short to cache never counts as a miss', async () => {
  let s = recordStep(EMPTY, usage({ input_tokens: 800 }), T0, '5m')
  s = recordStep(s, usage({ input_tokens: 900 }), T0 + 1000, '5m')
  expect(s.misses).toBe(0)
})

// ── what the band shows as time passes ─────────────────────────────────────

const warm = (ttl: '5m' | '1h'): CacheState =>
  recordStep(
    recordStep(EMPTY, usage({ cache_creation_input_tokens: 20_000 }), T0 - 1000, ttl),
    usage({ cache_read_input_tokens: 20_000, cache_creation_input_tokens: 6_000, output_tokens: 1_000 }),
    T0,
    ttl,
  )

test('nothing before the first response', async () => {
  expect(view(EMPTY, T0)).toEqual({ kind: 'none' })
  expect(bandText(view(EMPTY, T0))).toBe('')
})

test('a fresh 1h cache: full bar, minutes left', async () => {
  const v = view(warm('1h'), T0 + 30_000)
  expect(v.kind).toBe('warm')
  expect(bandText(v)).toBe('cache ● 1h ████████████████ 59m left · hit 43% · misses 0')
})

test('a 5m cache with under a quarter left is low and counts seconds', async () => {
  const v = view(warm('5m'), T0 + TTL_MS['5m'] - 53_000)
  expect(v.kind === 'warm' && v.level).toBe('low')
  expect(bandText(v)).toBe('cache ● 5m ███░░░░░░░░░░░░░ 53s left · hit 43% · misses 0')
})

test('the level flips at a quarter of the TTL', async () => {
  const at = (leftMs: number) => view(warm('1h'), T0 + TTL_MS['1h'] - leftMs)
  expect(at(15 * 60_000 + 1)).toMatchObject({ level: 'ok' })
  expect(at(15 * 60_000 - 1)).toMatchObject({ level: 'low' })
})

test('past the TTL the cache is cold and the next message re-caches everything it re-sends', async () => {
  const s = warm('5m')
  expect(view(s, T0 + TTL_MS['5m'] - 1).kind).toBe('warm')
  const v = view(s, T0 + TTL_MS['5m'])
  expect(v).toEqual({ kind: 'cold', tokens: 27_000 })
  expect(bandText(v)).toBe('cache ○ cold · next message re-caches 27k tokens')
})

test('formatting', async () => {
  expect(leftText(59 * 60_000 + 30_000)).toBe('59m left')
  expect(leftText(61_000)).toBe('1m left')
  expect(leftText(60_000)).toBe('60s left')
  expect(leftText(400)).toBe('1s left')
  expect(tokensText(950)).toBe('950')
  expect(tokensText(82_400)).toBe('82k')
  expect(tokensText(1_250_000)).toBe('1.3M')
  expect(bar(1, 8)).toEqual({ filled: '████████', empty: '' })
  expect(bar(0.001, 8)).toEqual({ filled: '█', empty: '░░░░░░░' })
})

test('the report names the TTL source and, when cold, the write rate', async () => {
  const s = warm('5m')
  expect(reportText(EMPTY, T0, 'x')).toMatch(/no model response yet/)
  expect(reportText(s, T0 + 1000, 'CURE_CACHE_TTL')).toMatch(/TTL assumed {11}5m \(CURE_CACHE_TTL\)/)
  expect(reportText(s, T0 + TTL_MS['5m'], 'x')).toMatch(/27k tokens, all at the cache-write rate/)
})

// ── the hooks, end to end ──────────────────────────────────────────────────

const subscription = () => ({ value: { startedAt: T0, context: { window: 200_000 }, rateLimits: [{ kind: 'five_hour', percentUsed: 12 }] } })

const respond = (u: StepUsage) =>
  async function* (_$: unknown, e: { turnId: string; index: number }) {
    return { turnId: e.turnId, index: e.index, answer: 'ok', toolUses: [], stopReason: 'end_turn', usage: { ...u, model: 'claude-opus-5-5' } }
  }

const step = async ($: any, index: number, agentId?: string) => {
  const stream = $.turn.step({ turnId: 't1', index, model: 'claude-opus-5-5', messageCount: 1 + index, ...(agentId ? { agentId } : {}) })
  for await (const _ of stream) void _
}

const bandProps = { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 100, scroll: { offset: 0, bodyRows: 10 }, view: {} }

test('/cache before any response says so', async ($, on) => {
  mock.clock(on, { now: T0 })
  mock.env(on, {})
  on('session.usage', subscription)
  const r = await $.command.run({ command: 'cache' } as never)
  expect(r.text).toMatch(/no model response yet/)
})

for (const surface of ['terminal', 'desktop'] as const) {
  test(`a response warms the band, time drains it, and it goes cold (${surface})`, async ($, on) => {
    const clock = mock.clock(on, { now: T0 })
    mock.env(on, {})
    on('session.usage', subscription)
    on('turn.step', respond(usage({ cache_creation_input_tokens: 80_000, output_tokens: 2_000 })) as never)
    // The engine's own band, which the mod yields to before the first response: empty.
    on('ui.render', ($$, e) => h($$.ui.resolve(e).Box, null) as never)

    const text = async () => {
      const ui = await $.ui.mount({ plugin: 'cure-cache-band', surface, component: 'AbovePrompt', props: bandProps as never })
      const found = await ui.findAll({ type: 'Text' })
      await ui.unmount()
      return found.map(el => el.text).join('')
    }

    expect(await text()).toBe('')
    await step($, 0)
    expect(await text()).toBe('cache ● 1h ████████████████ 60m left · hit 0% · misses 0')
    await clock.advance(50 * 60_000)
    expect(await text()).toBe('cache ● 1h ███░░░░░░░░░░░░░ 10m left · hit 0% · misses 0')
    await clock.advance(10 * 60_000)
    expect(await text()).toBe('cache ○ cold · next message re-caches 82k tokens')
  })
}

test('the band yields to a survey', async ($, on) => {
  mock.clock(on, { now: T0 })
  mock.env(on, {})
  on('session.usage', subscription)
  on('turn.step', respond(usage({ cache_creation_input_tokens: 80_000 })) as never)
  on('ui.render', ($$, e) => h($$.ui.resolve(e).Box, null) as never)
  await step($, 0)
  const ui = await $.ui.mount({ plugin: 'cure-cache-band', surface: 'terminal', component: 'AbovePrompt', props: { ...bandProps, hasSurvey: true } as never })
  expect(await ui.findAll({ type: 'Text' })).toHaveLength(0)
})

test('a subagent\'s request does not touch the main conversation\'s cache figures', async ($, on) => {
  mock.clock(on, { now: T0 })
  mock.env(on, {})
  on('session.usage', subscription)
  on('turn.step', respond(usage({ cache_creation_input_tokens: 80_000 })) as never)
  await step($, 0, 'agent-1')
  const r = await $.command.run({ command: 'cache' } as never)
  expect(r.text).toMatch(/no model response yet/)
})

test('CURE_CACHE_TTL overrides the inferred TTL', async ($, on) => {
  mock.clock(on, { now: T0 })
  mock.env(on, { CURE_CACHE_TTL: '5m' })
  on('session.usage', subscription)
  on('turn.step', respond(usage({ cache_creation_input_tokens: 80_000 })) as never)
  await step($, 0)
  const r = await $.command.run({ command: 'cache' } as never)
  expect(r.text).toMatch(/cache ● 5m/)
  expect(r.text).toMatch(/5m \(CURE_CACHE_TTL\)/)
})
