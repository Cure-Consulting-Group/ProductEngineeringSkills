import type { CacheState, CacheTtl } from '../types'

/** What one model response reported, as `turn.step`'s `usage` carries it. */
export type StepUsage = {
  input_tokens: number
  output_tokens: number
  cache_read_input_tokens: number
  cache_creation_input_tokens: number
}

export type RateLimit = { kind: string; percentUsed: number }

export type View =
  | { kind: 'none' }
  | { kind: 'warm'; level: 'ok' | 'low'; ttl: CacheTtl; leftMs: number; fraction: number; hitPercent: number; misses: number }
  | { kind: 'cold'; tokens: number }

export const TTL_MS: Record<CacheTtl, number> = { '5m': 5 * 60 * 1000, '1h': 60 * 60 * 1000 }

/** Under this share of the TTL left, the band turns amber. */
export const LOW_FRACTION = 0.25
/** A prefix shorter than this is below the API's minimum cacheable length; reading none of it is not a miss. */
const MIN_CACHEABLE = 1024
export const BAR_CELLS = 16

export const EMPTY: CacheState = {
  lastAt: null,
  ttl: '1h',
  prefixTokens: 0,
  nextTokens: 0,
  read: 0,
  written: 0,
  uncached: 0,
  requests: 0,
  misses: 0,
}

/**
 * The TTL the session's cache entries are assumed to have. The API does not
 * report it per response, so this is inferred: CURE_CACHE_TTL when set;
 * otherwise 1h on a subscription inside its limits, 5m on an API key (no
 * rate-limit windows) or once a window is exhausted.
 */
export function inferTtl(override: string | undefined, rateLimits: readonly RateLimit[]): CacheTtl {
  if (override === '5m' || override === '1h') return override
  if (rateLimits.length === 0) return '5m'
  return rateLimits.some(l => l.percentUsed >= 100) ? '5m' : '1h'
}

/**
 * Folds one main-thread response into the session's figures. A miss is a
 * request, after the first, that read less than half of the prefix the
 * request before it left in the cache: an expiry, a model switch, a
 * compaction or an edited prefix all land here, and all cost a re-write.
 */
export function recordStep(state: CacheState, usage: StepUsage, now: number, ttl: CacheTtl): CacheState {
  const prefix = usage.input_tokens + usage.cache_read_input_tokens + usage.cache_creation_input_tokens
  // The first request has no prefix before it, so it is never a miss.
  const isMiss = state.prefixTokens >= MIN_CACHEABLE && usage.cache_read_input_tokens < state.prefixTokens / 2
  return {
    lastAt: now,
    ttl,
    prefixTokens: prefix,
    nextTokens: prefix + usage.output_tokens,
    read: state.read + usage.cache_read_input_tokens,
    written: state.written + usage.cache_creation_input_tokens,
    uncached: state.uncached + usage.input_tokens,
    requests: state.requests + 1,
    misses: state.misses + (isMiss ? 1 : 0),
  }
}

/** Share of all prompt tokens this session that the cache served, as a whole percentage. */
export function hitPercent(state: CacheState): number {
  const total = state.read + state.written + state.uncached
  return total === 0 ? 0 : Math.round((state.read / total) * 100)
}

export function view(state: CacheState, now: number): View {
  if (state.lastAt === null) return { kind: 'none' }
  const total = TTL_MS[state.ttl]
  const leftMs = state.lastAt + total - now
  if (leftMs <= 0) return { kind: 'cold', tokens: state.nextTokens }
  const fraction = Math.min(1, leftMs / total)
  return {
    kind: 'warm',
    level: fraction < LOW_FRACTION ? 'low' : 'ok',
    ttl: state.ttl,
    leftMs,
    fraction,
    hitPercent: hitPercent(state),
    misses: state.misses,
  }
}

/** `59m left` above a minute, `53s left` under it; never rounds up to the full TTL's next unit. */
export function leftText(leftMs: number): string {
  const seconds = Math.max(1, Math.ceil(leftMs / 1000))
  return seconds > 60 ? `${Math.floor(seconds / 60)}m left` : `${seconds}s left`
}

export function tokensText(tokens: number): string {
  if (tokens >= 1_000_000) return `${(tokens / 1_000_000).toFixed(1)}M`
  return tokens >= 1000 ? `${Math.round(tokens / 1000)}k` : String(tokens)
}

/** Estimated write fee for re-caching tokens at Claude 3.5 Sonnet's write rate ($3.75 / M tokens). */
export function writeFeeText(tokens: number): string {
  if (tokens <= 0) return ''
  const fee = (tokens / 1_000_000) * 3.75
  return fee < 0.01 ? '<$0.01 fee' : `~$${fee.toFixed(2)} fee`
}

/** The bar's two runs: at least one filled cell while any time is left. */
export function bar(fraction: number, cells: number = BAR_CELLS): { filled: string; empty: string } {
  const n = Math.min(cells, Math.max(1, Math.round(fraction * cells)))
  return { filled: '█'.repeat(n), empty: '░'.repeat(cells - n) }
}

/** The band as one plain string: what the timer compares to know a redraw is due, and what /cache prints first. */
export function bandText(v: View): string {
  if (v.kind === 'none') return ''
  if (v.kind === 'cold') {
    const fee = writeFeeText(v.tokens)
    return `cache ○ cold · next message re-caches ${tokensText(v.tokens)} tokens${fee ? ` (${fee})` : ''}`
  }
  const b = bar(v.fraction)
  return `cache ● ${v.ttl} ${b.filled}${b.empty} ${leftText(v.leftMs)} · hit ${v.hitPercent}% · misses ${v.misses}`
}

export function reportText(state: CacheState, now: number, ttlSource: string): string {
  const v = view(state, now)
  if (v.kind === 'none') return 'cure-cache-band: no model response yet this session, so nothing is cached that the band has seen.'
  return [
    bandText(v),
    `  TTL assumed           ${state.ttl} (${ttlSource})`,
    `  Requests (main)       ${state.requests}, ${state.misses} missed`,
    `  Read from cache       ${tokensText(state.read)} tokens`,
    `  Written to cache      ${tokensText(state.written)} tokens`,
    `  Uncached input        ${tokensText(state.uncached)} tokens`,
    `  Next message re-sends ${tokensText(state.nextTokens)} tokens${v.kind === 'cold' ? `, all at the cache-write rate (${writeFeeText(state.nextTokens)})` : ''}`,
  ].join('\n')
}
