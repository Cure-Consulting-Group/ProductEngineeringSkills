import type { On } from 'claude-code'

import { detectEgressViolation, formatEgressReport } from './egress'

const OVERRIDES_KEY = 'cure-egress-guard-overrides'
const REFUSE = 'Refuse the request'
const ALLOW = 'Allow this once (logged)'

async function getRepoName($: any): Promise<string> {
  const res = await $.process.run(['git', 'rev-parse', '--show-toplevel'])
  if (res && res.exitCode === 0 && res.stdout) {
    return res.stdout.trim().split('/').pop() || ''
  }
  return ''
}

export function register(on: On) {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'egress-guard',
      description: 'Show outbound AI-vendor egress protection status and prohibited hosts',
    })
    return next(e)
  })

  on('command.run', { command: 'egress-guard' }, async $ => {
    const repo = await getRepoName($)
    return { text: formatEgressReport(repo) }
  })

  on('tool.call', async ($, e, next) => {
    const isBash = String(e.tool) === 'Bash' && typeof e.command === 'string'
    const isWebFetch = String(e.tool) === 'WebFetch' && typeof e.url === 'string'

    if (!isBash && !isWebFetch) return next(e)

    const payload = isBash ? String(e.command) : String(e.url)
    const repo = await getRepoName($)
    const verdict = detectEgressViolation(payload, repo)

    if (!verdict.violated) return next(e)

    // Unauthorized AI egress in protected repo
    let answer: string | undefined
    try {
      answer = await $.ui.ask(
        `cure-egress-guard warning:\n${verdict.reason}`,
        [REFUSE, ALLOW],
      )
    } catch {
      answer = undefined
    }

    if (answer !== ALLOW) {
      return {
        deny: `Blocked by cure-egress-guard: ${verdict.reason}`,
      }
    }

    // Override allowed and recorded
    const overrides = ((await $.store.get(OVERRIDES_KEY)) as any[] | undefined) ?? []
    overrides.push({
      at: new Date().toISOString(),
      repo,
      host: verdict.host,
      tool: String(e.tool),
    })
    await $.store.set(OVERRIDES_KEY, overrides)
    $.ui.toast(`cure-egress-guard: override recorded for ${verdict.host}`)

    return next(e)
  })
}
