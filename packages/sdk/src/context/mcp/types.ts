export interface McpServerConfig {
  name: string
  command: string
  args?: string[]
  env?: Record<string, string>
  description?: string
  tags?: string[]
}

export interface McpClientConfig {
  name: string
  description?: string
  serverUrl?: string
  tags?: string[]
}

export interface McpToolConfig {
  name: string
  description?: string
  serverName?: string
  tags?: string[]
}
