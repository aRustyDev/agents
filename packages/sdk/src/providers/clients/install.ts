/**
 * Install a skill to a specific AI client's skills directory.
 */

import { homedir } from 'node:os'
import { join } from 'node:path'
import { unzip } from '@agents/core/archive'
import { ensureDir, pathExists } from '@agents/core/file-io'
import { err, ok, type Result } from '@agents/core/types'
import { SdkError } from '../../util/errors'

export interface InstallTarget {
  clientId: string
  skillsDir: string
}

export interface InstallResult {
  target: InstallTarget
  skillName: string
  installedPath: string
  fileCount: number
}

/** Known client skill directories. */
const CLIENT_SKILLS_DIRS: Record<string, () => string> = {
  'claude-code': () => join(homedir(), '.claude', 'skills'),
  'claude-desktop': () => join(homedir(), '.claude', 'skills'), // shares with Claude Code
}

/** Get the skills directory for a client. */
export function getClientSkillsDir(clientId: string): string | undefined {
  return CLIENT_SKILLS_DIRS[clientId]?.()
}

/** List known client IDs that support skill installation. */
export function getInstallableClients(): string[] {
  return Object.keys(CLIENT_SKILLS_DIRS)
}

/**
 * Install a skill zip to a client's skills directory.
 *
 * Extracts the zip into {skillsDir}/{skillName}/.
 * If the skill already exists, it is overwritten.
 */
export async function installSkillToClient(
  zipPath: string,
  skillName: string,
  clientId: string
): Promise<Result<InstallResult>> {
  const skillsDir = getClientSkillsDir(clientId)
  if (!skillsDir) {
    return err(
      new SdkError(
        `Unknown client: ${clientId}`,
        'E_PROVIDER_UNAVAILABLE',
        `Supported clients: ${getInstallableClients().join(', ')}`
      )
    )
  }

  if (!pathExists(zipPath)) {
    return err(new SdkError(`Zip not found: ${zipPath}`, 'E_COMPONENT_NOT_FOUND'))
  }

  const installDir = join(skillsDir, skillName)
  const dirResult = await ensureDir(installDir)
  if (!dirResult.ok) return dirResult as Result<never>

  const extracted = await unzip(zipPath, installDir)
  if (!extracted.ok) return extracted as Result<never>

  return ok({
    target: { clientId, skillsDir },
    skillName,
    installedPath: installDir,
    fileCount: extracted.value.length,
  })
}
