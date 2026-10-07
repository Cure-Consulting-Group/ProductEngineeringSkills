/**
 * GitHub billing arithmetic for the spend band. Pure: the usage items in, the
 * numbers the band shows out.
 *
 * The source is `GET /organizations/{org}/settings/billing/usage?year&month`
 * (enhanced billing platform): one item per day × product × SKU × repo, with
 * `grossAmount` (list price), `discountAmount` (what the plan's included
 * usage absorbed) and `netAmount` (what is billed). Dates are UTC days.
 */

export type UsageItem = {
  date: string
  product: string
  sku: string
  quantity: number
  unitType: string
  grossAmount: number
  discountAmount: number
  netAmount: number
  repositoryName?: string
}

export type Spend = {
  /** UTC day the numbers are for, YYYY-MM-DD. */
  today: string
  /** Gross Actions spend today (list price, before included usage). */
  actionsToday: number
  /** Gross Actions spend month to date. */
  actionsMonth: number
  /** What is actually billed month to date, every product (seats included). */
  billedMonth: number
  /**
   * Gross Actions spend projected to month end: month to date, plus the rest
   * of the month at the average of the last (up to) three complete days. Falls
   * back to month-to-date pace before the month has a complete day.
   */
  projectedActions: number
  /** The daily pace the projection uses for the rest of the month. */
  recentDailyPace: number
  /** How many complete days that pace averages (0 = month-to-date pace). */
  paceDays: number
  /** The monthly included Actions allowance, in dollars. */
  allowance: number
  /** The allowance spread evenly over the month's days. */
  dailyAllowance: number
  /** Projected Actions gross above the allowance (0 when inside it). */
  projectedOverage: number
  /** The repo with the most gross Actions spend today, and its amount. */
  topRepoToday?: { repo: string; amount: number }
}

const round2 = (n: number) => Math.round(n * 100) / 100

/** Days in the UTC month of `now`. */
export function daysInMonth(now: Date): number {
  return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + 1, 0)).getUTCDate()
}

/** The band's numbers from one month's usage items, as of `now`. */
export function summarize(items: readonly UsageItem[], now: Date, allowance: number): Spend {
  const today = now.toISOString().slice(0, 10)
  let actionsToday = 0
  let actionsMonth = 0
  let billedMonth = 0
  const byRepoToday = new Map<string, number>()
  const byDay = new Map<string, number>()
  for (const i of items) {
    billedMonth += i.netAmount || 0
    if (i.product !== 'actions') continue
    actionsMonth += i.grossAmount || 0
    const day = i.date.slice(0, 10)
    byDay.set(day, (byDay.get(day) ?? 0) + (i.grossAmount || 0))
    if (day === today) {
      actionsToday += i.grossAmount || 0
      const repo = i.repositoryName || '(org)'
      byRepoToday.set(repo, (byRepoToday.get(repo) ?? 0) + (i.grossAmount || 0))
    }
  }
  const days = daysInMonth(now)
  // Elapsed days include today's fraction, so the projection does not jump at midnight.
  const elapsed = now.getUTCDate() - 1 + (now.getUTCHours() * 60 + now.getUTCMinutes()) / 1440
  // The last three complete days of this month (days with no usage count as $0).
  const recent: number[] = []
  for (let d = now.getUTCDate() - 1; d >= 1 && recent.length < 3; d--) {
    const key = `${today.slice(0, 8)}${String(d).padStart(2, '0')}`
    recent.push(byDay.get(key) ?? 0)
  }
  const remaining = Math.max(0, days - elapsed)
  const mtdPace = elapsed > 0.25 ? actionsMonth / elapsed : 0
  const recentDailyPace = recent.length > 0 ? recent.reduce((a, b) => a + b, 0) / recent.length : mtdPace
  const projectedActions = recent.length > 0 || elapsed > 0.25 ? actionsMonth + recentDailyPace * remaining : actionsMonth
  const top = [...byRepoToday.entries()].sort((a, b) => b[1] - a[1])[0]
  return {
    today,
    actionsToday: round2(actionsToday),
    actionsMonth: round2(actionsMonth),
    billedMonth: round2(billedMonth),
    projectedActions: round2(projectedActions),
    recentDailyPace: round2(recentDailyPace),
    paceDays: recent.length,
    allowance,
    dailyAllowance: round2(allowance / days),
    projectedOverage: round2(Math.max(0, projectedActions - allowance)),
    topRepoToday: top && top[1] > 0 ? { repo: top[0], amount: round2(top[1]) } : undefined,
  }
}

const usd = (n: number) => `$${n.toFixed(2)}`

/** The short suffix beside the spinner. */
export function bandText(s: Spend): string {
  return `Actions ${usd(s.actionsToday)} today · ${usd(s.dailyAllowance)}/day covered`
}

/** The persistent warning line, or undefined when the month is on pace. */
export function warningText(s: Spend): string | undefined {
  if (s.projectedOverage <= 0) return undefined
  return `GitHub Actions headed for ${usd(s.projectedActions)} this month at the recent ${usd(s.recentDailyPace)}/day, ${usd(s.projectedOverage)} over the ${usd(s.allowance)} included. /spend for detail.`
}

/** The /spend report. */
export function reportText(s: Spend, fetchedAt: string, org: string): string {
  return [
    `GitHub spend for ${org} (as of ${fetchedAt})`,
    `  Actions today        ${usd(s.actionsToday)}   (plan covers ~${usd(s.dailyAllowance)}/day)`,
    `  Actions this month   ${usd(s.actionsMonth)}   (plan covers ${usd(s.allowance)})`,
    `  Projected month end  ${usd(s.projectedActions)}   ${s.projectedOverage > 0 ? `→ ${usd(s.projectedOverage)} over` : '→ inside the allowance'}`,
    `                       (month to date + ${s.paceDays > 0 ? `last ${s.paceDays} full day${s.paceDays > 1 ? 's' : ''}' average, ${usd(s.recentDailyPace)}/day` : `month-to-date pace, ${usd(s.recentDailyPace)}/day`}, for the rest of the month)`,
    `  Billed so far        ${usd(s.billedMonth)}   (every product, seats included)`,
    s.topRepoToday ? `  Top repo today       ${s.topRepoToday.repo} ${usd(s.topRepoToday.amount)}` : '  Top repo today       none',
  ].join('\n')
}

/** Usage items from the API's JSON text; throws on anything else. */
export function parseUsage(json: string): UsageItem[] {
  const body = JSON.parse(json) as { usageItems?: unknown }
  if (!Array.isArray(body.usageItems)) throw new Error('no usageItems in the billing response')
  return body.usageItems as UsageItem[]
}
