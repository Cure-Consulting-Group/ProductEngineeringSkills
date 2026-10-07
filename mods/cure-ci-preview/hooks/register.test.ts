import { expect, mock, test } from 'claude-code/testing'

import { classifyChanges, formatCiPreview } from './preview'

// ── Pure unit tests ────────────────────────────────────────────────────────

test('classifyChanges: docs-only changes skip heavy runners', () => {
  const preview = classifyChanges(['README.md', 'docs/ARCHITECTURE.md', 'design/tokens.json'])
  expect(preview.jobs).toContain('Docs Quick-Lint / Skip')
  expect(preview.estimatedCostUsd).toBe(0)
  expect(preview.warning).toBeUndefined()
})

test('classifyChanges: code changes trigger Linux runner', () => {
  const preview = classifyChanges(['src/index.ts', 'src/api.ts'])
  expect(preview.jobs).toContain('Linux Runner (Test & Validate Matrix)')
  expect(preview.estimatedMinutes).toBe(15)
  expect(preview.estimatedCostUsd).toBe(0.12)
})

test('classifyChanges: iOS changes trigger macOS runner', () => {
  const preview = classifyChanges(['ios/App/ViewController.swift', 'Podfile'])
  expect(preview.jobs).toContain('macOS Runner (iOS Matrix)')
  expect(preview.estimatedMinutes).toBe(15)
  expect(preview.estimatedCostUsd).toBe(0.24)
})

test('classifyChanges: mixed docs and code generates warning', () => {
  const preview = classifyChanges(['.agents/notes.md', 'src/server.ts'])
  expect(preview.warning).toContain('loses docs-only skip optimization')
  expect(preview.jobs).toContain('Linux Runner (Test & Validate Matrix)')
})

test('classifyChanges: full stack changes accumulate runner costs', () => {
  const preview = classifyChanges(['ios/App.swift', 'src/backend.ts'])
  expect(preview.jobs.length).toBe(2)
  expect(preview.estimatedMinutes).toBe(30)
  expect(preview.estimatedCostUsd).toBe(0.36) // 0.24 + 0.12
})

test('formatCiPreview: includes jobs and warning', () => {
  const text = formatCiPreview({
    jobs: ['Linux Runner (Test & Validate Matrix)'],
    estimatedMinutes: 15,
    estimatedCostUsd: 0.12,
    warning: 'Mixed docs and code',
  })
  expect(text).toContain('~15 billed min')
  expect(text).toContain('~$0.12')
  expect(text).toContain('⚠️  Mixed docs and code')
})

// ── Hook end-to-end tests ──────────────────────────────────────────────────

test('command: /ci-preview returns classification based on git diff', async ($, on) => {
  mock.store(on, {})
  on('process.run', (_$: any, e: any) => {
    if (e.argv && e.argv.includes('origin/HEAD...HEAD')) {
      return { value: { exitCode: 0, stdout: 'README.md\ndocs/specs.md\n', stderr: '' } }
    }
    return { value: { exitCode: 0, stdout: '', stderr: '' } }
  })

  const r = await $.command.run({ command: 'ci-preview' })
  expect(r.text).toContain('Docs Quick-Lint / Skip')
  expect(r.text).toContain('$0.00')
})

test('hook: intercepts git push and shows toast preview', async ($, on) => {
  mock.store(on, {})
  on('process.run', (_$: any, e: any) => {
    if (e.argv && e.argv.includes('origin/HEAD...HEAD')) {
      return { value: { exitCode: 0, stdout: 'src/app.ts\n', stderr: '' } }
    }
    return { value: { exitCode: 0, stdout: 'pushed', stderr: '' } }
  })
  on('tool.call', () => ({ result: 'pushed to origin' }))

  const r = await $.tool.call({ tool: 'Bash', command: 'git push origin main' })
  expect(r.result).toBe('pushed to origin')
})

test('hook: benign bash command is not intercepted for git diff', async ($, on) => {
  mock.store(on, {})
  on('tool.call', () => ({ result: 'output' }))

  const r = await $.tool.call({ tool: 'Bash', command: 'ls -la' })
  expect(r.result).toBe('output')
})
