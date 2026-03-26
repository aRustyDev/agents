import { agentModule } from './agent'
import { commandModule } from './command'
import { hookModule } from './hook'
import { mcpClientModule, mcpServerModule, mcpToolModule } from './mcp'
import { outputStyleModule } from './output-style'
import { pluginModule } from './plugin'
import { registerComponentType } from './registry'
import { ruleModule } from './rule'
import { skillModule } from './skill'

// Auto-register all built-in types
for (const mod of [
  skillModule,
  ruleModule,
  hookModule,
  commandModule,
  outputStyleModule,
  agentModule,
  mcpServerModule,
  mcpClientModule,
  mcpToolModule,
  pluginModule,
]) {
  registerComponentType(mod)
}

export * from './component'
export * from './frontmatter'
export * from './parser'
export * from './registry'
export * from './types'
export * from './validator'
