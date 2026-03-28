export interface SkillFrontmatter {
  name: string
  description: string
  version?: string
  author?: string
  license?: string
  tags?: string[]
  source?: string
  created?: string
  updated?: string
  globs?: string[]
  'allowed-tools'?: string
}
