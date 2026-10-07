export type CacheTtl = '5m' | '1h'

export type CacheState = {
  /** When the last main-thread response arrived, in `$.clock.now()`'s milliseconds; null before the first. */
  lastAt: number | null
  /** The TTL assumed for the entry that response wrote or refreshed. */
  ttl: CacheTtl
  /** Prompt tokens the last request was answered over: what a warm cache holds. */
  prefixTokens: number
  /** Prompt tokens the next request re-sends: the prefix plus the last response's output. */
  nextTokens: number
  /** Session totals over main-thread requests. */
  read: number
  written: number
  uncached: number
  requests: number
  misses: number
}

declare module 'claude-code' {
  interface PluginState {
    'cure-cache-band': { cache: CacheState }
  }
}
