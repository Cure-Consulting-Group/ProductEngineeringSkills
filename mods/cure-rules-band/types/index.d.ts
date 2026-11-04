/** The house rules of the repository the session is in; null when it has none. */
export type ActiveRules = { repo: string; rules: string[]; root: string }

declare module 'claude-code' {
  interface PluginState {
    'cure-rules-band': { active: ActiveRules | null; isHidden: boolean }
  }
}
