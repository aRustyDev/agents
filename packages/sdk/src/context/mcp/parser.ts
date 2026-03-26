import { readFile } from 'node:fs/promises'
import { basename } from 'node:path'
import { err, ok, type Result } from '@agents/core/types'
import { SdkError } from '../../util/errors'
import type { ParsedComponent } from '../component'
import {
  mcpClientSchemaValidator,
  mcpServerSchemaValidator,
  mcpToolSchemaValidator,
} from './schema'
import type { McpClientConfig, McpServerConfig, McpToolConfig } from './types'

async function readJsonFile(path: string): Promise<Result<Record<string, unknown>>> {
  let content: string
  try {
    content = await readFile(path, 'utf-8')
  } catch (e) {
    return err(
      new SdkError(`Failed to read MCP config file: ${path}`, 'E_COMPONENT_NOT_FOUND', String(e))
    )
  }
  try {
    return ok(JSON.parse(content) as Record<string, unknown>)
  } catch (e) {
    return err(new SdkError(`Invalid JSON in ${path}`, 'E_SCHEMA_INVALID', String(e)))
  }
}

function jsonMetadata(content: string) {
  const lines = content.split('\n')
  return {
    wordCount: content.split(/\s+/).filter(Boolean).length,
    sectionCount: 0,
    headingTree: [] as Array<{ depth: number; title: string }>,
    lineCount: lines.length,
  }
}

export async function parseMcpServer(
  path: string
): Promise<Result<ParsedComponent<McpServerConfig>>> {
  const raw = await readJsonFile(path)
  if (!raw.ok) return raw

  let content: string
  try {
    content = await readFile(path, 'utf-8')
  } catch {
    content = JSON.stringify(raw.value)
  }

  const validated = mcpServerSchemaValidator.validate(raw.value)
  if (!validated.ok) return validated

  const name = validated.value.name || basename(path, '.json')
  return ok({
    type: 'mcp-server' as const,
    name,
    content,
    frontmatter: validated.value,
    metadata: jsonMetadata(content),
  })
}

export async function parseMcpClient(
  path: string
): Promise<Result<ParsedComponent<McpClientConfig>>> {
  const raw = await readJsonFile(path)
  if (!raw.ok) return raw

  let content: string
  try {
    content = await readFile(path, 'utf-8')
  } catch {
    content = JSON.stringify(raw.value)
  }

  const validated = mcpClientSchemaValidator.validate(raw.value)
  if (!validated.ok) return validated

  const name = validated.value.name || basename(path, '.json')
  return ok({
    type: 'mcp-client' as const,
    name,
    content,
    frontmatter: validated.value,
    metadata: jsonMetadata(content),
  })
}

export async function parseMcpTool(path: string): Promise<Result<ParsedComponent<McpToolConfig>>> {
  const raw = await readJsonFile(path)
  if (!raw.ok) return raw

  let content: string
  try {
    content = await readFile(path, 'utf-8')
  } catch {
    content = JSON.stringify(raw.value)
  }

  const validated = mcpToolSchemaValidator.validate(raw.value)
  if (!validated.ok) return validated

  const name = validated.value.name || basename(path, '.json')
  return ok({
    type: 'mcp-tool' as const,
    name,
    content,
    frontmatter: validated.value,
    metadata: jsonMetadata(content),
  })
}
