import { expect, mock, test } from 'claude-code/testing'

import { formatHandoffDraft } from './handoff'

// ── Pure unit tests ────────────────────────────────────────────────────────

test('formatHandoffDraft: formats draft with commits and clean status', () => {
  const draft = formatHandoffDraft({
    date: '2026-10-07',
    branch: 'feat/new-mods',
    commits: ['a1b2c3d feat: add secret scrub', 'e4f5g6h fix: update regex'],
    dirtyFiles: [],
  })

  expect(draft).toContain('### Handoff: 2026-10-07 (feat/new-mods)')
  expect(draft).toContain('**Shipped Commits:**')
  expect(draft).toContain('- a1b2c3d feat: add secret scrub')
  expect(draft).toContain('Clean (no uncommitted diffs)')
})

test('formatHandoffDraft: handles dirty files and no commits', () => {
  const draft = formatHandoffDraft({
    date: '2026-10-07',
    branch: 'main',
    commits: [],
    dirtyFiles: ['src/app.ts', 'docs/notes.md'],
  })

  expect(draft).toContain('- (No recent commits recorded on this branch)')
  expect(draft).toContain('2 uncommitted file(s):')
  expect(draft).toContain('• src/app.ts')
})

// ── Hook end-to-end tests ──────────────────────────────────────────────────

test('command: /handoff gathers git status and returns draft', async ($, on) => {
  mock.store(on, {})
  on('process.run', (_$: any, e: any) => {
    const cmd = e.argv.join(' ')
    if (cmd.includes('rev-parse --abbrev-ref')) {
      return { value: { exitCode: 0, stdout: 'feat/test-branch\n', stderr: '' } }
    }
    if (cmd.includes('log -n 5')) {
      return { value: { exitCode: 0, stdout: 'c0ffee1 feat: initial commit\n', stderr: '' } }
    }
    if (cmd.includes('status --porcelain')) {
      return { value: { exitCode: 0, stdout: ' M package.json\n', stderr: '' } }
    }
    return { value: { exitCode: 0, stdout: '', stderr: '' } }
  })

  const r = await $.command.run({ command: 'handoff' })
  expect(r.text).toContain('feat/test-branch')
  expect(r.text).toContain('c0ffee1 feat: initial commit')
  expect(r.text).toContain('package.json')
})
