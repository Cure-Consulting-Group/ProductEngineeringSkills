/**
 * Pure functions for parsing multi-machine state claims and verifying file write permissions.
 */

export function parseStateTargets(content: string): Map<string, string> {
  const claims = new Map<string, string>()
  if (!content || typeof content !== 'string') return claims

  const lines = content.split('\n')
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed.startsWith('|')) continue

    const cells = trimmed
      .split('|')
      .map(c => c.trim())
      .filter(c => c.length > 0)

    // Expected shape: | State | Owner | ... |
    if (cells.length >= 2) {
      const state = cells[0].toUpperCase()
      const owner = cells[1].toLowerCase()
      // Skip header row
      if (state === 'STATE' || state === '---' || state.startsWith('---')) continue
      if (/^[A-Z]{2}$/.test(state)) {
        claims.set(state, owner)
      }
    }
  }

  return claims
}

const STATE_PATH_REGEX = /(?:scripts\/(?:build|lib|data)[-_/])([a-zA-Z]{2})(?:[-_./]|$)/i

export function detectStateFromPath(path: string): string | undefined {
  if (!path) return undefined
  const match = path.match(STATE_PATH_REGEX)
  if (match) {
    return match[1].toUpperCase()
  }
  return undefined
}

export type ClaimVerdict = {
  allowed: boolean
  state: string
  owner?: string
  reason?: string
}

export function evaluateClaim(
  state: string,
  currentHost: string,
  claims: Map<string, string>,
): ClaimVerdict {
  const owner = claims.get(state.toUpperCase())
  if (!owner) {
    return {
      allowed: true,
      state,
    }
  }

  const host = (currentHost || '').trim().toLowerCase()
  const cleanOwner = owner.trim().toLowerCase()

  const matches = host.includes(cleanOwner) || cleanOwner.includes(host)
  if (!matches) {
    return {
      allowed: false,
      state,
      owner,
      reason: `State row '${state}' is owned by '${owner}', but current machine is '${host}'. Never build a row another machine owns.`,
    }
  }

  return {
    allowed: true,
    state,
    owner,
  }
}

export function formatClaimsReport(currentHost: string, claims: Map<string, string>): string {
  if (claims.size === 0) {
    return `cure-claim-guard: No state targets configured in .agents/state-targets.md. Machine: ${currentHost}`
  }

  const lines = [
    `cure-claim-guard: Machine '${currentHost}' tracking ${claims.size} state claim(s):`,
  ]

  const host = currentHost.toLowerCase()
  let localCount = 0
  for (const [st, owner] of claims.entries()) {
    const isMine = host.includes(owner) || owner.includes(host)
    if (isMine) localCount++
    lines.push(`  • ${st}: ${owner}${isMine ? ' (this machine)' : ''}`)
  }

  lines.push(`Total owned by this machine: ${localCount}`)
  return lines.join('\n')
}
