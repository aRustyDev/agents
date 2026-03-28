export interface PluginAuthor {
  name: string
  email?: string
  url?: string
}

export interface PluginManifest {
  name: string
  version: string
  description: string
  author?: PluginAuthor
  homepage?: string
  repository?: string
  license?: string
  keywords?: string[]
  commands?: string[]
  agents?: string[]
  skills?: string[]
  outputStyles?: string[]
}

export interface PluginSourceDef {
  source: string
  hash?: string
  forked?: boolean
  forked_at?: string
}

export interface BuildResult {
  ok: boolean
  outputDir?: string
  error?: string
}
