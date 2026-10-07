import { expect, mock, test } from 'claude-code/testing'

import { addedText, check, parentDirs, type Write } from './rules'

const w = (over: Partial<Write>): Write => ({
  path: '/r/x.ts',
  repo: 'cure-finops-watchdog',
  added: '',
  deps: [],
  ...over,
})
const rules = (over: Partial<Write>) => check(w(over)).map(v => v.rule)

// ── rules, as pure functions ───────────────────────────────────────────────

test('no-cron: a schedule trigger in a workflow is a violation', async () => {
  expect(rules({ path: '/r/.github/workflows/ci.yml', added: 'on:\n  schedule:\n    - cron: "0 3 * * *"\n' })).toEqual(['no-cron'])
  expect(rules({ path: '/r/.github/workflows/ci.yaml', added: 'on:\n  schedule:\n' })).toEqual(['no-cron'])
})

test('no-cron: the word outside a workflow, or a workflow without the trigger, passes', async () => {
  expect(rules({ path: '/r/docs/notes.md', added: 'schedule: weekly' })).toEqual([])
  expect(rules({ path: '/r/.github/workflows/ci.yml', added: 'on:\n  push:\n# no schedule here\n' })).toEqual([])
})

test('level5-vertex-only: consumer Gemini paths are refused only in Level5', async () => {
  for (const added of [
    "import { GoogleGenerativeAI } from '@google/generative-ai'",
    'const url = "https://generativelanguage.googleapis.com/v1beta/models"',
    'const key = process.env.GEMINI_API_KEY',
  ]) {
    expect(rules({ repo: 'Level5', added })).toEqual(['level5-vertex-only'])
    expect(rules({ repo: 'Vendly', added })).toEqual([])
  }
  expect(rules({ repo: 'Level5', added: "import { VertexAI } from '@google-cloud/vertexai'" })).toEqual([])
})

test('minors-new-ai-vendor: a new vendor import in a minors repo is a violation', async () => {
  expect(rules({ repo: 'initiated-recruiting', added: "import OpenAI from 'openai'" })).toEqual(['minors-new-ai-vendor'])
  expect(rules({ repo: 'SPEDTECH', added: "const A = require('@anthropic-ai/sdk')" })).toEqual(['minors-new-ai-vendor'])
  expect(rules({ repo: 'LearnLift', added: "import { x } from '@google/genai/node'" })).toEqual(['minors-new-ai-vendor'])
})

test('minors-new-ai-vendor: an existing dependency, other repos, and non-AI imports pass', async () => {
  expect(rules({ repo: 'initiated-recruiting', added: "import { GoogleGenerativeAI } from '@google/generative-ai'", deps: ['@google/generative-ai'] })).toEqual([])
  expect(rules({ repo: 'DistrictZero', added: "import OpenAI from 'openai'" })).toEqual([])
  expect(rules({ repo: 'SPEDTECH', added: "import { z } from 'zod'\nimport fs from 'node:fs'" })).toEqual([])
})

test('hardcoded-secret: credential literals are violations, .env files are exempt', async () => {
  const google = 'AIza' + 'SyBHDe0123456789abcdefghijklmnopqrs'
  expect(rules({ path: '/r/scripts/fix.js', added: `const KEY = '${google}'` })).toEqual(['hardcoded-secret'])
  expect(rules({ path: '/r/.env', added: `GEMINI=${google}` })).toEqual([])
  expect(rules({ path: '/r/.env.local', added: `GEMINI=${google}` })).toEqual([])
  expect(rules({ path: '/r/sa.json', added: '{ "private_key": "-----BEGIN PRIVATE KEY-----\\nabc" }' })).toEqual(['hardcoded-secret'])
  expect(rules({ path: '/r/a.ts', added: 'const t = "ghp_' + 'a'.repeat(36) + '"' })).toEqual(['hardcoded-secret'])
  expect(rules({ path: '/r/a.ts', added: 'const k = process.env.GEMINI_KEY' })).toEqual([])
})

test('several rules can fire on one write', async () => {
  const google = 'AIza' + 'SyBHDe0123456789abcdefghijklmnopqrs'
  expect(rules({ repo: 'Level5', path: '/r/a.ts', added: `import { G } from '@google/generative-ai'\nconst k = '${google}'` })).toEqual([
    'level5-vertex-only',
    'hardcoded-secret',
  ])
})

