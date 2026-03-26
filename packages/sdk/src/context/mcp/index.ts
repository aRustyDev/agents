import type { ParsedComponent, ValidationResult } from '../component'
import type { ComponentTypeModule } from '../registry'
import { parseMcpClient, parseMcpServer, parseMcpTool } from './parser'
import {
  mcpClientSchemaValidator,
  mcpServerSchemaValidator,
  mcpToolSchemaValidator,
} from './schema'
import type { McpClientConfig, McpServerConfig, McpToolConfig } from './types'

function validateMcpComponent(
  component: ParsedComponent<Record<string, unknown>>
): ValidationResult {
  const errors = []
  if (!component.frontmatter.name) {
    errors.push({
      path: 'frontmatter.name',
      message: 'name is required',
      severity: 'error' as const,
    })
  }
  return { valid: errors.length === 0, errors, warnings: [] }
}

export const mcpServerModule: ComponentTypeModule<McpServerConfig> = {
  type: 'mcp-server',
  schema: mcpServerSchemaValidator,
  parse: parseMcpServer,
  validate: validateMcpComponent as (
    component: ParsedComponent<McpServerConfig>
  ) => ValidationResult,
}

export const mcpClientModule: ComponentTypeModule<McpClientConfig> = {
  type: 'mcp-client',
  schema: mcpClientSchemaValidator,
  parse: parseMcpClient,
  validate: validateMcpComponent as (
    component: ParsedComponent<McpClientConfig>
  ) => ValidationResult,
}

export const mcpToolModule: ComponentTypeModule<McpToolConfig> = {
  type: 'mcp-tool',
  schema: mcpToolSchemaValidator,
  parse: parseMcpTool,
  validate: validateMcpComponent as (component: ParsedComponent<McpToolConfig>) => ValidationResult,
}

export { parseMcpClient, parseMcpServer, parseMcpTool } from './parser'
export {
  mcpClientSchemaValidator,
  mcpServerSchemaValidator,
  mcpToolSchemaValidator,
} from './schema'
export type { McpClientConfig, McpServerConfig, McpToolConfig } from './types'
