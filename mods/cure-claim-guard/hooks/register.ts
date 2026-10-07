import type { On } from 'claude-code'

import {
  detectStateFromPath,
  evaluateClaim,
  formatClaimsReport,
  parseStateTargets,
} from './claims'

const FILE_TOOLS = new Set(['Write', 'Edit', 'MultiEdit', 'NotebookEdit'])
const TARGETS_PATH = '.agents/state-targets.md'
const OVERRIDES_KEY = 'cure-claim-guard-overrides'

const REFUSE = 'Refuse the write'
const ALLOW = 'Allow this once (logged)'

function targetPath(e: Record<string, unknown>): string {
  const str = (v: unknown) => (typeof v === 'string' ? v : '')
  return str(e.file_path) || str(e.path) || str(e.target)
}

export function register(on: On) {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'claims',
      description: 'Show multi-machine state target ownership for this repository',
    })
    return next(e)
  })

  on('command.run', { command: 'claims' }, async $ => {
    const res = await $.process.run(['hostname'])
    const host = res.stdout ? res.stdout.trim() : 'unknown-host'
    const exists = await $.fs.exists(TARGETS_PATH)
    if (!exists) {
      return {
        text: `cure-claim-guard: No .agents/state-targets.md found in workspace. Host: ${host}`,
      }
    }
    const content = (await $.fs.read(TARGETS_PATH)) || ''
    const claims = parseStateTargets(content)
    return { text: formatClaimsReport(host, claims) }
  })

  on('tool.call', async ($, e, next) => {
    if (!FILE_TOOLS.has(String(e.tool))) return next(e)

    const path = targetPath(e)
    const state = detectStateFromPath(path)
    if (!state) return next(e)

    const exists = await $.fs.exists(TARGETS_PATH)
    if (!exists) return next(e)

    const content = (await $.fs.read(TARGETS_PATH)) || ''
    const claims = parseStateTargets(content)
    const res = await $.process.run(['hostname'])
    const host = res.stdout ? res.stdout.trim() : 'unknown-host'

    const verdict = evaluateClaim(state, host, claims)
    if (verdict.allowed) return next(e)

    // Unauthorized write according to state-targets.md
    let answer: string | undefined
    try {
      answer = await $.ui.ask(
        `cure-claim-guard violation:\n${verdict.reason}\nTarget: ${path}`,
        [REFUSE, ALLOW],
      )
    } catch {
      // Non-interactive or dismissed
      answer = undefined
    }

    if (answer !== ALLOW) {
      return {
        deny: `Refused by cure-claim-guard: ${verdict.reason}`,
      }
    }

    // Override allowed
    const overrides = ((await $.store.get(OVERRIDES_KEY)) as any[] | undefined) ?? []
    overrides.push({
      at: new Date().toISOString(),
      state,
      host,
      path,
      owner: verdict.owner,
    })
    await $.store.set(OVERRIDES_KEY, overrides)
    $.ui.toast(`cure-claim-guard: override recorded for state ${state}`)

    return next(e)
  })
}
