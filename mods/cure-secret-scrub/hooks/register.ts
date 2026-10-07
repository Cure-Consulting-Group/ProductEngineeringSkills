import type { On } from 'claude-code'

import { scrubToolOutput } from './scrub'

const SCRUB_TOOLS = new Set(['Read', 'Grep', 'Bash'])
const SCRUB_STATE_KEY = 'cure-secret-scrub-counts'

type ScrubRecord = {
  totalCount: number
  byKind: Record<string, number>
}

export function register(on: On) {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'secret-scrub',
      description: 'Show credentials redacted from tool outputs during this session',
    })
    return next(e)
  })

  on('command.run', { command: 'secret-scrub' }, async $ => {
    const stats = ((await $.store.get(SCRUB_STATE_KEY)) as ScrubRecord | undefined) ?? {
      totalCount: 0,
      byKind: {},
    }

    if (stats.totalCount === 0) {
      return { text: 'cure-secret-scrub: No credentials have been redacted in this session.' }
    }

    const lines = [
      `cure-secret-scrub: Redacted ${stats.totalCount} credential(s) from tool output:`,
      ...Object.entries(stats.byKind).map(([kind, num]) => `  • ${kind}: ${num}`),
    ]
    return { text: lines.join('\n') }
  })

  on('tool.call', async ($, e, next) => {
    const r = await next(e)
    if (!r || !SCRUB_TOOLS.has(String(e.tool))) {
      return r
    }

    let modified = false
    let turnCount = 0
    const turnKinds: string[] = []

    for (const field of ['result', 'text', 'stdout', 'stderr'] as const) {
      if (r[field] !== undefined) {
        const { output, count, kinds } = scrubToolOutput(r[field])
        if (count > 0) {
          r[field] = output
          modified = true
          turnCount += count
          turnKinds.push(...kinds)
        }
      }
    }

    if (modified) {
      const stats = ((await $.store.get(SCRUB_STATE_KEY)) as ScrubRecord | undefined) ?? {
        totalCount: 0,
        byKind: {},
      }
      stats.totalCount += turnCount
      for (const k of turnKinds) {
        stats.byKind[k] = (stats.byKind[k] || 0) + 1
      }
      await $.store.set(SCRUB_STATE_KEY, stats)

      $.ui.toast(`cure-secret-scrub: Redacted ${turnCount} credential(s) from ${String(e.tool)} output`)
    }

    return r
  })
}
