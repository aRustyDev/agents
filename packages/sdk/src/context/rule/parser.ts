import { readFile } from 'node:fs/promises'
import { basename } from 'node:path'
import { err, ok, type Result } from '@agents/core/types'
import { SdkError } from '../../util/errors'
import type { ParsedComponent } from '../component'
import { computeBasicMetadata, parseFrontmatter } from '../frontmatter'
import { ruleSchemaValidator } from './schema'
import type { RuleFrontmatter } from './types'

export async function parseRule(path: string): Promise<Result<ParsedComponent<RuleFrontmatter>>> {
  let content: string
  try {
    content = await readFile(path, 'utf-8')
  } catch (e) {
    return err(
      new SdkError(`Failed to read rule file: ${path}`, 'E_COMPONENT_NOT_FOUND', String(e))
    )
  }

  const { attrs, body } = parseFrontmatter(content)
  const validated = ruleSchemaValidator.validate(attrs)
  if (!validated.ok) return validated

  const metadata = computeBasicMetadata(content, body)
  const name = validated.value.name || basename(path, '.md')

  return ok({
    type: 'rule' as const,
    name,
    content,
    frontmatter: validated.value,
    metadata,
  })
}
