import { expect, mock, test } from 'claude-code/testing'

import {
  applyQueuePositions,
  foldSalvage,
  formatLaneBoard,
  parseGitHubRemote,
  parsePullList,
  parseWorktreeList,
  type LaneInfo,
  type PullInfo,
} from './lanes'

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

test('parsePullList: tallies completed, failed, pending and skipped checks', () => {
  const pulls = parsePullList(
    JSON.stringify([
      {
        number: 510,
        headRefName: 'feat/topic-pages-design',
        title: 'feat(topic-pages): the six topic templates',
        mergeStateStatus: 'CLEAN',
        statusCheckRollup: [
          { status: 'COMPLETED', conclusion: 'SUCCESS' },
          { status: 'COMPLETED', conclusion: 'FAILURE' },
          { status: 'IN_PROGRESS', conclusion: null },
          { status: 'COMPLETED', conclusion: 'NEUTRAL' },
          { status: 'COMPLETED', conclusion: 'SKIPPED' },
        ],
      },
    ]),
  )

  expect(pulls[0].checks).toEqual({ pass: 1, fail: 1, pending: 2 })
  expect(pulls[0].state).toBe('CLEAN')
  expect(pulls[0].queue).toBe(null)
})

test('applyQueuePositions: maps merge queue positions by pull request number', () => {
  const pulls = parsePullList('[{"number":510,"headRefName":"feat/x","title":"x","mergeStateStatus":"CLEAN","statusCheckRollup":[]},{"number":499,"headRefName":"docs/x","title":"x","mergeStateStatus":"CLEAN","statusCheckRollup":[]}]')
  applyQueuePositions(
    pulls,
    '{"data":{"repository":{"mergeQueue":{"entries":{"nodes":[{"position":1,"pullRequest":{"number":510}}]}}}}}',
  )

  expect(pulls[0].queue).toBe(1)
  expect(pulls[1].queue).toBe(null)
})

test('foldSalvage: folds a salvage twin and leaves an orphan visible', () => {
  const lane = (branch: string, path: string): LaneInfo => ({
    name: branch.replace(/^lane\//, ''),
    branch,
    path,
    commitsAhead: 0,
    dirtyCount: 0,
    windowStatus: branch === 'lane/topic' ? 'merged' : 'pending',
    merged: branch === 'lane/topic',
  })

  const folded = foldSalvage([
    lane('lane/topic', '(no worktree)'),
    lane('lane/topic-salvage', '(no worktree)'),
    lane('lane/orphan-salvage', '(no worktree)'),
  ])

  expect(folded.map(row => row.branch)).toEqual(['lane/topic', 'lane/orphan-salvage'])
  expect(folded[0].path).toBe('(no worktree) +salvage')
  expect(folded[1].salvageOf).toBe('lane/orphan')
})

test('parseGitHubRemote: handles ssh and https origin URLs', () => {
  expect(parseGitHubRemote('git@github.com:o/r.git')).toEqual({ owner: 'o', repo: 'r' })
  expect(parseGitHubRemote('https://github.com/o/r.git')).toEqual({ owner: 'o', repo: 'r' })
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
      merged: false,
    },
    {
      name: 'refactor',
      branch: 'lane/refactor',
      path: '/Users/r/repo/.worktrees/refactor',
      commitsAhead: 1,
      dirtyCount: 2,
      windowStatus: 'active',
      merged: false,
    },
  ])

  expect(board).toContain('2 lane(s) (0 merged) · 0 open PR(s)')
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

