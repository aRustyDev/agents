import * as v from 'valibot'
import { createSchemaValidator } from '../validator'

export const AgentFrontmatterSchema = v.object({
  name: v.string(),
  description: v.optional(v.string()),
  tools: v.optional(v.array(v.string())),
  tags: v.optional(v.array(v.string())),
})

export const agentSchemaValidator = createSchemaValidator(AgentFrontmatterSchema)
