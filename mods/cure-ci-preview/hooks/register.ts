import type { On } from 'claude-code'

import { classifyChanges, formatCiPreview } from './preview'

const PUSH_COMMAND_REGEX = /\b(?:git\s+push|gh\s+pr\s+create)\b/

async function getChangedPaths($: any): Promise<string[]> {
  const diffRes = await $.process.run(['git', 'diff', '--name-only', 'origin/HEAD...HEAD'])
  if (diffRes && diffRes.exitCode === 0 && diffRes.stdout) {
    const lines = diffRes.stdout.split('\n').map((l: string) => l.trim()).filter((l: string) => l.length > 0)
    if (lines.length > 0) return lines
  }

  // Fallback to local unstaged/staged git status
  const statRes = await $.process.run(['git', 'status', '--porcelain'])
  if (statRes && statRes.exitCode === 0 && statRes.stdout) {
    return statRes.stdout
      .split('\n')
      .map((l: string) => l.trim().slice(3).trim())
      .filter((l: string) => l.length > 0)
  }

  return []
}

export function register(on: On) {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'ci-preview',
      description: 'Preview GitHub Actions CI job trigger classification and runner costs for pending changes',
    })
    return next(e)
  })

  on('command.run', { command: 'ci-preview' }, async $ => {
    const paths = await getChangedPaths($)
    const preview = classifyChanges(paths)
    return { text: formatCiPreview(preview) }
  })

  on('tool.call', async ($, e, next) => {
    if (String(e.tool) === 'Bash' && typeof e.command === 'string' && PUSH_COMMAND_REGEX.test(e.command)) {
      const paths = await getChangedPaths($)
      const preview = classifyChanges(paths)
      $.ui.toast(`cure-ci-preview: ~${preview.estimatedMinutes} billed min (~$${preview.estimatedCostUsd.toFixed(2)}) for ${preview.jobs.join(', ')}`)
      if (preview.warning) {
        $.ui.log(`cure-ci-preview warning: ${preview.warning}`)
      }
    }

    return next(e)
  })
}
