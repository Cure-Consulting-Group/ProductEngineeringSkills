import type { On } from 'claude-code'

import {
  extractCitations,
  formatVerificationNotice,
  verifyCitation,
  type StaleCitation,
  type VerificationResult,
} from './cite'

const CITE_STATE_KEY = 'cure-cite-check-stats'

type CiteSessionState = {
  totalChecked: number
  totalValid: number
  totalStale: number
  recentStale: Array<{ path: string; line: number; reason: string }>
}

export function register(on: On) {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'cite-check',
      description: 'Show code citation validation summary for this session',
    })
    return next(e)
  })

  on('command.run', { command: 'cite-check' }, async $ => {
    const stats = ((await $.store.get(CITE_STATE_KEY)) as CiteSessionState | undefined) ?? {
      totalChecked: 0,
      totalValid: 0,
      totalStale: 0,
      recentStale: [],
    }

    if (stats.totalChecked === 0) {
      return { text: 'cure-cite-check: No code citations checked in this session yet.' }
    }

    const lines = [
      `cure-cite-check: ${stats.totalChecked} citation(s) checked · ${stats.totalValid} valid · ${stats.totalStale} stale`,
    ]

    if (stats.recentStale.length > 0) {
      lines.push('Stale citations:')
      for (const s of stats.recentStale.slice(-5)) {
        lines.push(`  • ${s.path}:${s.line} — ${s.reason}`)
      }
    }

    return { text: lines.join('\n') }
  })

  on('turn.step', async function* ($, e, next) {
    const result = yield* next(e)
    const text = result?.answer

    if (typeof text === 'string' && text.length > 0) {
      const citations = extractCitations(text)
      if (citations.length > 0) {
        const staleList: StaleCitation[] = []

        for (const c of citations) {
          const exists = await $.fs.exists(c.path)
          let lineCount = 0

          if (exists) {
            const content = await $.fs.read(c.path)
            if (typeof content === 'string') {
              lineCount = content.split('\n').length
            }
          }

          const stale = verifyCitation(c, exists, lineCount)
          if (stale) {
            staleList.push(stale)
          }
        }

        const verification: VerificationResult = {
          total: citations.length,
          valid: citations.length - staleList.length,
          stale: staleList,
        }

        const notice = formatVerificationNotice(verification)

        // Update session stats
        const stats = ((await $.store.get(CITE_STATE_KEY)) as CiteSessionState | undefined) ?? {
          totalChecked: 0,
          totalValid: 0,
          totalStale: 0,
          recentStale: [],
        }

        stats.totalChecked += verification.total
        stats.totalValid += verification.valid
        stats.totalStale += verification.stale.length
        for (const s of verification.stale) {
          stats.recentStale.push({
            path: s.citation.path,
            line: s.citation.line,
            reason: s.reason,
          })
        }
        await $.store.set(CITE_STATE_KEY, stats)

        if (staleList.length > 0) {
          $.ui.toast(notice)
          result.answer = `${text}\n\n${notice}`
        }
      }
    }

    return result
  })
}
