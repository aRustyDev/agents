import { err, type Result } from '@agents/core/types'
import { SdkError } from '../util/errors'
import type { ParsedComponent } from './component'
import { getComponentModule } from './registry'
import type { ComponentType } from './types'

export async function parseComponent(
  type: ComponentType,
  path: string
): Promise<Result<ParsedComponent>> {
  const mod = getComponentModule(type)
  if (!mod) return err(new SdkError(`No parser registered for '${type}'`, 'E_COMPONENT_NOT_FOUND'))
  return mod.parse(path)
}
