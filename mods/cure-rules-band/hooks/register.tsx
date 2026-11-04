import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { ActiveRules } from '../types'
import { formatRulesReport, repoNameFromCommonDir, resolveRepoRules } from './banner'

/**
 * cure-rules-band: the house rules of the repository the session is in, in a
 * band above the prompt. Shows nothing for a repo with no rules.
 *
 * Hot path: drawing never spawns git or reads a file. The rules are resolved
 * at session start, after each main-loop turn and on /rules, and git runs only
 * when the session's root has moved to a folder it has not seen.
 */

const CONFIG_FILE = '.cure/rules.json'

const active = atom({ plugin: 'cure-rules-band', key: 'active' } as const, null)
const isHidden = atom({ plugin: 'cure-rules-band', key: 'isHidden' } as const, false)

/** Repository per root folder: { name, toplevel }, or null outside git. */
const repoCache = new Map<string, { name: string; top: string } | null>()

export const register: Register = on => {
  repoCache.clear()

  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'rules', description: 'Show the house rules of the repository this session is in' })
    await refresh($)
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId === undefined) await refresh($)
    return result
  })

  on('command.run', { command: 'rules' }, async ($, e) => {
    const arg = String(e.args ?? '').trim().toLowerCase()
    if (arg === 'hide' || arg === 'show') {
      await update($, isHidden, () => arg === 'hide')
      $.ui.invalidate('ui.render')
      return { text: arg === 'hide' ? 'cure-rules-band: band hidden for this session (/rules show brings it back)' : 'cure-rules-band: band shown' }
    }
    const now = await refresh($)
    return { text: now ? formatRulesReport(now.repo, now.rules) : 'cure-rules-band: this repository has no house rules on record.' }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const now = await read($, active)
    if (e.props.hasSurvey || !now || (await read($, isHidden))) return next(e)
    const { Box, Text } = $.ui.resolve(e)
    return (
      <Box>
        <Text color="cyan">rules ● {now.repo}</Text>
        <Text dimColor> · {now.rules.join(' · ')}</Text>
      </Box>
    )
  })
}

async function repoOf($: any, dir: string): Promise<{ name: string; top: string } | null> {
  if (repoCache.has(dir)) return repoCache.get(dir) ?? null
  const res = await $.process
    .run(['git', '-C', dir, 'rev-parse', '--path-format=absolute', '--git-common-dir', '--show-toplevel'], { timeoutMs: 5000 })
    .catch(() => undefined)
  const [common = '', top = ''] = res && res.exitCode === 0 ? res.stdout.trim().split('\n') : []
  const found = common ? { name: repoNameFromCommonDir(common), top: top.trim() } : null
  repoCache.set(dir, found)
  return found
}

async function refresh($: any): Promise<ActiveRules | null> {
  const root: string = await $.session.root()
  const current = await read($, active)
  if (current && current.root === root) return current
  const repo = await repoOf($, root)
  const configPath = `${repo?.top || root}/${CONFIG_FILE}`
  const config = (await $.fs.exists(configPath)) ? await $.fs.read(configPath).catch(() => undefined) : undefined
  const resolved = resolveRepoRules(repo?.name, typeof config === 'string' ? config : undefined)
  const next: ActiveRules | null = resolved ? { ...resolved, root } : null
  if (JSON.stringify(next) !== JSON.stringify(current)) {
    await update($, active, () => next)
    $.ui.invalidate('ui.render')
  }
  return next
}
