import type { Result } from '@agents/core/types'
import type { ParsedComponent, SchemaValidator, ValidationResult } from './component'
import type { ComponentType } from './types'

export interface ComponentTypeModule<T extends Record<string, unknown> = Record<string, unknown>> {
  readonly type: ComponentType
  readonly schema: SchemaValidator<T>
  parse(path: string): Promise<Result<ParsedComponent<T>>>
  validate(component: ParsedComponent<T>): ValidationResult
}

const modules = new Map<ComponentType, ComponentTypeModule>()

export function registerComponentType<T extends Record<string, unknown>>(
  mod: ComponentTypeModule<T>
): void {
  modules.set(mod.type, mod as ComponentTypeModule)
}

export function getComponentModule(type: ComponentType): ComponentTypeModule | undefined {
  return modules.get(type)
}

export function getRegisteredModules(): Map<ComponentType, ComponentTypeModule> {
  return new Map(modules)
}