test('addedText reads only what each file tool adds', async () => {
  expect(addedText({ tool: 'Write', content: 'A' })).toBe('A')
  expect(addedText({ tool: 'Edit', old_string: 'OLD', new_string: 'NEW' })).toBe('NEW')
  expect(addedText({ tool: 'MultiEdit', edits: [{ old_string: 'o', new_string: 'n1' }, { new_string: 'n2' }] })).toBe('n1\nn2')
  expect(addedText({ tool: 'Bash', command: 'echo AIza' })).toBe('')
})

test('parentDirs walks up to the root, nearest first', async () => {
  expect(parentDirs('/a/b/c.ts')).toEqual(['/a/b', '/a', '/'])
})

// ── the hook, end to end ───────────────────────────────────────────────────

const WORKFLOW = { tool: 'Write', file_path: '/repo/.github/workflows/nightly.yml', content: 'on:\n  schedule:\n    - cron: "0 3 * * *"\n' }

/** Answers the guard's question with `label`, or refuses to answer (dismissed / headless). */
const answering = (label: string | undefined) => (_$: any, e: any) => {
  if (e.tool === 'AskUserQuestion') {
    return label === undefined ? { deny: 'non-interactive' } : { result: { answers: { [e.questions[0].question]: label } } }
  }
  return { result: 'written' }
}

const stubRepo = (on: any, repo = 'cure-finops-watchdog') => {
  on('fs.exists', () => ({ value: false }))
  on('process.run', () => ({ value: { exitCode: 1, stdout: '', stderr: '' } }))
  return repo
}

test('a clean write goes through untouched', async ($, on) => {
  stubRepo(on)
  on('tool.call', () => ({ result: 'written' }))
  const r = await $.tool.call({ tool: 'Write', file_path: '/repo/src/a.ts', content: 'export const a = 1' })
  expect(r.result).toBe('written')
})

test('a violating write is denied when the person refuses', async ($, on) => {
  stubRepo(on)
  on('tool.call', answering('Refuse the write'))
  const r = await $.tool.call(WORKFLOW)
  expect(r.deny).toMatch(/no-cron/)
  expect(r.result).toBeUndefined()
})

test('a violating write is denied when nobody can be asked', async ($, on) => {
  stubRepo(on)
  on('tool.call', answering(undefined))
  const r = await $.tool.call(WORKFLOW)
  expect(r.deny).toMatch(/nobody could be asked/)
})

test('an override lets the write through and is recorded', async ($, on) => {
  stubRepo(on)
  mock.store(on, {})
  mock.clock(on, { now: Date.UTC(2026, 9, 5, 12) })
  on('tool.call', answering('Allow this once (logged)'))
  const r = await $.tool.call(WORKFLOW)
  expect(r.result).toBe('written')
  // The record is read back the way the person reads it: /policy-guard.
  const shown = await $.command.run({ command: 'policy-guard' })
  expect(shown.text).toMatch(/Recent overrides:/)
  expect(shown.text).toMatch(/no-cron/)
  expect(shown.text).toContain(WORKFLOW.file_path)
})

test('/policy-guard says so when nothing was overridden', async ($, on) => {
  mock.store(on, {})
  const shown = await $.command.run({ command: 'policy-guard' })
  expect(shown.text).toMatch(/No overrides recorded/)
})

test('other tools are never inspected', async ($, on) => {
  stubRepo(on)
  on('tool.call', (_$: any, e: any) => {
    if (e.tool === 'AskUserQuestion') throw new Error('must not ask')
    return { result: 'ran' }
  })
  const r = await $.tool.call({ tool: 'Bash', command: 'echo "schedule:" > .github/workflows/x.yml' })
  expect(r.result).toBe('ran')
})

test('an Edit that adds a violation is guarded like a Write', async ($, on) => {
  stubRepo(on)
  on('tool.call', answering('Refuse the write'))
  const r = await $.tool.call({
    tool: 'Edit',
    file_path: '/repo/.github/workflows/ci.yml',
    old_string: 'on:\n  push:',
    new_string: 'on:\n  push:\n  schedule:\n    - cron: "0 * * * *"',
  })
  expect(r.deny).toMatch(/no-cron/)
})

test('an Edit that only removes a violation goes through', async ($, on) => {
  stubRepo(on)
  on('tool.call', answering(undefined))
  const r = await $.tool.call({ tool: 'Edit', file_path: '/repo/.github/workflows/ci.yml', old_string: '  schedule:\n', new_string: '' })
  expect(r.result).toBe('written')
})
