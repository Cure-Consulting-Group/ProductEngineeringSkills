import type { On } from 'claude-code'

import {
  formatRulesReport,
  resolveRepoRules,
} from './banner'

const CONFIG_PATH = '.cure/rules.json'

async function getRepoName($: any): Promise<string> {
  const res = await $.process.run(['git', 'rev-parse', '--show-toplevel'])
  if (res && res.exitCode === 0 && res.stdout) {
    return res.stdout.trim().split('/').pop() || 'Workspace'
  }
  return 'Workspace'
}

async function getActiveRules($: any): Promise<{ repo: string; rules: string[] }> {
  const repo = await getRepoName($)
  let configText: string | undefined
  const exists = await $.fs.exists(CONFIG_PATH)
  if (exists) {
    configText = await $.fs.read(CONFIG_PATH)
  }
  return resolveRepoRules(repo, configText)
}

export function register(on: On) {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'rules',
      description: 'Show active architectural and legal house rules for this repository',
    })
    return next(e)
  })

  on('command.run', { command: 'rules' }, async $ => {
    const { repo, rules } = await getActiveRules($)
    return { text: formatRulesReport(repo, rules) }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)

    const { repo, rules } = await getActiveRules($)
    const { Box, Text } = $.ui.resolve(e)

    return (
      <Box>
        <Text color="cyan">rules ● {repo}</Text>
        <Text dimColor> · {rules.join(' · ')}</Text>
      </Box>
    )
  })
}
