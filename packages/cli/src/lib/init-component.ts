// Compatibility wrapper — delegates to @agents/sdk/context/scaffold with projectRoot pre-filled
import { resolve } from 'node:path'
import { currentDir } from '@agents/core/runtime'
import type { Result } from '@agents/core/types'
import { initComponent as sdkInitComponent } from '@agents/sdk/context/scaffold'
import type { ComponentType } from '@agents/sdk/context/types'

const PROJECT_ROOT = resolve(currentDir(import.meta), '../../../..')

export async function initComponent(
  type: ComponentType,
  name: string,
  opts?: { cwd?: string }
): Promise<Result<{ path: string; files: string[] }>> {
  return sdkInitComponent(type, name, { ...opts, projectRoot: PROJECT_ROOT })
}
