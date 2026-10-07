/**
 * Pure functions for identifying and scrubbing secret credentials from text.
 */

export type SecretMatch = {
  kind: string
  pattern: RegExp
  placeholder: string
}

export const SECRET_RULES: readonly SecretMatch[] = [
  {
    kind: 'Google API key',
    pattern: /AIza[0-9A-Za-z_-]{35}/g,
    placeholder: '[REDACTED:GOOGLE_API_KEY]',
  },
  {
    kind: 'Anthropic API key',
    pattern: /sk-ant-[0-9A-Za-z_-]{20,}/g,
    placeholder: '[REDACTED:ANTHROPIC_API_KEY]',
  },
  {
    kind: 'OpenAI API key',
    pattern: /\bsk-(?:proj-)?[0-9A-Za-z_-]{32,}/g,
    placeholder: '[REDACTED:OPENAI_API_KEY]',
  },
  {
    kind: 'GitHub token',
    pattern: /\b(?:ghp|gho|ghs|ghu)_[0-9A-Za-z]{36}\b|\bgithub_pat_[0-9A-Za-z_]{40,}/g,
    placeholder: '[REDACTED:GITHUB_TOKEN]',
  },
  {
    kind: 'Stripe secret key',
    pattern: /\b(?:sk|rk)_live_[0-9A-Za-z]{20,}/g,
    placeholder: '[REDACTED:STRIPE_SECRET_KEY]',
  },
  {
    kind: 'AWS access key',
    pattern: /\bAKIA[0-9A-Z]{16}\b/g,
    placeholder: '[REDACTED:AWS_ACCESS_KEY]',
  },
  {
    kind: 'Private key block',
    pattern: /-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |)PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |DSA |OPENSSH |PGP |)PRIVATE KEY-----/g,
    placeholder: '[REDACTED:PRIVATE_KEY_BLOCK]',
  },
  {
    kind: 'Service-account private key',
    pattern: /"private_key"\s*:\s*"-----BEGIN[^"]+"/g,
    placeholder: '"private_key": "[REDACTED:SERVICE_ACCOUNT_KEY]"',
  },
]

export type ScrubResult = {
  text: string
  count: number
  kinds: string[]
}

/**
 * Scrubs any secret patterns from input text, replacing them with typed placeholders.
 */
export function scrubText(input: string): ScrubResult {
  if (!input || typeof input !== 'string') {
    return { text: input ?? '', count: 0, kinds: [] }
  }

  let text = input
  let count = 0
  const matchedKinds = new Set<string>()

  for (const rule of SECRET_RULES) {
    const matches = text.match(rule.pattern)
    if (matches && matches.length > 0) {
      count += matches.length
      matchedKinds.add(rule.kind)
      text = text.replace(rule.pattern, rule.placeholder)
    }
  }

  return {
    text,
    count,
    kinds: [...matchedKinds],
  }
}

/**
 * Deeply scrubs secrets from string properties in arbitrary tool output structures.
 */
export function scrubToolOutput(output: any): { output: any; count: number; kinds: string[] } {
  if (output === null || output === undefined) {
    return { output, count: 0, kinds: [] }
  }

  if (typeof output === 'string') {
    const { text, count, kinds } = scrubText(output)
    return { output: text, count, kinds }
  }

  if (Array.isArray(output)) {
    let totalCount = 0
    const allKinds = new Set<string>()
    const mapped = output.map(item => {
      const { output: res, count, kinds } = scrubToolOutput(item)
      totalCount += count
      kinds.forEach(k => allKinds.add(k))
      return res
    })
    return { output: mapped, count: totalCount, kinds: [...allKinds] }
  }

  if (typeof output === 'object') {
    let totalCount = 0
    const allKinds = new Set<string>()
    const copy: Record<string, any> = {}
    for (const [key, value] of Object.entries(output)) {
      const { output: res, count, kinds } = scrubToolOutput(value)
      totalCount += count
      kinds.forEach(k => allKinds.add(k))
      copy[key] = res
    }
    return { output: copy, count: totalCount, kinds: [...allKinds] }
  }

  return { output, count: 0, kinds: [] }
}
