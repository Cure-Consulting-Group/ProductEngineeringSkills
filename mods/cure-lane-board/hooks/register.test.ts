import { expect, mock, test } from 'claude-code/testing'

import { formatLaneBoard, parseWorktreeList } from './lanes'

// ── Pure unit tests ────────────────────────────────────────────────────────

const SAMPLE_WORKTREE_PORCELAIN = `worktree /Users/r/repo
HEAD a1b2c3d4e5f6
branch refs/heads/main

worktree /Users/r/repo/.worktrees/bw-tests
HEAD 9f8e7d6c5b4a
branch refs/heads/lane/bw-tests

worktree /Users/r/repo/.worktrees/detached
HEAD 1234567890ab
detached
`

test('parseWorktreeList: parses git worktree list porcelain output', () => {
  const entries = parseWorktreeList(SAMPLE_WORKTREE_PORCELAIN)
  expect(entries.length).toBe(3)
  expect(entries[0].branch).toBe('main')
  expect(entries[0].commit).toBe('a1b2c3d')
  expect(entries[1].branch).toBe('lane/bw-tests')
  expect(entries[1].path).toBe('/Users/r/repo/.worktrees/bw-tests')
  expect(entries[2].branch).toBe('(detached)')
})

test('formatLaneBoard: formats clean dashboard table', () => {
  const board = formatLaneBoard([
    {
      name: 'bw-tests',
      branch: 'lane/bw-tests',
      path: '/Users/r/repo/.worktrees/bw-tests',
      commitsAhead: 3,
      dirtyCount: 0,
      windowStatus: 'active',
    },
    {
      name: 'refactor',
      branch: 'lane/refactor',
      path: '/Users/r/repo/.worktrees/refactor',
      commitsAhead: 1,
      dirtyCount: 2,
      windowStatus: 'active',
    },
  ])

  expect(board).toContain('2 active lane(s)')
  expect(board).toContain('lane/bw-tests')
  expect(board).toContain('3c')
  expect(board).toContain('clean')
  expect(board).toContain('lane/refactor')
  expect(board).toContain('2 dirty')
})

test('formatLaneBoard: handles empty lanes', () => {
  const board = formatLaneBoard([])
  expect(board).toContain('No active tri-lane branches')
})

// ── Hook end-to-end tests ──────────────────────────────────────────────────

test('command: /lanes reports no active lanes when git has none', async ($, on) => {
  mock.store(on, {})
  on('process.run', (_$: any, e: any) => {
    if (e.argv && e.argv.includes('worktree')) {
      return { value: { exitCode: 0, stdout: 'worktree /repo\nHEAD abc\nbranch refs/heads/main\n', stderr: '' } }
    }
    if (e.argv && e.argv.includes('branch')) {
      return { value: { exitCode: 0, stdout: '', stderr: '' } }
    }
    return { value: { exitCode: 0, stdout: '', stderr: '' } }
  })

  const r = await $.command.run({ command: 'lanes' })
  expect(r.text).toContain('No active tri-lane branches')
})

test('command: /lanes renders active worktree lanes', async ($, on) => {
  mock.store(on, {})
  on('process.run', (_$: any, e: any) => {
    const cmd = e.argv.join(' ')
    if (cmd.includes('worktree list')) {
      return { value: { exitCode: 0, stdout: SAMPLE_WORKTREE_PORCELAIN, stderr: '' } }
    }
    if (cmd.includes('rev-list --count')) {
      return { value: { exitCode: 0, stdout: '4\n', stderr: '' } }
    }
    if (cmd.includes('status --porcelain')) {
      return { value: { exitCode: 0, stdout: '', stderr: '' } }
    }
    if (cmd.includes('branch --list')) {
      return { value: { exitCode: 0, stdout: '', stderr: '' } }
    }
    return { value: { exitCode: 0, stdout: '', stderr: '' } }
  })

  const r = await $.command.run({ command: 'lanes' })
  expect(r.text).toContain('1 active lane(s)')
  expect(r.text).toContain('lane/bw-tests')
  expect(r.text).toContain('4c')
  expect(r.text).toContain('clean')
})
