import type { On } from 'claude-code'

import { formatHandoffDraft } from './handoff'

export function register(on: On) {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'handoff',
      description: 'Draft a structured STATE.md handoff block summarizing recent commits and uncommitted diffs',
    })
    return next(e)
  })

  on('command.run', { command: 'handoff' }, async $ => {
    let branch = 'unknown'
    const branchRes = await $.process.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    if (branchRes && branchRes.exitCode === 0 && branchRes.stdout) {
      branch = branchRes.stdout.trim()
    }

    let commits: string[] = []
    const logRes = await $.process.run(['git', 'log', '-n', '5', '--oneline'])
    if (logRes && logRes.exitCode === 0 && logRes.stdout) {
      commits = logRes.stdout.split('\n').map((l: string) => l.trim()).filter((l: string) => l.length > 0)
    }

    let dirtyFiles: string[] = []
    const statusRes = await $.process.run(['git', 'status', '--porcelain'])
    if (statusRes && statusRes.exitCode === 0 && statusRes.stdout) {
      dirtyFiles = statusRes.stdout
        .split('\n')
        .map((l: string) => l.slice(3).trim())
        .filter((l: string) => l.length > 0)
    }

    const date = new Date().toISOString().slice(0, 10)
    const draft = formatHandoffDraft({ date, branch, commits, dirtyFiles })

    return { text: draft }
  })
}
