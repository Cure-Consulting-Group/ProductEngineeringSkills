import type { On } from 'claude-code'

import { formatLaneBoard, parseWorktreeList, type LaneInfo } from './lanes'

export function register(on: On) {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'lanes',
      description: 'Show status of active tri-lane worktrees, branches, live commits, and defect windows',
    })
    return next(e)
  })

  on('command.run', { command: 'lanes' }, async $ => {
    const lanes: LaneInfo[] = []
    const seenBranches = new Set<string>()

    // 1. Check worktrees
    const wtRes = await $.process.run(['git', 'worktree', 'list', '--porcelain'])
    if (wtRes && wtRes.exitCode === 0 && wtRes.stdout) {
      const entries = parseWorktreeList(wtRes.stdout)
      for (const entry of entries) {
        if (entry.branch && entry.branch.startsWith('lane/')) {
          seenBranches.add(entry.branch)

          let ahead = 0
          const aheadRes = await $.process.run(['git', 'rev-list', '--count', `origin/HEAD..${entry.branch}`])
          if (aheadRes && aheadRes.exitCode === 0 && aheadRes.stdout) {
            ahead = parseInt(aheadRes.stdout.trim(), 10) || 0
          }

          let dirty = 0
          const statusRes = await $.process.run(['git', '-C', entry.path, 'status', '--porcelain'])
          if (statusRes && statusRes.exitCode === 0 && statusRes.stdout) {
            dirty = statusRes.stdout.split('\n').filter((l: string) => l.trim().length > 0).length
          }

          lanes.push({
            name: entry.branch.replace(/^lane\//, ''),
            branch: entry.branch,
            path: entry.path,
            commitsAhead: ahead,
            dirtyCount: dirty,
            windowStatus: 'active',
          })
        }
      }
    }

    // 2. Check standalone lane branches not in worktrees
    const brRes = await $.process.run(['git', 'branch', '--list', 'lane/*'])
    if (brRes && brRes.exitCode === 0 && brRes.stdout) {
      const branchLines = brRes.stdout
        .split('\n')
        .map((l: string) => l.replace(/^[*+ ]/, '').trim())
        .filter((l: string) => l.startsWith('lane/') && !seenBranches.has(l))

      for (const b of branchLines) {
        let ahead = 0
        const aheadRes = await $.process.run(['git', 'rev-list', '--count', `origin/HEAD..${b}`])
        if (aheadRes && aheadRes.exitCode === 0 && aheadRes.stdout) {
          ahead = parseInt(aheadRes.stdout.trim(), 10) || 0
        }

        lanes.push({
          name: b.replace(/^lane\//, ''),
          branch: b,
          path: '(no worktree)',
          commitsAhead: ahead,
          dirtyCount: 0,
          windowStatus: 'pending',
        })
      }
    }

    return { text: formatLaneBoard(lanes) }
  })
}
