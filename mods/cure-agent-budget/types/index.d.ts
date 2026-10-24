/** One subagent this session started and has not yet seen finish. */
export type Tracked = { id: string; description: string; startedAt: number }

/** Counters for /agents-budget; session-scoped, never machine-global. */
export type Stats = { spawned: number; denied: number; routed: number }

declare module 'claude-code' {
  interface PluginState {
    'cure-agent-budget': { active: Tracked[]; stats: Stats }
  }
}
