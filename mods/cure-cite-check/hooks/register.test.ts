import { expect, mock, test } from 'claude-code/testing'

import {
  extractCitations,
  formatVerificationNotice,
  verifyCitation,
} from './cite'

// ── Pure unit tests ────────────────────────────────────────────────────────

test('extractCitations: extracts bare and backtick citations', () => {
  const text = 'See `src/index.ts:45` and also helpers/utils.py:120 for details.'
  const cites = extractCitations(text)
  expect(cites.length).toBe(2)
  expect(cites[0].path).toBe('src/index.ts')
  expect(cites[0].line).toBe(45)
  expect(cites[1].path).toBe('helpers/utils.py')
  expect(cites[1].line).toBe(120)
})

test('extractCitations: extracts range citations', () => {
  const text = 'Look at `src/service.ts:10-25`.'
  const cites = extractCitations(text)
  expect(cites.length).toBe(1)
  expect(cites[0].path).toBe('src/service.ts')
  expect(cites[0].line).toBe(10)
  expect(cites[0].endLine).toBe(25)
})

test('extractCitations: extracts markdown link citations', () => {
  const text = 'Defined in [User Component](src/components/User.tsx#L88).'
  const cites = extractCitations(text)
  expect(cites.length).toBe(1)
  expect(cites[0].path).toBe('src/components/User.tsx')
  expect(cites[0].line).toBe(88)
})

test('extractCitations: ignores web URLs with ports', () => {
  const text = 'Running on http://localhost:8080 and https://api.service.com:443.'
  const cites = extractCitations(text)
  expect(cites.length).toBe(0)
})

test('verifyCitation: passes citation within line count', () => {
  const cite = { raw: 'a.ts:25', path: 'a.ts', line: 25 }
  const issue = verifyCitation(cite, true, 50)
  expect(issue).toBeUndefined()
})

test('verifyCitation: flags missing file', () => {
  const cite = { raw: 'missing.ts:25', path: 'missing.ts', line: 25 }
  const issue = verifyCitation(cite, false, 0)
  expect(issue).toBeDefined()
  expect(issue?.reason).toContain('does not exist')
})

test('verifyCitation: flags line exceeding file length', () => {
  const cite = { raw: 'a.ts:120', path: 'a.ts', line: 120 }
  const issue = verifyCitation(cite, true, 80)
  expect(issue).toBeDefined()
  expect(issue?.reason).toContain('exceeds file length (80 lines)')
})

test('formatVerificationNotice: formats clean vs stale results', () => {
  const clean = formatVerificationNotice({ total: 2, valid: 2, stale: [] })
  expect(clean).toContain('2 citation(s) verified ✓')

  const cite = { raw: 'a.ts:99', path: 'a.ts', line: 99 }
  const stale = formatVerificationNotice({
    total: 2,
    valid: 1,
    stale: [{ citation: cite, reason: 'exceeds file length' }],
  })
  expect(stale).toContain('1 stale')
  expect(stale).toContain('a.ts:99')
})

// ── Hook end-to-end tests ──────────────────────────────────────────────────

test('command: /cite-check initially reports no citations', async ($, on) => {
  mock.store(on, {})
  const r = await $.command.run({ command: 'cite-check' })
  expect(r.text).toContain('No code citations checked')
})

test('hook: verifies citations in turn.step and appends notice on stale citation', async ($, on) => {
  mock.store(on, {})

  on('fs.exists', ({ path }: any) => ({
    value: path === 'src/existing.ts',
  }))

  on('fs.read', ({ path }: any) => ({
    value: path === 'src/existing.ts' ? 'line 1\nline 2\nline 3' : '',
  }))

  on('turn.step', async function* (_$: any, e: any) {
    return {
      turnId: e.turnId,
      answer: 'Defined in `src/existing.ts:50` (stale) and `src/missing.ts:10`.',
      toolUses: [],
    }
  })

  const stream = $.turn.step({ turnId: 't1', model: 'claude-3-5-sonnet' })
  for await (const _ of stream) void _

  const r = await $.command.run({ command: 'cite-check' })
  expect(r.text).toContain('2 citation(s) checked')
  expect(r.text).toContain('2 stale')
})
