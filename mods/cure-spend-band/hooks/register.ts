import type { On } from 'claude-code'

import { bandText, parseUsage, reportText, summarize, warningText, type Spend } from './spend'

/**
 * cure-spend-band: today's GitHub Actions spend beside the spinner, a warning
 * line under the prompt when the month is on pace to exceed the plan's
 * included usage, and /spend for the detail.
 *
 * Reads billing through the `gh` CLI the person is already logged into
 * (`gh api organizations/{org}/settings/billing/usage`), every 15 minutes and
 * on /spend. No token is stored by the mod.
 *
 * Settings, as environment variables:
 *   CURE_SPEND_ORG        the organization (default Cure-Consulting-Group)
 *   CURE_SPEND_ALLOWANCE  monthly included Actions usage in USD (default 300)
 *
 * Fails quiet: if `gh` is missing, logged out or the API refuses, the band
 * shows nothing and /spend says why.
 */

const REFRESH_MS = 15 * 60 * 1000
const DEFAULT_ORG = 'Cure-Consulting-Group'
const DEFAULT_ALLOWANCE = 300

let latest: { spend: Spend; fetchedAt: string; org: string } | undefined
let lastError: string | undefined
let timer: { cancel: () => void } | undefined

export function register(on: On) {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'spend', description: "Show this month's GitHub Actions spend against the plan's included usage" })
    timer?.cancel()
    timer = $.clock.every(REFRESH_MS, () => void refresh($))
    void refresh($)
    return next(e)
  })

  on('session.end', async ($, e, next) => {
    timer?.cancel()
    timer = undefined
    return next(e)
  })

  on('command.run', { command: 'spend' }, async $ => {
    await refresh($)
    if (!latest) return { text: `cure-spend-band: no billing data (${lastError ?? 'not fetched yet'})` }
    const report = reportText(latest.spend, latest.fetchedAt, latest.org)
    return {
      text: lastError ? `${report}\n  Latest refresh FAILED: ${lastError} (numbers above are from ${latest.fetchedAt})` : report,
    }
  })

  on('ui.render', { component: 'Spinner' }, async ($, e, next) => {
    if (!latest) return next(e)
    const suffix = typeof e.props?.suffix === 'string' ? e.props.suffix : ''
    return next({ ...e, props: { ...e.props, suffix: `${suffix} · ${bandText(latest.spend)}` } })
  })
}

async function settings($: any): Promise<{ org: string; allowance: number }> {
  const org = (await $.env.get('CURE_SPEND_ORG')) || DEFAULT_ORG
  const raw = Number(await $.env.get('CURE_SPEND_ALLOWANCE'))
  return { org, allowance: Number.isFinite(raw) && raw > 0 ? raw : DEFAULT_ALLOWANCE }
}

async function refresh($: any): Promise<void> {
  try {
    const { org, allowance } = await settings($)
    const now = new Date(await $.clock.now())
    const url = `organizations/${org}/settings/billing/usage?year=${now.getUTCFullYear()}&month=${now.getUTCMonth() + 1}`
    const res = await $.process.run(['gh', 'api', url], { timeoutMs: 60000 })
    if (res.exitCode !== 0) throw new Error((res.stderr || 'gh api failed').trim().split('\n')[0])
    const spend = summarize(parseUsage(res.stdout), now, allowance)
    latest = { spend, fetchedAt: now.toISOString().slice(11, 16) + ' UTC', org }
    lastError = undefined
    $.ui.status(warningText(spend))
  } catch (err) {
    lastError = err instanceof Error ? err.message : String(err)
  }
  $.ui.invalidate('ui.render')
}
