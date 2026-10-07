import { expect, mock, test } from 'claude-code/testing'

import { scrubText, scrubToolOutput, SECRET_RULES } from './scrub'

// ── Pure unit tests ────────────────────────────────────────────────────────

test('scrubText: redacts Google API key', () => {
  const key = 'AIza' + 'SyBHDe0123456789abcdefghijklmnopqrs'
  const res = scrubText(`const API_KEY = "${key}";`)
  expect(res.count).toBe(1)
  expect(res.kinds).toContain('Google API key')
  expect(res.text).toBe('const API_KEY = "[REDACTED:GOOGLE_API_KEY]";')
})

test('scrubText: redacts Anthropic API key', () => {
  const key = 'sk-ant-api03-' + 'a'.repeat(30) + 'xyz'
  const res = scrubText(`export ANTHROPIC_API_KEY="${key}"`)
  expect(res.count).toBe(1)
  expect(res.kinds).toContain('Anthropic API key')
  expect(res.text).toBe('export ANTHROPIC_API_KEY="[REDACTED:ANTHROPIC_API_KEY]"')
})

test('scrubText: redacts OpenAI API key', () => {
  const key = 'sk-proj-' + 'a'.repeat(45)
  const res = scrubText(`apiKey: '${key}'`)
  expect(res.count).toBe(1)
  expect(res.kinds).toContain('OpenAI API key')
  expect(res.text).toBe("apiKey: '[REDACTED:OPENAI_API_KEY]'")
})

test('scrubText: redacts GitHub personal access tokens', () => {
  const ghp = 'ghp_' + 'a'.repeat(36)
  const pat = 'github_pat_' + 'b'.repeat(45)
  const res = scrubText(`token1: ${ghp}, token2: ${pat}`)
  expect(res.count).toBe(2)
  expect(res.kinds).toContain('GitHub token')
  expect(res.text).toBe('token1: [REDACTED:GITHUB_TOKEN], token2: [REDACTED:GITHUB_TOKEN]')
})

test('scrubText: redacts Stripe live secret keys', () => {
  const stripe = 'sk_live_' + '1234567890abcdefghijklmn'
  const res = scrubText(`stripe.apiKey = '${stripe}';`)
  expect(res.count).toBe(1)
  expect(res.kinds).toContain('Stripe secret key')
  expect(res.text).toBe("stripe.apiKey = '[REDACTED:STRIPE_SECRET_KEY]';")
})

test('scrubText: redacts AWS access key ID', () => {
  const aws = 'AKIA' + 'IOSFODNN7EXAMPLE'
  const res = scrubText(`AWS_ACCESS_KEY_ID=${aws}`)
  expect(res.count).toBe(1)
  expect(res.kinds).toContain('AWS access key')
  expect(res.text).toBe('AWS_ACCESS_KEY_ID=[REDACTED:AWS_ACCESS_KEY]')
})

test('scrubText: redacts PEM private key blocks', () => {
  const pem = '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n-----END RSA PRIVATE KEY-----'
  const res = scrubText(`Host key:\n${pem}\nDone.`)
  expect(res.count).toBe(1)
  expect(res.kinds).toContain('Private key block')
  expect(res.text).toBe('Host key:\n[REDACTED:PRIVATE_KEY_BLOCK]\nDone.')
})

test('scrubText: redacts GCP service account private key fields in json', () => {
  const sa = '{\n  "type": "service_account",\n  "private_key": "-----BEGIN PRIVATE KEY-----\\nabc\\n-----END PRIVATE KEY-----"\n}'
  const res = scrubText(sa)
  expect(res.count).toBeGreaterThanOrEqual(1)
  expect(res.text).toContain('[REDACTED:')
})

test('scrubText: benign text passes unmodified', () => {
  const input = 'This is normal code without credentials.\nconst a = 42;'
  const res = scrubText(input)
  expect(res.count).toBe(0)
  expect(res.kinds).toEqual([])
  expect(res.text).toBe(input)
})

test('scrubToolOutput: recursively traverses nested objects and arrays', () => {
  const google = 'AIza' + 'SyBHDe0123456789abcdefghijklmnopqrs'
  const payload = {
    stdout: `Found key: ${google}`,
    meta: {
      items: [`export KEY=${google}`, 'benign'],
    },
  }
  const { output, count, kinds } = scrubToolOutput(payload)
  expect(count).toBe(2)
  expect(kinds).toContain('Google API key')
  expect(output.stdout).toBe('Found key: [REDACTED:GOOGLE_API_KEY]')
  expect(output.meta.items[0]).toBe('export KEY=[REDACTED:GOOGLE_API_KEY]')
  expect(output.meta.items[1]).toBe('benign')
})

// ── Hook end-to-end tests ──────────────────────────────────────────────────

test('hook: scrubs Read output containing secrets', async ($, on) => {
  mock.store(on, {})
  const key = 'AIza' + 'SyBHDe0123456789abcdefghijklmnopqrs'
  on('tool.call', () => ({
    result: `// Config\nconst KEY = '${key}'\n`,
  }))

  const r = await $.tool.call({ tool: 'Read', file_path: '/repo/.env.backup' })
  expect(r.result).toBe("// Config\nconst KEY = '[REDACTED:GOOGLE_API_KEY]'\n")
})

test('hook: scrubs Grep output containing secrets', async ($, on) => {
  mock.store(on, {})
  const ghp = 'ghp_' + 'a'.repeat(36)
  on('tool.call', () => ({
    result: 'ok',
    text: `src/config.ts:12: const token = "${ghp}"`,
  }))

  const r = await $.tool.call({ tool: 'Grep', query: 'token' })
  expect(r.text).toBe('src/config.ts:12: const token = "[REDACTED:GITHUB_TOKEN]"')
})

test('hook: scrubs Bash stdout containing secrets', async ($, on) => {
  mock.store(on, {})
  const key = 'sk-ant-api03-' + 'a'.repeat(30) + 'xyz'
  on('tool.call', () => ({
    result: 'ok',
    stdout: `export ANTHROPIC_API_KEY="${key}"\n`,
    stderr: '',
  }))

  const r = await $.tool.call({ tool: 'Bash', command: 'env' })
  expect(r.stdout).toBe('export ANTHROPIC_API_KEY="[REDACTED:ANTHROPIC_API_KEY]"\n')
})

test('hook: passes non-scrub tool untouched', async ($, on) => {
  mock.store(on, {})
  const key = 'AIza' + 'SyBHDe0123456789abcdefghijklmnopqrs'
  on('tool.call', () => ({
    result: `wrote ${key}`,
  }))

  const r = await $.tool.call({ tool: 'Write', file_path: '/repo/a.txt', content: key })
  expect(r.result).toBe(`wrote ${key}`)
})

test('command: /secret-scrub before redaction reports no credentials', async ($, on) => {
  mock.store(on, {})
  const r = await $.command.run({ command: 'secret-scrub' })
  expect(r.text).toContain('No credentials have been redacted')
})

test('command: /secret-scrub after redaction reports counts', async ($, on) => {
  mock.store(on, {})
  const key = 'AIza' + 'SyBHDe0123456789abcdefghijklmnopqrs'
  on('tool.call', () => ({ result: `KEY=${key}` }))

  await $.tool.call({ tool: 'Read', file_path: '/repo/config.json' })
  const r = await $.command.run({ command: 'secret-scrub' })
  expect(r.text).toContain('Redacted 1 credential(s)')
  expect(r.text).toContain('Google API key: 1')
})
