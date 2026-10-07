import { expect, mock, test } from 'claude-code/testing'

import {
  detectStateFromPath,
  evaluateClaim,
  formatClaimsReport,
  parseStateTargets,
} from './claims'

// ── Pure unit tests ────────────────────────────────────────────────────────

const SAMPLE_MD = `
# State Build Targets

| State | Owner | Status |
|---|---|---|
| AL | mac-mini | in-progress |
| CA | macbook | completed |
| NY | mac-mini | pending |
| TX | macbook | in-progress |
`

test('parseStateTargets: parses markdown table claims', () => {
  const claims = parseStateTargets(SAMPLE_MD)
  expect(claims.size).toBe(4)
  expect(claims.get('AL')).toBe('mac-mini')
  expect(claims.get('CA')).toBe('macbook')
  expect(claims.get('NY')).toBe('mac-mini')
  expect(claims.get('TX')).toBe('macbook')
})

test('detectStateFromPath: extracts 2-letter state code from script paths', () => {
  expect(detectStateFromPath('scripts/build-al-tax.js')).toBe('AL')
  expect(detectStateFromPath('scripts/lib/ca/rules.ts')).toBe('CA')
  expect(detectStateFromPath('scripts/data-ny.csv')).toBe('NY')
  expect(detectStateFromPath('scripts/lib/tx_engine.ts')).toBe('TX')
  expect(detectStateFromPath('src/components/Header.tsx')).toBeUndefined()
})

test('evaluateClaim: approves state owned by local host', () => {
  const claims = parseStateTargets(SAMPLE_MD)
  const verdict = evaluateClaim('CA', 'macbook-pro.local', claims)
  expect(verdict.allowed).toBe(true)
  expect(verdict.reason).toBeUndefined()
})

test('evaluateClaim: denies state owned by another host', () => {
  const claims = parseStateTargets(SAMPLE_MD)
  const verdict = evaluateClaim('AL', 'macbook-pro.local', claims)
  expect(verdict.allowed).toBe(false)
  expect(verdict.reason).toContain("owned by 'mac-mini'")
})

test('evaluateClaim: allows unclaimed states', () => {
  const claims = parseStateTargets(SAMPLE_MD)
  const verdict = evaluateClaim('FL', 'macbook-pro.local', claims)
  expect(verdict.allowed).toBe(true)
})

test('formatClaimsReport: annotates local machine states', () => {
  const claims = parseStateTargets(SAMPLE_MD)
  const report = formatClaimsReport('macbook', claims)
  expect(report).toContain("Machine 'macbook'")
  expect(report).toContain('CA: macbook (this machine)')
  expect(report).toContain('AL: mac-mini')
  expect(report).toContain('Total owned by this machine: 2')
})

// ── Hook end-to-end tests ──────────────────────────────────────────────────

test('command: /claims without targets file reports missing file', async ($, on) => {
  mock.store(on, {})
  on('fs.exists', () => ({ value: false }))
  on('process.run', () => ({ value: { exitCode: 0, stdout: 'macbook\n', stderr: '' } }))

  const r = await $.command.run({ command: 'claims' })
  expect(r.text).toContain('No .agents/state-targets.md found')
})

test('command: /claims with targets file displays report', async ($, on) => {
  mock.store(on, {})
  on('fs.exists', () => ({ value: true }))
  on('fs.read', () => ({ value: SAMPLE_MD }))
  on('process.run', () => ({ value: { exitCode: 0, stdout: 'macbook\n', stderr: '' } }))

  const r = await $.command.run({ command: 'claims' })
  expect(r.text).toContain('CA: macbook (this machine)')
  expect(r.text).toContain('AL: mac-mini')
})

test('hook: allows write when state is owned by local machine', async ($, on) => {
  mock.store(on, {})
  on('fs.exists', () => ({ value: true }))
  on('fs.read', () => ({ value: SAMPLE_MD }))
  on('process.run', () => ({ value: { exitCode: 0, stdout: 'macbook\n', stderr: '' } }))
  on('tool.call', () => ({ result: 'written' }))

  const r = await $.tool.call({
    tool: 'Write',
    file_path: 'scripts/build-ca-tax.js',
    content: 'export const ca = true',
  })
  expect(r.result).toBe('written')
})

test('hook: refuses write when state is owned by other machine and prompt is refused', async ($, on) => {
  mock.store(on, {})
  on('fs.exists', () => ({ value: true }))
  on('fs.read', () => ({ value: SAMPLE_MD }))
  on('process.run', () => ({ value: { exitCode: 0, stdout: 'macbook\n', stderr: '' } }))

  on('tool.call', (_$: any, e: any) => {
    if (e.tool === 'AskUserQuestion') {
      return { result: { answers: { [e.questions[0].question]: 'Refuse the write' } } }
    }
    return { result: 'written' }
  })

  const r = await $.tool.call({
    tool: 'Write',
    file_path: 'scripts/build-al-tax.js',
    content: 'export const al = true',
  })
  expect(r.deny).toContain('owned by \'mac-mini\'')
})

test('hook: allows write when user overrides and logs override', async ($, on) => {
  mock.store(on, {})
  on('fs.exists', () => ({ value: true }))
  on('fs.read', () => ({ value: SAMPLE_MD }))
  on('process.run', () => ({ value: { exitCode: 0, stdout: 'macbook\n', stderr: '' } }))

  on('tool.call', (_$: any, e: any) => {
    if (e.tool === 'AskUserQuestion') {
      return { result: { answers: { [e.questions[0].question]: 'Allow this once (logged)' } } }
    }
    return { result: 'written' }
  })

  const r = await $.tool.call({
    tool: 'Write',
    file_path: 'scripts/build-al-tax.js',
    content: 'export const al = true',
  })
  expect(r.result).toBe('written')
})
