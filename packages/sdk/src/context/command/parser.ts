import { readFile } from 'node:fs/promises'
import { basename } from 'node:path'
import { err, ok, type Result } from '@agents/core/types'
import { SdkError } from '../../util/errors'
import type { ParsedComponent } from '../component'
import { computeBasicMetadata, parseFrontmatter } from '../frontmatter'
import { commandSchemaValidator } from './schema'
import type { CommandFrontmatter } from './types'

export async function parseCommand(
  path: string
): Promise<Result<ParsedComponent<CommandFrontmatter>>> {
  let content: string
  try {
    content = await readFile(path, 'utf-8')
  } catch (e) {
    return err(
      new SdkError(`Failed to read command file: ${path}`, 'E_COMPONENT_NOT_FOUND', String(e))
    )
  }

  const { attrs, body } = parseFrontmatter(content)
  const validated = commandSchemaValidator.validate(attrs)
  if (!validated.ok) return validated

  const metadata = computeBasicMetadata(content, body)
  const name = validated.value.name || basename(path, '.md')

  return ok({
    type: 'command' as const,
    name,
    content,
    frontmatter: validated.value,
    metadata,
  })
}
