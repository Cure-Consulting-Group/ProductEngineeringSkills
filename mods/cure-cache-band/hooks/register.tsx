import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import { EMPTY, bandText, bar, inferTtl, leftText, recordStep, reportText, tokensText, view } from './cache'

/**
 * cure-cache-band: a row above the prompt showing how long the prompt cache
 * has left, the session's hit rate and misses, and, once it has lapsed, how
 * many tokens the next message will pay to re-cache. /cache gives the detail.
 *
 * It counts the main conversation's requests only: a subagent keeps a cache
 * of its own. Nothing is fetched; every figure comes from the usage each
 * model response already reports.
 *
 * Setting, as an environment variable:
 *   CURE_CACHE_TTL  `5m` or `1h`, when the inferred TTL is wrong for your plan
 *
 * The TTL is inferred, not reported by the API (see inferTtl): the countdown
 * is an estimate, the hit rate and misses are measured.
 */

const TICK_MS = 1000

const cache = atom({ plugin: 'cure-cache-band', key: 'cache' } as const, EMPTY)

let timer: { cancel: () => void } | undefined
let drawn = ''

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'cache', description: 'Show prompt cache time left, hit rate and misses for this session' })
    timer?.cancel()
    // Redraw only when the row's text would change: once a second in the last minute, once a minute before it.
    timer = $.clock.every(TICK_MS, async () => {
      const text = bandText(view(await read($, cache), await $.clock.now()))
      if (text !== drawn) $.ui.invalidate('ui.render')
    })
    return next(e)
  })

  on('session.end', async ($, e, next) => {
    timer?.cancel()
    timer = undefined
    return next(e)
  })

  on('turn.step', async function* ($, e, next) {
    const result = yield* next(e)
    const usage = result.usage
    if (e.agentId === undefined && usage) {
      const [now, ttl] = [await $.clock.now(), (await ttlNow($)).ttl]
      await update($, cache, state => recordStep(state, usage, now, ttl))
    }
    return result
  })

  on('command.run', { command: 'cache' }, async $ => {
    const { source } = await ttlNow($)
    return { text: reportText(await read($, cache), await $.clock.now(), source) }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const v = view(await read($, cache), await $.clock.now())
    drawn = bandText(v)
    if (v.kind === 'none' || e.props.hasSurvey) return next(e)

    const { Box, Text } = $.ui.resolve(e)

    if (v.kind === 'cold') {
      return (
        <Box>
          <Text color="red">cache ○ cold</Text>
          <Text dimColor> · next message re-caches {tokensText(v.tokens)} tokens</Text>
        </Box>
      )
    }

    const color = v.level === 'low' ? 'yellow' : 'green'
    const b = bar(v.fraction)
    return (
      <Box>
        <Text color={color}>
          cache ● {v.ttl} {b.filled}
        </Text>
        <Text dimColor>{b.empty}</Text>
        <Text color={color}> {leftText(v.leftMs)}</Text>
        <Text dimColor>
          {' '}
          · hit {v.hitPercent}% · misses {v.misses}
        </Text>
      </Box>
    )
  })
}

async function ttlNow($: EngineInterface) {
  const override = (await $.env.get('CURE_CACHE_TTL')) || undefined
  const { rateLimits } = await $.session.usage()
  const ttl = inferTtl(override, rateLimits)
  const source = override === ttl ? 'CURE_CACHE_TTL' : rateLimits.length === 0 ? 'inferred: no subscription limits reported' : 'inferred from subscription limits'
  return { ttl, source }
}
