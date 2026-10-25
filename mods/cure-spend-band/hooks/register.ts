import type { Register } from 'claude-code'

import { bandText, compact, parseUsage, reportText, summarize, warningText, type Spend, type UsageItem } from './spend'

/**
 * cure-spend-band: today's GitHub Actions spend beside the spinner, a warning
 * line under the prompt when the month is on pace to exceed the plan's
 * included usage, and /spend for the detail.
 *
 * Reads billing through the `gh` CLI the person is already logged into
 * (`gh api organizations/{org}/settings/billing/usage`). One fetch serves the
 * whole machine: the answer is kept in `$.store` (shared by every session) with
 * its `fetchedAt`, and a session fetches only when that copy is over 15 minutes
 * old. No token is stored by the mod.
 *
 * Settings: userConfig `org`, `allowanceUsd`, `paceWarning`; the environment
 * variables CURE_SPEND_ORG and CURE_SPEND_ALLOWANCE still override them.
 * `/spend dismiss` hides the warning line for the rest of the month; `/spend show`
 * brings it back.
 *
 * Fails quiet: if `gh` is missing, logged out or the API refuses, the band
 * shows nothing and /spend says why.
 */

const REFRESH_MS = 15 * 60 * 1000
/** /spend refetches when the machine's copy is older than this. */
const COMMAND_MAX_AGE_MS = 60 * 1000
/** Under the 30 s `$.process.run` cap. */
const GH_TIMEOUT_MS = 25_000
const DEFAULT_ORG = 'Cure-Consulting-Group'
const DEFAULT_ALLOWANCE = 300
const BILLING_KEY = 'billing'
const DISMISSED_KEY = 'dismissedMonth'

type Billing = { org: string; month: string; fetchedAt: number; items: UsageItem[] }
type Settings = { org: string; allowance: number; paceWarning: boolean }

let latest: { spend: Spend; fetchedAt: string; org: string } | undefined
let lastError: string | undefined
let timer: { cancel: () => void } | undefined

export const register: Register = (on, options) => {
  const configured: Settings = {
    org: typeof options.org === 'string' && options.org.trim() ? options.org.trim() : DEFAULT_ORG,
    allowance: typeof options.allowanceUsd === 'number' && options.allowanceUsd > 0 ? options.allowanceUsd : DEFAULT_ALLOWANCE,
    paceWarning: options.paceWarning !== false,
  }

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'spend',
      description: "Show this month's GitHub Actions spend against the plan's included usage (dismiss | show)",
    })
    timer?.cancel()
    timer = $.clock.every(REFRESH_MS, () => void refresh($, configured, REFRESH_MS))
    void refresh($, configured, REFRESH_MS)
    return next(e)
  })

  on('session.end', async ($, e, next) => {
    timer?.cancel()
    timer = undefined
    return next(e)
  })

  on('command.run', { command: 'spend' }, async ($, e) => {
    const arg = String(e.args ?? '').trim().toLowerCase()
    if (arg === 'dismiss' || arg === 'show') {
      const month = monthOf(new Date(await $.clock.now()))
      if (arg === 'dismiss') await $.store.set(DISMISSED_KEY, month)
      else await $.store.delete(DISMISSED_KEY)
      await refresh($, configured, REFRESH_MS)
      return { text: arg === 'dismiss' ? `cure-spend-band: pace warning hidden until ${month} ends (/spend show brings it back)` : 'cure-spend-band: pace warning shown again' }
    }
    await refresh($, configured, COMMAND_MAX_AGE_MS)
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

const monthOf = (d: Date) => d.toISOString().slice(0, 7)

async function settings($: any, configured: Settings): Promise<Settings> {
  const org = (await $.env.get('CURE_SPEND_ORG')) || configured.org
  const raw = Number(await $.env.get('CURE_SPEND_ALLOWANCE'))
  return { org, allowance: Number.isFinite(raw) && raw > 0 ? raw : configured.allowance, paceWarning: configured.paceWarning }
}

/** Uses the machine's copy when it is younger than `maxAgeMs`; fetches otherwise. */
async function refresh($: any, configured: Settings, maxAgeMs: number): Promise<void> {
  try {
    const { org, allowance, paceWarning } = await settings($, configured)
    const nowMs = await $.clock.now()
    const now = new Date(nowMs)
    const month = monthOf(now)
    let billing = (await $.store.get(BILLING_KEY)) as Billing | undefined
    const isFresh = billing && billing.org === org && billing.month === month && nowMs - billing.fetchedAt < maxAgeMs
    if (!isFresh) {
      const url = `organizations/${org}/settings/billing/usage?year=${now.getUTCFullYear()}&month=${now.getUTCMonth() + 1}`
      const res = await $.process.run(['gh', 'api', url], { timeoutMs: GH_TIMEOUT_MS })
      if (res.exitCode !== 0) throw new Error((res.stderr || 'gh api failed').trim().split('\n')[0])
      billing = { org, month, fetchedAt: nowMs, items: compact(parseUsage(res.stdout)) }
      await $.store.set(BILLING_KEY, billing)
    }
    const spend = summarize(billing!.items, now, allowance)
    latest = { spend, fetchedAt: new Date(billing!.fetchedAt).toISOString().slice(11, 16) + ' UTC', org }
    lastError = undefined
    const dismissed = (await $.store.get(DISMISSED_KEY)) === month
    $.ui.status(paceWarning && !dismissed ? warningText(spend) : undefined)
  } catch (err) {
    lastError = err instanceof Error ? err.message : String(err)
  }
  $.ui.invalidate('ui.render')
}
