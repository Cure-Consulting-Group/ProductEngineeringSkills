import { expect, mock, test } from 'claude-code/testing'

import {
  detectEgressViolation,
  formatEgressReport,
  isProtectedRepo,
} from './egress'

// ── Pure unit tests ────────────────────────────────────────────────────────

test('isProtectedRepo: accurately flags PHI and minors repos', () => {
  expect(isProtectedRepo('Level5')).toBe(true)
  expect(isProtectedRepo('initiated-recruiting')).toBe(true)
  expect(isProtectedRepo('SPEDTECH')).toBe(true)
  expect(isProtectedRepo('LearnLift')).toBe(true)
  expect(isProtectedRepo('ProductEngineeringSkills')).toBe(false)
  expect(isProtectedRepo('Vendly')).toBe(false)
})

test('detectEgressViolation: flags consumer Gemini call in Level5', () => {
  const cmd = 'curl -X POST https://generativelanguage.googleapis.com/v1beta/models'
  const verdict = detectEgressViolation(cmd, 'Level5')
  expect(verdict.violated).toBe(true)
  expect(verdict.host).toBe('generativelanguage.googleapis.com')
  expect(verdict.reason).toContain('Level5 processes PHI')
})

test('detectEgressViolation: flags OpenAI call in initiated-recruiting', () => {
  const cmd = 'curl https://api.openai.com/v1/chat/completions'
  const verdict = detectEgressViolation(cmd, 'initiated-recruiting')
  expect(verdict.violated).toBe(true)
  expect(verdict.host).toBe('api.openai.com')
  expect(verdict.reason).toContain('minors\' or student data')
})

test('detectEgressViolation: exempts calls in non-protected repos', () => {
  const cmd = 'curl https://api.openai.com/v1/models'
  const verdict = detectEgressViolation(cmd, 'Vendly')
  expect(verdict.violated).toBe(false)
})

test('detectEgressViolation: allows benign outbound calls in protected repos', () => {
  const cmd = 'curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user'
  const verdict = detectEgressViolation(cmd, 'Level5')
  expect(verdict.violated).toBe(false)
})

test('formatEgressReport: reflects protected repository status', () => {
  const text = formatEgressReport('Level5')
  expect(text).toContain('PROTECTED')
  expect(text).toContain('api.openai.com')
})

// ── Hook end-to-end tests ──────────────────────────────────────────────────

test('command: /egress-guard displays repository status', async ($, on) => {
  mock.store(on, {})
  on('process.run', () => ({ value: { exitCode: 0, stdout: '/Users/r/Level5\n', stderr: '' } }))

  const r = await $.command.run({ command: 'egress-guard' })
  expect(r.text).toContain('PROTECTED')
  expect(r.text).toContain('Level5')
})

test('hook: blocks bash curl to OpenAI in Level5 when refused', async ($, on) => {
  mock.store(on, {})
  on('process.run', () => ({ value: { exitCode: 0, stdout: '/Users/r/Level5\n', stderr: '' } }))

  on('tool.call', (_$: any, e: any) => {
    if (e.tool === 'AskUserQuestion') {
      return { result: { answers: { [e.questions[0].question]: 'Refuse the request' } } }
    }
    return { result: 'ran' }
  })

  const r = await $.tool.call({
    tool: 'Bash',
    command: 'curl -X POST https://api.openai.com/v1/chat/completions -d @data.json',
  })

  expect(r.deny).toContain('Blocked by cure-egress-guard')
  expect(r.deny).toContain('Level5 processes PHI')
})

test('hook: allows bash curl when user overrides and logs override', async ($, on) => {
  mock.store(on, {})
  on('process.run', () => ({ value: { exitCode: 0, stdout: '/Users/r/Level5\n', stderr: '' } }))

  on('tool.call', (_$: any, e: any) => {
    if (e.tool === 'AskUserQuestion') {
      return { result: { answers: { [e.questions[0].question]: 'Allow this once (logged)' } } }
    }
    return { result: 'ran' }
  })

  const r = await $.tool.call({
    tool: 'Bash',
    command: 'curl -X POST https://api.openai.com/v1/chat/completions -d @data.json',
  })

  expect(r.result).toBe('ran')
})

test('hook: allows benign bash curl in protected repo', async ($, on) => {
  mock.store(on, {})
  on('process.run', () => ({ value: { exitCode: 0, stdout: '/Users/r/Level5\n', stderr: '' } }))
  on('tool.call', () => ({ result: 'ok' }))

  const r = await $.tool.call({
    tool: 'Bash',
    command: 'curl https://api.github.com/zen',
  })

  expect(r.result).toBe('ok')
})
