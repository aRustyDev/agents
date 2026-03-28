import * as v from 'valibot'
import { createSchemaValidator } from '../validator'

export const SkillFrontmatterSchema = v.object({
  name: v.string(),
  description: v.string(),
  version: v.optional(v.string()),
  author: v.optional(v.string()),
  license: v.optional(v.string()),
  tags: v.optional(v.array(v.string())),
  source: v.optional(v.string()),
  created: v.optional(v.string()),
  updated: v.optional(v.string()),
  globs: v.optional(v.array(v.string())),
  'allowed-tools': v.optional(v.string()),
})

/** Alias for backward compat with consumers using the un-suffixed name. */
export const SkillFrontmatter = SkillFrontmatterSchema
export type SkillFrontmatter = v.InferOutput<typeof SkillFrontmatterSchema>

export const skillSchemaValidator = createSchemaValidator(SkillFrontmatterSchema)
