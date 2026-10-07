import { expect, mock, test } from 'claude-code/testing'

import { bandText, daysInMonth, parseUsage, reportText, summarize, warningText, type UsageItem } from './spend'

const item = (over: Partial<UsageItem>): UsageItem => ({
  date: '2026-10-05T00:00:00Z',
  product: 'actions',
  sku: 'Actions Linux',
  quantity: 100,
  unitType: 'Minutes',
  grossAmount: 0,
  discountAmount: 0,
  netAmount: 0,
  repositoryName: 'DistrictZero',
  ...over,
})

// Noon UTC on 5 October: 4.5 days elapsed of a 31-day month.
const NOON_OCT_5 = new Date(Date.UTC(2026, 9, 5, 12))

// ── arithmetic, as pure functions ──────────────────────────────────────────

test('daysInMonth follows the calendar', async () => {
  expect(daysInMonth(new Date(Date.UTC(2026, 9, 5)))).toBe(31)
  expect(daysInMonth(new Date(Date.UTC(2026, 1, 3)))).toBe(28)
})

test('summarize splits today from the month and Actions from everything billed', async () => {
  const s = summarize(
    [
      item({ date: '2026-10-03T00:00:00Z', grossAmount: 8.92, netAmount: 0 }),
      item({ date: '2026-10-05T00:00:00Z', grossAmount: 3.97, netAmount: 0 }),
      item({ date: '2026-10-05T00:00:00Z', grossAmount: 2.2, repositoryName: 'statledger' }),
      item({ date: '2026-10-05T00:00:00Z', product: 'ghec', sku: 'Enterprise Cloud', grossAmount: 0.68, netAmount: 0.68 }),
    ],
    NOON_OCT_5,
    300,
  )
  expect(s.today).toBe('2026-10-05')
  expect(s.actionsToday).toBe(6.17)
  expect(s.actionsMonth).toBe(15.09)
  expect(s.billedMonth).toBe(0.68)
  expect(s.dailyAllowance).toBe(9.68)
  expect(s.topRepoToday).toEqual({ repo: 'DistrictZero', amount: 3.97 })
})

test('the projection is month to date plus the last three full days\' average', async () => {
  // Month to date $65; the last three full days (4th, 3rd, 2nd) average $10; 26.5 days remain at noon on the 5th.
  const s = summarize(
    [
      item({ date: '2026-10-01T00:00:00Z', grossAmount: 30 }),
      item({ date: '2026-10-02T00:00:00Z', grossAmount: 20 }),
      item({ date: '2026-10-03T00:00:00Z', grossAmount: 9 }),
      item({ date: '2026-10-04T00:00:00Z', grossAmount: 1 }),
      item({ date: '2026-10-05T00:00:00Z', grossAmount: 5 }),
    ],
    NOON_OCT_5,
    300,
  )
  expect(s.paceDays).toBe(3)
  expect(s.recentDailyPace).toBe(10)
  expect(s.projectedActions).toBe(330)
  expect(s.projectedOverage).toBe(30)
  expect(warningText(s)).toMatch(/headed for \$330\.00 this month at the recent \$10\.00\/day, \$30\.00 over the \$300\.00 included/)
})

test('an expensive early day stops counting once three newer full days exist', async () => {
  // The failure this replaced: $64 on the 1st-2nd projected the whole month as if every day cost that.
  const early = [item({ date: '2026-10-01T00:00:00Z', grossAmount: 41 }), item({ date: '2026-10-02T00:00:00Z', grossAmount: 23 })]
  const quiet = ['03', '04', '05'].map(d => item({ date: `2026-10-${d}T00:00:00Z`, grossAmount: 2 }))
  const s = summarize([...early, ...quiet, item({ date: '2026-10-06T00:00:00Z', grossAmount: 1 })], new Date(Date.UTC(2026, 9, 6, 12)), 300)
  expect(s.recentDailyPace).toBe(2)
  expect(s.projectedOverage).toBe(0)
})

test('a day with no usage counts as $0 in the recent average', async () => {
  const s = summarize([item({ date: '2026-10-02T00:00:00Z', grossAmount: 9 })], NOON_OCT_5, 300)
  expect(s.paceDays).toBe(3)
  expect(s.recentDailyPace).toBe(3)
})

test('before the month has a full day, month-to-date pace is used', async () => {
  const s = summarize([item({ date: '2026-10-01T00:00:00Z', grossAmount: 10 })], new Date(Date.UTC(2026, 9, 1, 18)), 300)
  expect(s.paceDays).toBe(0)
  expect(s.recentDailyPace).toBe(13.33)
  expect(s.projectedActions).toBe(413.33)
})

