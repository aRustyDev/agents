import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { registerDatabaseTools } from '../../examples/database-tools'
import type { Props } from '../types'

/**
 * Register all MCP tools based on user permissions
 */
export function registerAllTools(server: McpServer, env: Env, props: Props) {
  // Register database tools
  registerDatabaseTools(server, env, props)

  // Future tools can be registered here
  // registerOtherTools(server, env, props);
}
