export interface LspServerEntry {
  command: string
  args?: string[]
  extensionToLanguage: Record<string, string>
}

export interface LspConfig {
  lspServers: Record<string, LspServerEntry>
}
