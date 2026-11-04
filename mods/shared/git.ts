/**
 * Read-only git for cure-lane-board and cure-lane-verifier: every call names its
 * repository (`git -C <dir>`, never the session cwd), never throws, and is
 * bounded, so independent calls can run together under Promise.all.
 *
 * Mods install one folder each: this file is the source, and mods/shared/vendor.py
 * copies it into each consumer's hooks/shared/. Edit it here, then run the script.
 */

export type GitResult = { exitCode: number; stdout: string; stderr: string }

export const GIT_TIMEOUT_MS = 8_000

/** Any process, normalized: a rejection or a malformed answer reads as exit 1. */
export async function run($: any, argv: readonly string[], timeoutMs = GIT_TIMEOUT_MS): Promise<GitResult> {
  try {
    const r = await $.process.run(argv, { timeoutMs })
    return {
      exitCode: typeof r?.exitCode === 'number' ? r.exitCode : 1,
      stdout: typeof r?.stdout === 'string' ? r.stdout : '',
      stderr: typeof r?.stderr === 'string' ? r.stderr : '',
    }
  } catch (err) {
    return { exitCode: 1, stdout: '', stderr: err instanceof Error ? err.message : String(err) }
  }
}

/** `git -C <dir> <args>`. */
export async function git($: any, dir: string, args: readonly string[]): Promise<GitResult> {
  return run($, ['git', '-C', dir, ...args])
}

/** Several git calls in one repository at once; results in the order asked. */
export async function gitAll($: any, dir: string, calls: readonly (readonly string[])[]): Promise<GitResult[]> {
  return Promise.all(calls.map(args => git($, dir, args)))
}
