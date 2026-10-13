import type { On } from 'claude-code'

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

type ProcessResult = { exitCode: number; stdout: string; stderr: string }

const failedProcess = (): ProcessResult => ({ exitCode: 1, stdout: '', stderr: 'process failed' })

async function run($: any, argv: string[]): Promise<ProcessResult> {
  try {
    const result = await $.process.run(argv)
    return {
      exitCode: typeof result?.exitCode === 'number' ? result.exitCode : 1,
      stdout: typeof result?.stdout === 'string' ? result.stdout : '',
      stderr: typeof result?.stderr === 'string' ? result.stderr : '',
    }
  } catch {
    return failedProcess()
  }
}

const parseBranches = (stdout: string): string[] =>
  stdout
    .split('\n')
    .map(line => line.replace(/^[*+ ]+/, '').trim())
    .filter(line => line.startsWith('lane/'))

const salvageOf = (branch: string): string | undefined =>
  branch.endsWith('-salvage') ? branch.slice(0, -'-salvage'.length) : undefined

export function register(on: On) {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'lanes',
      description: 'Show status of active tri-lane worktrees, branches, live commits, defect windows, and pull requests',
    })
    return next(e)
  })

  on('command.run', { command: 'lanes' }, async $ => {
    const lanes: LaneInfo[] = []
    const seenBranches = new Set<string>()
    const notes: string[] = []
    const addNote = (note: string) => {
      if (!notes.includes(note)) notes.push(note)
    }

    const mergedRes = await run($, ['git', 'branch', '--merged', 'origin/HEAD', '--list', 'lane/*'])
    const mergedBranches = new Set<string>()
    if (mergedRes.exitCode === 0) {
      for (const branch of parseBranches(mergedRes.stdout)) mergedBranches.add(branch)
    } else {
      addNote('could not verify merged state (origin/HEAD unset)')
    }

    const makeLane = async (branch: string, path: string, dirtyCount: number): Promise<LaneInfo> => {
      let commitsAhead = 0
      const aheadRes = await run($, ['git', 'rev-list', '--count', `origin/HEAD..${branch}`])
      if (aheadRes.exitCode === 0) {
        commitsAhead = parseInt(aheadRes.stdout.trim(), 10) || 0
      } else {
        addNote('lane commit counts: could not verify')
      }

      return {
        name: branch.replace(/^lane\//, ''),
        branch,
        path,
        commitsAhead,
        dirtyCount,
        windowStatus: mergedBranches.has(branch) ? 'merged' : 'active',
        merged: mergedBranches.has(branch),
        salvageOf: salvageOf(branch),
      }
    }

    const wtRes = await run($, ['git', 'worktree', 'list', '--porcelain'])
    if (wtRes.exitCode === 0) {
      const entries = parseWorktreeList(wtRes.stdout)
      for (const entry of entries) {
        if (!entry.branch || !entry.branch.startsWith('lane/')) continue
        seenBranches.add(entry.branch)

        let dirty = 0
        const statusRes = await run($, ['git', '-C', entry.path, 'status', '--porcelain'])
        if (statusRes.exitCode === 0) {
          dirty = statusRes.stdout.split('\n').filter(line => line.trim().length > 0).length
        } else {
          addNote('worktree status: could not verify')
        }

        lanes.push(await makeLane(entry.branch, entry.path, dirty))
      }
    } else {
      addNote('worktrees: could not verify')
    }

    const brRes = await run($, ['git', 'branch', '--list', 'lane/*'])
    if (brRes.exitCode === 0) {
      for (const branch of parseBranches(brRes.stdout)) {
        if (seenBranches.has(branch)) continue
        lanes.push(await makeLane(branch, '(no worktree)', 0))
      }
    } else {
      addNote('lane branches: could not verify')
    }

    const foldedLanes = foldSalvage(lanes)
    let pulls: PullInfo[] = []
    const pullRes = await run($, [
      'gh',
      'pr',
      'list',
      '--state',
      'open',
      '--limit',
      '30',
      '--json',
      'number,headRefName,title,mergeStateStatus,statusCheckRollup',
    ])

    if (pullRes.exitCode !== 0) {
      addNote('pull requests: could not verify (gh unavailable)')
    } else {
      pulls = parsePullList(pullRes.stdout)

      const remoteRes = await run($, ['git', 'remote', 'get-url', 'origin'])
      const repo = remoteRes.exitCode === 0 ? parseGitHubRemote(remoteRes.stdout) : null
      if (repo) {
        const query = `{repository(owner:"${repo.owner}",name:"${repo.repo}"){mergeQueue{entries(first:20){nodes{position pullRequest{number}}}}}}`
        const queueRes = await run($, ['gh', 'api', 'graphql', '-f', `query=${query}`])
        if (queueRes.exitCode === 0) {
          applyQueuePositions(pulls, queueRes.stdout)
        } else {
          addNote('merge queue: could not verify')
        }
      } else {
        addNote('merge queue: could not verify')
      }
    }

    return { text: formatLaneBoard(foldedLanes, pulls, notes) }
  })
}
