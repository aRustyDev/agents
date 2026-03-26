import * as v from 'valibot'
import { createSchemaValidator } from '../validator'

export const RuleFrontmatterSchema = v.object({
  name: v.string(),
  description: v.optional(v.string()),
  tags: v.optional(v.array(v.string())),
})

export const ruleSchemaValidator = createSchemaValidator(RuleFrontmatterSchema)
