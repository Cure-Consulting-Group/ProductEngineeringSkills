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

import { git, run, type GitResult } from './shared/git'

const GH_TIMEOUT_MS = 15_000

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
    const notes: string[] = []
    const addNote = (note: string) => {
      if (!notes.includes(note)) notes.push(note)
    }
    // Every git call names the repository the session is rooted in, never the shell's cwd.
    const root = await $.session.root()

    // Round 1, in parallel: everything that does not depend on another answer.
    const [mergedRes, wtRes, brRes, pullRes, remoteRes] = await Promise.all([
      git($, root, ['branch', '--merged', 'origin/HEAD', '--list', 'lane/*']),
      git($, root, ['worktree', 'list', '--porcelain']),
      git($, root, ['branch', '--list', 'lane/*']),
      run($, ['gh', 'pr', 'list', '--state', 'open', '--limit', '30', '--json', 'number,headRefName,title,mergeStateStatus,statusCheckRollup'], GH_TIMEOUT_MS),
      git($, root, ['remote', 'get-url', 'origin']),
    ])

    const mergedBranches = new Set<string>()
    if (mergedRes.exitCode === 0) for (const branch of parseBranches(mergedRes.stdout)) mergedBranches.add(branch)
    else addNote('could not verify merged state (origin/HEAD unset)')

    const targets: Array<{ branch: string; path: string; hasWorktree: boolean }> = []
    const seenBranches = new Set<string>()
    if (wtRes.exitCode === 0) {
      for (const entry of parseWorktreeList(wtRes.stdout)) {
        if (!entry.branch || !entry.branch.startsWith('lane/')) continue
        seenBranches.add(entry.branch)
        targets.push({ branch: entry.branch, path: entry.path, hasWorktree: true })
      }
    } else {
      addNote('worktrees: could not verify')
    }
    if (brRes.exitCode === 0) {
      for (const branch of parseBranches(brRes.stdout)) {
        if (!seenBranches.has(branch)) targets.push({ branch, path: '(no worktree)', hasWorktree: false })
      }
    } else {
      addNote('lane branches: could not verify')
    }

    // Round 2, in parallel: per lane, its commits ahead and (with a worktree) its dirty files.
    const repo = remoteRes.exitCode === 0 ? parseGitHubRemote(remoteRes.stdout) : null
    const queueQuery = repo && pullRes.exitCode === 0
      ? `{repository(owner:"${repo.owner}",name:"${repo.repo}"){mergeQueue{entries(first:20){nodes{position pullRequest{number}}}}}}`
      : undefined
    const [perLane, queueRes] = await Promise.all([
      Promise.all(
        targets.map(t =>
          Promise.all([
            git($, root, ['rev-list', '--count', `origin/HEAD..${t.branch}`]),
            t.hasWorktree ? git($, t.path, ['status', '--porcelain']) : Promise.resolve<GitResult>({ exitCode: 0, stdout: '', stderr: '' }),
          ]),
        ),
      ),
      queueQuery ? run($, ['gh', 'api', 'graphql', '-f', `query=${queueQuery}`], GH_TIMEOUT_MS) : Promise.resolve(undefined),
    ])

    const lanes: LaneInfo[] = targets.map((t, i) => {
      const [aheadRes, statusRes] = perLane[i]
      if (aheadRes.exitCode !== 0) addNote('lane commit counts: could not verify')
      if (statusRes.exitCode !== 0) addNote('worktree status: could not verify')
      return {
        name: t.branch.replace(/^lane\//, ''),
        branch: t.branch,
        path: t.path,
        commitsAhead: aheadRes.exitCode === 0 ? parseInt(aheadRes.stdout.trim(), 10) || 0 : 0,
        dirtyCount: statusRes.exitCode === 0 ? statusRes.stdout.split('\n').filter(line => line.trim().length > 0).length : 0,
        windowStatus: mergedBranches.has(t.branch) ? 'merged' : 'active',
        merged: mergedBranches.has(t.branch),
        salvageOf: salvageOf(t.branch),
      }
    })

    let pulls: PullInfo[] = []
    if (pullRes.exitCode !== 0) {
      addNote('pull requests: could not verify (gh unavailable)')
    } else {
      pulls = parsePullList(pullRes.stdout)
      if (queueRes && queueRes.exitCode === 0) applyQueuePositions(pulls, queueRes.stdout)
      else addNote('merge queue: could not verify')
    }

    return { text: formatLaneBoard(foldSalvage(lanes), pulls, notes) }
  })
}
