import { readFile } from 'node:fs/promises'
import { basename, extname } from 'node:path'
import { err, ok, type Result } from '@agents/core/types'
import { SdkError } from '../../util/errors'
import type { ParsedComponent } from '../component'
import type { HookFrontmatter } from './types'

/**
 * Parse a hook file. Hooks are shell scripts or JSON configs, so we extract
 * the name from the filename rather than YAML frontmatter.
 */
export async function parseHook(path: string): Promise<Result<ParsedComponent<HookFrontmatter>>> {
  let content: string
  try {
    content = await readFile(path, 'utf-8')
  } catch (e) {
    return err(
      new SdkError(`Failed to read hook file: ${path}`, 'E_COMPONENT_NOT_FOUND', String(e))
    )
  }

  const ext = extname(path)
  const name = basename(path, ext)
  const lines = content.split('\n')

  return ok({
    type: 'hook' as const,
    name,
    content,
    frontmatter: { name } as HookFrontmatter,
    metadata: {
      wordCount: content.split(/\s+/).filter(Boolean).length,
      sectionCount: 0,
      headingTree: [],
      lineCount: lines.length,
    },
  })
}
