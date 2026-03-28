import { readFile } from 'node:fs/promises'
import { basename, dirname } from 'node:path'
import { err, ok, type Result } from '@agents/core/types'
import { SdkError } from '../../util/errors'
import type { ParsedComponent } from '../component'
import { pluginSchemaValidator } from './schema'
import type { PluginManifest } from './types'

export async function parsePlugin(path: string): Promise<Result<ParsedComponent<PluginManifest>>> {
  let content: string
  try {
    content = await readFile(path, 'utf-8')
  } catch (e) {
    return err(
      new SdkError(`Failed to read plugin manifest: ${path}`, 'E_COMPONENT_NOT_FOUND', String(e))
    )
  }

  let data: unknown
  try {
    data = JSON.parse(content)
  } catch (e) {
    return err(new SdkError(`Invalid JSON in ${path}`, 'E_SCHEMA_INVALID', String(e)))
  }

  const validated = pluginSchemaValidator.validate(data)
  if (!validated.ok) return validated

  const lines = content.split('\n')
  const name = validated.value.name || basename(dirname(path))

  return ok({
    type: 'plugin' as const,
    name,
    content,
    frontmatter: validated.value,
    metadata: {
      wordCount: content.split(/\s+/).filter(Boolean).length,
      sectionCount: 0,
      headingTree: [],
      lineCount: lines.length,
    },
  })
}
