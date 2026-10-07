/**
 * Pure functions for drafting structured STATE.md handoff blocks.
 */

export type HandoffParams = {
  date: string
  branch: string
  commits: string[]
  dirtyFiles: string[]
}

export function formatHandoffDraft(params: HandoffParams): string {
  const lines: string[] = [
    `### Handoff: ${params.date} (${params.branch})`,
    '',
    '**Shipped Commits:**',
  ]

  if (params.commits.length === 0) {
    lines.push('- (No recent commits recorded on this branch)')
  } else {
    for (const c of params.commits) {
      lines.push(`- ${c}`)
    }
  }

  lines.push('')
  lines.push('**Working Tree:**')
  if (params.dirtyFiles.length === 0) {
    lines.push('- Clean (no uncommitted diffs)')
  } else {
    lines.push(`- ${params.dirtyFiles.length} uncommitted file(s):`)
    for (const f of params.dirtyFiles.slice(0, 10)) {
      lines.push(`  • ${f}`)
    }
    if (params.dirtyFiles.length > 10) {
      lines.push(`  • ... and ${params.dirtyFiles.length - 10} more`)
    }
  }

  lines.push('')
  lines.push('**Next Steps & Continuity:**')
  lines.push('- [ ] Verify CI validation check on latest branch push')
  lines.push('- [ ] Review open issues or PRs against main')
  lines.push('')

  return lines.join('\n')
}
