/**
 * Generic component scaffolding.
 *
 * Copies a template directory and replaces `{{name}}` placeholders in all
 * files. Used by `agents init <type> <name>` for types that have a
 * `templateDir` defined in their ComponentTypeMetadata.
 */

import { join, resolve } from 'node:path'
import { type ComponentType, getComponentMeta } from '@agents/core/component/types'
import {
  ensureDir,
  listDirectory,
  pathExists,
  readTextFile,
  writeTextFile,
} from '@agents/core/file-io'
import { currentDir } from '@agents/core/runtime'
import { CliError, err, ok, type Result } from '@agents/core/types'

const PROJECT_ROOT = resolve(currentDir(import.meta), '../../../..')

export async function initComponent(
  type: ComponentType,
  name: string,
  opts?: { cwd?: string }
): Promise<Result<{ path: string; files: string[] }>> {
  const meta = getComponentMeta(type)
  if (!meta.templateDir) {
    return err(
      new CliError(
        `No template for type '${type}'. Use a type-specific init command.`,
        'E_NO_TEMPLATE'
      )
    )
  }
  const templatePath = join(PROJECT_ROOT, meta.templateDir)
  if (!pathExists(templatePath)) {
    return err(new CliError(`Template not found: ${templatePath}`, 'E_TEMPLATE_MISSING'))
  }
  const outputDir = join(opts?.cwd ?? process.cwd(), name)
  if (pathExists(outputDir)) {
    return err(new CliError(`Already exists: ${outputDir}`, 'E_EXISTS'))
  }
  const dirResult = await ensureDir(outputDir)
  if (!dirResult.ok) return dirResult as Result<never>

  const entries = await listDirectory(templatePath)
  if (!entries.ok) return entries as Result<never>

  const files: string[] = []
  for (const entry of entries.value) {
    if (entry.isFile()) {
      const content = await readTextFile(join(templatePath, entry.name))
      if (content.ok) {
        await writeTextFile(
          join(outputDir, entry.name),
          content.value.replace(/\{\{name\}\}/g, name)
        )
        files.push(entry.name)
      }
    }
  }
  return ok({ path: outputDir, files })
}