test('inside the allowance there is no warning', async () => {
  const s = summarize([item({ date: '2026-10-04T00:00:00Z', grossAmount: 20 })], NOON_OCT_5, 300)
  expect(s.projectedOverage).toBe(0)
  expect(warningText(s)).toBeUndefined()
})

test('the first hours of a month do not extrapolate a spike', async () => {
  const s = summarize([item({ date: '2026-10-01T00:00:00Z', grossAmount: 5 })], new Date(Date.UTC(2026, 9, 1, 2)), 300)
  expect(s.projectedActions).toBe(5)
})

test('band and report text', async () => {
  const s = summarize([item({ grossAmount: 4.34 })], NOON_OCT_5, 300)
  expect(bandText(s)).toBe('Actions $4.34 today · $9.68/day covered')
  expect(reportText(s, '12:00 UTC', 'Cure-Consulting-Group')).toMatch(/Actions this month {3}\$4\.34/)
})

test('parseUsage refuses a response without usage items', async () => {
  expect(parseUsage('{"usageItems":[]}')).toEqual([])
  expect(() => parseUsage('{"message":"Not Found"}')).toThrow(/no usageItems/)
})

// ── the hooks, end to end ──────────────────────────────────────────────────

const billing = (items: UsageItem[]) => (_$: any, e: any) => {
  const argv: string[] = e.argv ?? e.args ?? e
  return argv[0] === 'gh'
    ? { value: { exitCode: 0, stdout: JSON.stringify({ usageItems: items }), stderr: '' } }
    : { value: { exitCode: 1, stdout: '', stderr: 'unexpected' } }
}

test('/spend reports the month from gh, and asks for the right month', async ($, on) => {
  mock.clock(on, { now: NOON_OCT_5.getTime() })
  mock.env(on, {})
  const calls: string[][] = []
  on('process.run', (_$: any, e: any) => {
    calls.push(e.argv ?? e.args ?? e)
    return billing(['01', '02', '03', '04'].map(d => item({ date: `2026-10-${d}T00:00:00Z`, grossAmount: 12 })))(_$, e)
  })
  const r = await $.command.run({ command: 'spend' })
  expect(r.text).toMatch(/GitHub spend for Cure-Consulting-Group/)
  // $48 so far; the last three full days average $12; 26.5 days remain: $366.
  expect(r.text).toMatch(/Projected month end {2}\$366\.00 {3}→ \$66\.00 over/)
  expect(r.text).toMatch(/last 3 full days' average, \$12\.00\/day/)
  expect(calls[0]).toEqual(['gh', 'api', 'organizations/Cure-Consulting-Group/settings/billing/usage?year=2026&month=10'])
})

test('the org and allowance come from the environment', async ($, on) => {
  mock.clock(on, { now: NOON_OCT_5.getTime() })
  mock.env(on, { CURE_SPEND_ORG: 'Other-Org', CURE_SPEND_ALLOWANCE: '1000' })
  on('process.run', billing([item({ grossAmount: 45 })]))
  const r = await $.command.run({ command: 'spend' })
  expect(r.text).toMatch(/GitHub spend for Other-Org/)
  expect(r.text).toMatch(/inside the allowance/)
})

test('when gh fails, /spend says why instead of showing numbers', async ($, on) => {
  mock.clock(on, { now: NOON_OCT_5.getTime() })
  mock.env(on, { CURE_SPEND_ORG: 'Broken-Org' })
  on('process.run', () => ({ value: { exitCode: 1, stdout: '', stderr: 'gh: Not Found (HTTP 404)\n' } }))
  const r = await $.command.run({ command: 'spend' })
  // Whether or not an earlier fetch succeeded, the failure is named.
  expect(r.text).toMatch(/gh: Not Found \(HTTP 404\)/)
})

test('the refresh timer starts at session start and is cancelled at session end', async ($, on) => {
  const clock = mock.clock(on, { now: NOON_OCT_5.getTime() })
  mock.env(on, {})
  let fetches = 0
  on('process.run', (_$: any, e: any) => {
    fetches += 1
    return billing([item({ grossAmount: 1 })])(_$, e)
  })
  on('command.register', () => ({ value: undefined }))
  on('session.start', (_$: any, e: any) => ({ cwd: e.cwd }))
  on('session.end', () => ({ sessionId: 'test' }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.invalidate', () => ({ value: undefined }))
  await $.session.start({ cwd: '/repo', surface: null, isInteractive: false })
  // Two refresh periods pass: the timer fetches on each.
  await clock.advance(31 * 60 * 1000)
  const whileRunning = fetches
  await $.session.end({ cwd: '/repo', reason: 'other' })
  await clock.advance(60 * 60 * 1000)
  expect(whileRunning).toBeGreaterThanOrEqual(2)
  expect(fetches).toBe(whileRunning)
})