test('formatLaneBoard: prints merged lanes, pull requests and notes', () => {
  const pulls: PullInfo[] = [
    {
      number: 510,
      branch: 'feat/topic-pages-design',
      title: 'feat(topic-pages): the six topic templates',
      state: 'CLEAN',
      checks: { pass: 11, fail: 0, pending: 0 },
      queue: 1,
    },
    {
      number: 499,
      branch: 'docs/operation-deep-blue-sea',
      title: 'docs(strategy): Operation Deep Blue Sea',
      state: 'CLEAN',
      checks: { pass: 9, fail: 0, pending: 0 },
      queue: null,
    },
  ]
  const board = formatLaneBoard(
    [
      {
        name: 'done',
        branch: 'lane/done',
        path: '(no worktree) +salvage',
        commitsAhead: 0,
        dirtyCount: 0,
        windowStatus: 'merged',
        merged: true,
      },
    ],
    pulls,
    ['could not verify merged state (origin/HEAD unset)'],
  )

  expect(board).toContain('1 lane(s) (1 merged) · 2 open PR(s)')
  expect(board).toContain('merged')
  expect(board).toContain('+salvage')
  expect(board).toContain('Pull requests (open): 2')
  expect(board).toContain('checks 11 pass · 0 fail · 0 pending')
  expect(board).toContain('queue #1')
  expect(board).toContain('—')
  expect(board).toContain('could not verify merged state (origin/HEAD unset)')
  for (const line of board.split('\n')) expect(line.length).toBeLessThanOrEqual(100)
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
  expect(r.text).toContain('1 lane(s) (0 merged) · 0 open PR(s)')
  expect(r.text).toContain('lane/bw-tests')
  expect(r.text).toContain('4c')
  expect(r.text).toContain('clean')
})

test('command: /lanes folds merged salvage lanes and renders pull request queue data', async ($, on) => {
  mock.store(on, {})
  on('process.run', (_$: any, e: any) => {
    const cmd = e.argv.join(' ')
    if (cmd.includes('branch --merged')) {
      return { value: { exitCode: 0, stdout: '  lane/done\n  lane/done-salvage\n', stderr: '' } }
    }
    if (cmd.includes('worktree list')) {
      return { value: { exitCode: 0, stdout: 'worktree /repo\nHEAD abc\nbranch refs/heads/main\n', stderr: '' } }
    }
    if (cmd.includes('branch --list')) {
      return { value: { exitCode: 0, stdout: '  lane/done\n  lane/done-salvage\n', stderr: '' } }
    }
    if (cmd.includes('rev-list --count')) {
      return { value: { exitCode: 0, stdout: '0\n', stderr: '' } }
    }
    if (cmd.includes('gh pr list')) {
      return {
        value: {
          exitCode: 0,
          stdout: '[{"number":510,"headRefName":"feat/topic-pages-design","title":"feat(topic-pages): the six topic templates","mergeStateStatus":"CLEAN","statusCheckRollup":[]}]',
          stderr: '',
        },
      }
    }
    if (cmd.includes('remote get-url')) {
      return { value: { exitCode: 0, stdout: 'git@github.com:o/r.git\n', stderr: '' } }
    }
    if (cmd.includes('gh api graphql')) {
      return { value: { exitCode: 0, stdout: '{"data":{"repository":{"mergeQueue":{"entries":{"nodes":[{"position":1,"pullRequest":{"number":510}}]}}}}}', stderr: '' } }
    }
    return { value: { exitCode: 0, stdout: '', stderr: '' } }
  })

  const r = await $.command.run({ command: 'lanes' })
  expect(r.text).toContain('1 lane(s) (1 merged)')
  expect(r.text).toContain('merged')
  expect(r.text).toContain('+salvage')
  expect(r.text).toContain('queue #1')
})

test('command: /lanes reports unavailable gh without throwing', async ($, on) => {
  mock.store(on, {})
  on('process.run', (_$: any, e: any) => {
    if (e.argv[0] === 'gh') return { value: { exitCode: 1, stdout: '', stderr: 'gh not found' } }
    return { value: { exitCode: 0, stdout: '', stderr: '' } }
  })

  const r = await $.command.run({ command: 'lanes' })
  expect(r.text).toContain('pull requests: could not verify (gh unavailable)')
})
