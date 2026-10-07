export type Pasted = {
  /** The N of the prompt's `[Image #N]`. */
  id: number
  /** The saved file's absolute path; null when none was found for this id. */
  path: string | null
  /** Pixel size, 0 when it could not be read. */
  width: number
  height: number
}

declare module 'claude-code' {
  interface PluginState {
    'cure-image-viewer': {
      /** Images the draft in the prompt box names. */
      draft: Pasted[]
      /** Images the running turn's prompt carried; cleared when the turn ends. */
      sent: Pasted[]
    }
  }
}
