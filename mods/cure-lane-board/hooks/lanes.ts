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
  merged: boolean
  salvageOf?: string
}

export type PullInfo = {
  number: number
  branch: string
  title: string
  state: string
  checks: { pass: number; fail: number; pending: number }
  queue: number | null
}

const FAILED_CONCLUSIONS = new Set(['FAILURE', 'TIMED_OUT', 'CANCELLED', 'ACTION_REQUIRED'])

export function parsePullList(json: string): PullInfo[] {
  try {
    const parsed: unknown = JSON.parse(json)
    if (!Array.isArray(parsed)) return []

    return parsed
      .filter((pull): pull is Record<string, unknown> => Boolean(pull) && typeof pull === 'object')
      .map(pull => {
        const checks = { pass: 0, fail: 0, pending: 0 }
        const rollup = Array.isArray(pull.statusCheckRollup) ? pull.statusCheckRollup : []

        for (const item of rollup) {
          if (!item || typeof item !== 'object') {
            checks.pending++
            continue
          }

          const check = item as Record<string, unknown>
          if (typeof check.state === 'string') {
            const state = check.state.toUpperCase()
            if (state === 'SUCCESS') {
              checks.pass++
            } else if (state === 'FAILURE' || state === 'ERROR') {
              checks.fail++
            } else {
              checks.pending++
            }
            continue
          }

          const conclusion = typeof check.conclusion === 'string' ? check.conclusion.toUpperCase() : ''
          const status = typeof check.status === 'string' ? check.status.toUpperCase() : ''

          if (conclusion === 'SKIPPED') continue
          if (status !== 'COMPLETED') {
            checks.pending++
          } else if (conclusion === 'SUCCESS') {
            checks.pass++
          } else if (FAILED_CONCLUSIONS.has(conclusion)) {
            checks.fail++
          } else {
            checks.pending++
          }
        }

        return {
          number: typeof pull.number === 'number' ? pull.number : Number(pull.number) || 0,
          branch: typeof pull.headRefName === 'string' ? pull.headRefName : '',
          title: typeof pull.title === 'string' ? pull.title : '',
          state: typeof pull.mergeStateStatus === 'string' ? pull.mergeStateStatus : '',
          checks,
          queue: null,
        }
      })
  } catch {
    return []
  }
}

export function applyQueuePositions(pulls: PullInfo[], json: string): void {
  try {
    const parsed: any = JSON.parse(json)
    const nodes = parsed?.data?.repository?.mergeQueue?.entries?.nodes
    if (!Array.isArray(nodes)) return

    const positions = new Map<number, number>()
    for (const node of nodes) {
      const number = Number(node?.pullRequest?.number)
      const position = Number(node?.position)
      if (Number.isFinite(number) && Number.isFinite(position)) positions.set(number, position)
    }

    for (const pull of pulls) pull.queue = positions.get(pull.number) ?? null
  } catch {
    // A failed queue response leaves every queue position as null.
  }
}

export function foldSalvage(lanes: LaneInfo[]): LaneInfo[] {
  const rows = lanes.map(lane => ({ ...lane }))
  const byBranch = new Map(rows.map(lane => [lane.branch, lane]))

  return rows.filter(lane => {
    if (!lane.branch.endsWith('-salvage')) return true

    const baseBranch = lane.salvageOf || lane.branch.slice(0, -'-salvage'.length)
    lane.salvageOf = baseBranch
    const base = byBranch.get(baseBranch)
    if (!base || base === lane) return true

    if (!lane.merged || lane.commitsAhead !== 0 || lane.path !== '(no worktree)' || lane.dirtyCount !== 0) {
      return true
    }

    if (base.path === '(no worktree)' && !base.path.includes('+salvage')) {
      base.path = '(no worktree) +salvage'
    }
    return false
  })
}

export type GitHubRepo = { owner: string; repo: string }

export function parseGitHubRemote(remote: string): GitHubRepo | null {
  const match = remote.trim().match(/github\.com(?::|\/)([^/]+)\/([^/]+?)(?:\.git)?\/?$/i)
  return match ? { owner: match[1], repo: match[2] } : null
}

const truncate = (value: string, max: number) => {
  if (value.length <= max) return value
  if (max <= 1) return '…'.slice(0, max)
  return `${value.slice(0, max - 1)}…`
}

export function formatLaneBoard(lanes: LaneInfo[], pulls: PullInfo[] = [], notes: string[] = []): string {
  const mergedCount = lanes.filter(lane => lane.merged).length
  const pullUnavailable = notes.some(note => note.startsWith('pull requests: could not verify'))
  const pullSummary = pullUnavailable ? 'PRs: could not verify' : `${pulls.length} open PR(s)`
  const lines = [`cure-lane-board: ${lanes.length} lane(s) (${mergedCount} merged) · ${pullSummary}`]

  if (lanes.length === 0) {
    lines.push('No active tri-lane branches or worktrees detected.')
  } else {
    lines.push(
      '─'.repeat(70),
      '  Lane / Branch               Ahead   Dirty   Defect Window   Path',
      '─'.repeat(70),
    )

    for (const lane of lanes) {
      const branchCol = (lane.branch || lane.name).padEnd(26).slice(0, 26)
      const aheadCol = `${lane.commitsAhead}c`.padEnd(8)
      const dirtyCol = lane.dirtyCount === 0 ? 'clean'.padEnd(8) : `${lane.dirtyCount} dirty`.padEnd(8)
      const windowCol = lane.windowStatus.padEnd(16)
      const shortPath = (lane.path || '(no worktree)').split('/').slice(-2).join('/')

      lines.push(`  ${branchCol}  ${aheadCol}${dirtyCol}${windowCol}${shortPath}`)
    }

    lines.push('─'.repeat(70))
  }

  if (!pullUnavailable) {
    lines.push('', `Pull requests (open): ${pulls.length}`)
    for (const pull of pulls) {
      const checks = `checks ${pull.checks.pass} pass · ${pull.checks.fail} fail · ${pull.checks.pending} pending`
      const queue = pull.queue === null ? '—' : `queue #${pull.queue}`
      const prefix = `  #${pull.number}  ${truncate(pull.branch, 24)}  ${checks}  ${queue}  `
      lines.push(`${prefix}${truncate(pull.title, Math.max(1, 100 - prefix.length))}`)
    }
  }

  const uniqueNotes = [...new Set(notes)]
  if (uniqueNotes.length > 0) lines.push('', ...uniqueNotes)
  return lines.join('\n')
}
