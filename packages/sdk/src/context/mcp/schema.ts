import * as v from 'valibot'
import { createSchemaValidator } from '../validator'

export const McpServerConfigSchema = v.object({
  name: v.string(),
  command: v.string(),
  args: v.optional(v.array(v.string())),
  env: v.optional(v.record(v.string(), v.string())),
  description: v.optional(v.string()),
  tags: v.optional(v.array(v.string())),
})

export const McpClientConfigSchema = v.object({
  name: v.string(),
  description: v.optional(v.string()),
  serverUrl: v.optional(v.string()),
  tags: v.optional(v.array(v.string())),
})

export const McpToolConfigSchema = v.object({
  name: v.string(),
  description: v.optional(v.string()),
  serverName: v.optional(v.string()),
  tags: v.optional(v.array(v.string())),
})

export const mcpServerSchemaValidator = createSchemaValidator(McpServerConfigSchema)
export const mcpClientSchemaValidator = createSchemaValidator(McpClientConfigSchema)
export const mcpToolSchemaValidator = createSchemaValidator(McpToolConfigSchema)
