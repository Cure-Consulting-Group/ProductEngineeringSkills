export type StaleEntry = { path: string; line: number; reason: string }
export type CiteStats = { checked: number; valid: number; stale: number; unverified: number }

declare module 'claude-code' {
  interface PluginState {
    // session-scoped: never the machine-global $.store
    'cure-cite-check': { stats: CiteStats; recentStale: StaleEntry[]; recentPaths: string[] }
  }
}
