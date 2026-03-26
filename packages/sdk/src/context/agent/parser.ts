import { readFile } from 'node:fs/promises'
import { basename } from 'node:path'
import { err, ok, type Result } from '@agents/core/types'
import { SdkError } from '../../util/errors'
import type { ParsedComponent } from '../component'
import { computeBasicMetadata, parseFrontmatter } from '../frontmatter'
import { agentSchemaValidator } from './schema'
import type { AgentFrontmatter } from './types'

export async function parseAgent(path: string): Promise<Result<ParsedComponent<AgentFrontmatter>>> {
  let content: string
  try {
    content = await readFile(path, 'utf-8')
  } catch (e) {
    return err(
      new SdkError(`Failed to read agent file: ${path}`, 'E_COMPONENT_NOT_FOUND', String(e))
    )
  }

  const { attrs, body } = parseFrontmatter(content)
  const validated = agentSchemaValidator.validate(attrs)
  if (!validated.ok) return validated

  const metadata = computeBasicMetadata(content, body)
  const name = validated.value.name || basename(path, '.md')

  return ok({
    type: 'agent' as const,
    name,
    content,
    frontmatter: validated.value,
    metadata,
  })
}
