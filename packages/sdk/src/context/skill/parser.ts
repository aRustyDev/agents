import { readFile } from 'node:fs/promises'
import { basename, dirname } from 'node:path'
import { err, ok, type Result } from '@agents/core/types'
import { SdkError } from '../../util/errors'
import type { ParsedComponent } from '../component'
import { computeBasicMetadata, parseFrontmatter } from '../frontmatter'
import { skillSchemaValidator } from './schema'
import type { SkillFrontmatter } from './types'

export async function parseSkill(path: string): Promise<Result<ParsedComponent<SkillFrontmatter>>> {
  let content: string
  try {
    content = await readFile(path, 'utf-8')
  } catch (e) {
    return err(
      new SdkError(`Failed to read skill file: ${path}`, 'E_COMPONENT_NOT_FOUND', String(e))
    )
  }

  const { attrs, body } = parseFrontmatter(content)
  const validated = skillSchemaValidator.validate(attrs)
  if (!validated.ok) return validated

  const metadata = computeBasicMetadata(content, body)
  const name = validated.value.name || basename(dirname(path))

  return ok({
    type: 'skill' as const,
    name,
    content,
    frontmatter: validated.value,
    metadata,
  })
}
