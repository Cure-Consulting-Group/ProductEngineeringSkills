/**
 * Pure functions for parsing git worktree lists and formatting tri-lane dashboard boards.
 */

export type WorktreeEntry = {
  path: string
  branch: string
  commit: string
}

export function parseWorktreeList(stdout: string): WorktreeEntry[] {
  if (!stdout || typeof stdout !== 'string') return []

  const entries: WorktreeEntry[] = []
  const blocks = stdout.split('\n\n')

  for (const block of blocks) {
    const lines = block.split('\n').map(l => l.trim())
    let path = ''
    let commit = ''
    let branch = ''

    for (const line of lines) {
      if (line.startsWith('worktree ')) {
        path = line.slice(9).trim()
      } else if (line.startsWith('HEAD ')) {
        commit = line.slice(5).trim().slice(0, 7)
      } else if (line.startsWith('branch ')) {
        const fullRef = line.slice(7).trim()
        branch = fullRef.replace(/^refs\/heads\//, '')
      }
    }

    if (path && (branch || commit)) {
      entries.push({ path, branch: branch || '(detached)', commit })
    }
  }

  return entries
}

export type LaneInfo = {
  name: string
  branch: string
  path: string
  commitsAhead: number
  dirtyCount: number
  windowStatus: string
}

export function formatLaneBoard(lanes: LaneInfo[]): string {
  if (lanes.length === 0) {
    return 'cure-lane-board: No active tri-lane branches or worktrees detected.'
  }

  const lines = [
    `cure-lane-board: ${lanes.length} active lane(s)`,
    '─'.repeat(70),
    '  Lane / Branch               Ahead   Dirty   Defect Window   Path',
    '─'.repeat(70),
  ]

  for (const lane of lanes) {
    const branchCol = (lane.branch || lane.name).padEnd(26).slice(0, 26)
    const aheadCol = `${lane.commitsAhead}c`.padEnd(8)
    const dirtyCol = lane.dirtyCount === 0 ? 'clean'.padEnd(8) : `${lane.dirtyCount} dirty`.padEnd(8)
    const windowCol = lane.windowStatus.padEnd(16)
    const shortPath = lane.path.split('/').slice(-2).join('/')

    lines.push(`  ${branchCol}  ${aheadCol}${dirtyCol}${windowCol}${shortPath}`)
  }

  lines.push('─'.repeat(70))
  return lines.join('\n')
}
