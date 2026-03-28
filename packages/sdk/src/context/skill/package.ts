/**
 * Package a skill directory into a zip for distribution/installation.
 */

import { basename, join } from 'node:path'
import { zipDirectory } from '@agents/core/archive'
import { pathExists } from '@agents/core/file-io'
import { err, ok, type Result } from '@agents/core/types'
import { SdkError } from '../../util/errors'

export interface PackageResult {
  zipPath: string
  skillName: string
  fileCount: number
}

/**
 * Package a skill directory into a distributable zip.
 *
 * The zip contains the skill's files (SKILL.md + any resources)
 * at the top level, ready for extraction into a skills directory.
 */
export async function packageSkill(
  skillDir: string,
  outputPath?: string,
  opts?: { exclude?: string[] }
): Promise<Result<PackageResult>> {
  // Verify SKILL.md exists
  const skillMd = join(skillDir, 'SKILL.md')
  if (!pathExists(skillMd)) {
    return err(
      new SdkError(
        `No SKILL.md found in ${skillDir}`,
        'E_VALIDATION_FAILED',
        'A skill directory must contain a SKILL.md file'
      )
    )
  }

  const skillName = basename(skillDir)
  const zipPath = outputPath ?? join(skillDir, '..', `${skillName}.zip`)
  const excludes = ['.git/*', '.DS_Store', 'node_modules/*', ...(opts?.exclude ?? [])]

  const result = await zipDirectory(skillDir, zipPath, { exclude: excludes })
  if (!result.ok) return result as Result<never>

  return ok({
    zipPath: result.value.path,
    skillName,
    fileCount: result.value.fileCount,
  })
}
