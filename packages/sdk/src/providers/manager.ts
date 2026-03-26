import type { Result } from '@agents/core/types'
import { err, ok } from '@agents/core/types'
import type {
  Component,
  ComponentAddOptions,
  ComponentAddResult,
  ComponentProvider,
  ComponentType,
  PaginatedResult,
  PublishOptions,
  PublishResult,
  RemoveResult,
  SearchParams,
} from '../context/types'
import { SdkError } from '../util/errors'
import { clampLimit, clampPage, emptyPage, paginateArray } from './pagination'

type Operation = 'search' | 'add' | 'list' | 'remove' | 'publish' | 'info' | 'outdated' | 'update'

export class ProviderManager {
  private readonly registry = new Map<string, ComponentProvider>()

  register(provider: ComponentProvider): void {
    this.registry.set(provider.id, provider)
  }

  getProvider(id: string): ComponentProvider | undefined {
    return this.registry.get(id)
  }

  providers(): ComponentProvider[] {
    return [...this.registry.values()]
  }

  findProviders(operation: Operation, type: ComponentType): ComponentProvider[] {
    return this.providers().filter((p) => {
      const supported = p.capabilities[operation]
      return (supported as readonly string[]).includes(type)
    })
  }

  async search(params: SearchParams): Promise<Result<PaginatedResult<Component>>> {
    const limit = clampLimit(params.limit)
    const page = clampPage(params.page)
    const type = params.type

    const providers = type
      ? this.findProviders('search', type)
      : this.providers().filter((p) => p.capabilities.search.length > 0)

    if (providers.length === 0) {
      return ok(emptyPage(page, limit))
    }

    // Fan out to all providers with generous limit, paginate aggregate in-memory
    const fanOutLimit = Math.min(limit * 3, 100)
    const settled = await Promise.allSettled(
      providers.map((p) => p.search({ ...params, limit: fanOutLimit, page: 1 }))
    )

    const allItems: Component[] = []
    for (const result of settled) {
      if (result.status === 'fulfilled' && result.value.ok) {
        allItems.push(...result.value.value.items)
      }
    }

    // Deduplicate by type:name:source
    const seen = new Set<string>()
    const deduped: Component[] = []
    for (const item of allItems) {
      const key = `${item.type}:${item.name}:${item.source}`
      if (!seen.has(key)) {
        seen.add(key)
        deduped.push(item)
      }
    }

    const filtered = type ? deduped.filter((c) => c.type === type) : deduped
    return ok(paginateArray(filtered, page, limit))
  }

  async add(
    source: string,
    type: ComponentType,
    opts: ComponentAddOptions
  ): Promise<Result<ComponentAddResult>> {
    const providers = this.findProviders('add', type)
    if (providers.length === 0) {
      return err(
        new SdkError(`No provider supports adding ${type} components`, 'E_PROVIDER_UNAVAILABLE')
      )
    }
    return providers[0]?.add(source, opts)
  }

  async list(
    type: ComponentType,
    opts?: { cwd?: string; agent?: string }
  ): Promise<Result<Component[]>> {
    const providers = this.findProviders('list', type)
    const allItems: Component[] = []
    for (const p of providers) {
      const result = await p.list(type, opts)
      if (result.ok) allItems.push(...result.value)
    }
    return ok(allItems)
  }

  async info(
    name: string,
    type: ComponentType,
    opts?: { cwd?: string }
  ): Promise<Result<Component>> {
    const providers = this.findProviders('info', type)
    for (const p of providers) {
      const result = await p.info(name, type, opts)
      if (result.ok) return result
    }
    return err(
      new SdkError(
        `Component "${name}" (${type}) not found in any provider`,
        'E_COMPONENT_NOT_FOUND'
      )
    )
  }

  async remove(
    name: string,
    type: ComponentType,
    opts?: { cwd?: string; agent?: string }
  ): Promise<Result<RemoveResult>> {
    const providers = this.findProviders('remove', type)
    if (providers.length === 0) {
      return err(
        new SdkError(`No provider supports removing ${type} components`, 'E_PROVIDER_UNAVAILABLE')
      )
    }
    return providers[0]?.remove(name, type, opts)
  }

  async publish(type: ComponentType, opts: PublishOptions): Promise<Result<PublishResult>> {
    const providers = this.findProviders('publish', type)
    if (providers.length === 0) {
      return err(new SdkError(`No provider supports publishing ${type}`, 'E_PROVIDER_UNAVAILABLE'))
    }
    return providers[0]!.publish(type, opts)
  }
}

/** @deprecated Use `ProviderManager` instead. */
export { ProviderManager as ComponentManager }
