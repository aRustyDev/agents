/**
 * Shell completion script generator.
 *
 * `agents completions bash|zsh|fish` — prints a completion script to stdout.
 * Users can eval or source the output in their shell profile.
 */

import { EXIT } from '@agents/core/types'
import { COMPONENT_TYPES } from '@agents/sdk/context/types'
import { createOutput } from '@agents/sdk/ui'
import { defineCommand } from 'citty'
import { globalArgs } from './shared-args'

// ---------------------------------------------------------------------------
// Completion data — derived from the type system, not hardcoded
// ---------------------------------------------------------------------------

const VERBS = ['add', 'remove', 'list', 'search', 'info', 'init', 'lint', 'update']
const NOUNS = [
  'catalog',
  'config',
  'plugin',
  'skill',
  'mcp',
  'component',
  'kg',
  'registry',
  'graph-viewer',
  'completions',
]
const ALL_COMMANDS = [...VERBS, ...NOUNS]
const CATALOG_SUBS = [
  'analyze',
  'summary',
  'forks',
  'cleanup',
  'errors',
  'scrub',
  'stale',
  'backfill',
  'discover',
]
const CONFIG_SUBS = ['get', 'set', 'list', 'edit', 'path']
const TYPES = [...COMPONENT_TYPES]

// ---------------------------------------------------------------------------
// Generators
// ---------------------------------------------------------------------------

export function generateBash(): string {
  const cmds = ALL_COMMANDS.join(' ')
  const types = TYPES.join(' ')
  const catalogSubs = CATALOG_SUBS.join(' ')
  const configSubs = CONFIG_SUBS.join(' ')

  return `# bash completion for agents CLI
# Add to ~/.bashrc: eval "$(agents completions bash)"
_agents_completions() {
  local cur prev words cword
  _init_completion || return

  local commands="${cmds}"
  local types="${types}"
  local catalog_subs="${catalogSubs}"
  local config_subs="${configSubs}"

  case "\${words[1]}" in
    add|remove|list|search|info|init|lint|update)
      if [[ $cword -eq 2 ]]; then
        COMPREPLY=( $(compgen -W "$types" -- "$cur") )
        return
      fi
      ;;
    catalog)
      if [[ $cword -eq 2 ]]; then
        COMPREPLY=( $(compgen -W "$catalog_subs" -- "$cur") )
        return
      fi
      ;;
    config)
      if [[ $cword -eq 2 ]]; then
        COMPREPLY=( $(compgen -W "$config_subs" -- "$cur") )
        return
      fi
      ;;
    completions)
      if [[ $cword -eq 2 ]]; then
        COMPREPLY=( $(compgen -W "bash zsh fish" -- "$cur") )
        return
      fi
      ;;
  esac

  if [[ $cword -eq 1 ]]; then
    COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
  fi
}
complete -F _agents_completions agents
`
}

export function generateZsh(): string {
  const cmds = ALL_COMMANDS.map((c) => `'${c}'`).join(' ')
  const types = TYPES.map((t) => `'${t}'`).join(' ')
  const catalogSubs = CATALOG_SUBS.map((s) => `'${s}'`).join(' ')
  const configSubs = CONFIG_SUBS.map((s) => `'${s}'`).join(' ')

  return `#compdef agents
# zsh completion for agents CLI
# Add to ~/.zshrc: eval "$(agents completions zsh)"
_agents() {
  local -a commands types catalog_subs config_subs

  commands=(${cmds})
  types=(${types})
  catalog_subs=(${catalogSubs})
  config_subs=(${configSubs})

  if (( CURRENT == 2 )); then
    _describe 'command' commands
    return
  fi

  case "$words[2]" in
    add|remove|list|search|info|init|lint|update)
      if (( CURRENT == 3 )); then
        _describe 'component type' types
      fi
      ;;
    catalog)
      if (( CURRENT == 3 )); then
        _describe 'catalog subcommand' catalog_subs
      fi
      ;;
    config)
      if (( CURRENT == 3 )); then
        _describe 'config subcommand' config_subs
      fi
      ;;
    completions)
      if (( CURRENT == 3 )); then
        _describe 'shell' '(bash zsh fish)'
      fi
      ;;
  esac
}
compdef _agents agents
`
}

export function generateFish(): string {
  const lines: string[] = [
    '# fish completion for agents CLI',
    '# Add to ~/.config/fish/completions/agents.fish or eval: agents completions fish | source',
    '',
    '# Disable file completions by default',
    'complete -c agents -f',
    '',
    '# Top-level commands',
  ]

  for (const cmd of ALL_COMMANDS) {
    lines.push(`complete -c agents -n '__fish_use_subcommand' -a '${cmd}'`)
  }

  lines.push('')
  lines.push('# Component types for verb commands')
  for (const verb of VERBS) {
    for (const type of TYPES) {
      lines.push(`complete -c agents -n '__fish_seen_subcommand_from ${verb}' -a '${type}'`)
    }
  }

  lines.push('')
  lines.push('# Catalog subcommands')
  for (const sub of CATALOG_SUBS) {
    lines.push(`complete -c agents -n '__fish_seen_subcommand_from catalog' -a '${sub}'`)
  }

  lines.push('')
  lines.push('# Config subcommands')
  for (const sub of CONFIG_SUBS) {
    lines.push(`complete -c agents -n '__fish_seen_subcommand_from config' -a '${sub}'`)
  }

  lines.push('')
  lines.push('# Completions subcommands')
  lines.push(`complete -c agents -n '__fish_seen_subcommand_from completions' -a 'bash zsh fish'`)
  lines.push('')

  return lines.join('\n')
}

// ---------------------------------------------------------------------------
// Subcommands
// ---------------------------------------------------------------------------

const bashCmd = defineCommand({
  meta: { name: 'bash', description: 'Generate bash completion script' },
  args: { ...globalArgs },
  run() {
    process.stdout.write(generateBash())
  },
})

const zshCmd = defineCommand({
  meta: { name: 'zsh', description: 'Generate zsh completion script' },
  args: { ...globalArgs },
  run() {
    process.stdout.write(generateZsh())
  },
})

const fishCmd = defineCommand({
  meta: { name: 'fish', description: 'Generate fish completion script' },
  args: { ...globalArgs },
  run() {
    process.stdout.write(generateFish())
  },
})

// ---------------------------------------------------------------------------
// Main command
// ---------------------------------------------------------------------------

export default defineCommand({
  meta: { name: 'completions', description: 'Generate shell completion scripts' },
  args: { ...globalArgs },
  subCommands: {
    bash: bashCmd,
    zsh: zshCmd,
    fish: fishCmd,
  },
  async run({ args }) {
    const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
    out.info('Usage: agents completions <bash|zsh|fish>')
    out.info('')
    out.info('Add to your shell profile:')
    out.info('  bash: eval "$(agents completions bash)"')
    out.info('  zsh:  eval "$(agents completions zsh)"')
    out.info('  fish: agents completions fish | source')
    process.exit(EXIT.OK)
  },
})
