import { err, ok, type Result } from '@agents/core/types'
import { SdkError } from '../../util/errors'
import type { CatalogStore } from '../interface'
import type {
  CatalogEntry,
  CatalogFilter,
  CatalogQuery,
  DiscoveryResult,
  ErrorRecord,
  StaleResult,
  SyncResult,
} from '../types'
import { appendNdjsonFile, readNdjsonFile, writeNdjsonFile } from './io'

export interface NdjsonStoreOptions {
  catalogPath: string
  errorLogPath?: string
}

/** Composite key for catalog entries. */
function entryKey(source: string, name: string): string {
  return `${source}::${name}`
}

function applyFilter(entries: CatalogEntry[], filter?: CatalogFilter): CatalogEntry[] {
  if (!filter) return entries
  let result = entries
  if (filter.type) result = result.filter((e) => e.type === filter.type)
  if (filter.availability) result = result.filter((e) => e.availability === filter.availability)
  if (filter.source) result = result.filter((e) => e.source === filter.source)
  if (filter.hasAnalysis !== undefined) {
    result = result.filter((e) =>
      filter.hasAnalysis ? e.analysis !== undefined : e.analysis === undefined
    )
  }
  return result
}

function applyQuery(entries: CatalogEntry[], params: CatalogQuery): CatalogEntry[] {
  let result = entries
  if (params.type) result = result.filter((e) => e.type === params.type)
  if (params.availability) result = result.filter((e) => e.availability === params.availability)
  if (params.source) result = result.filter((e) => e.source.includes(params.source!))
  if (params.query) {
    const q = params.query.toLowerCase()
    result = result.filter(
      (e) => e.name.toLowerCase().includes(q) || e.source.toLowerCase().includes(q)
    )
  }
  const offset = params.offset ?? 0
  const limit = params.limit ?? result.length
  return result.slice(offset, offset + limit)
}

export class NdjsonStore implements CatalogStore {
  readonly backend = 'ndjson'
  private readonly catalogPath: string
  private readonly errorLogPath: string

  constructor(opts: NdjsonStoreOptions) {
    this.catalogPath = opts.catalogPath
    this.errorLogPath = opts.errorLogPath ?? `${opts.catalogPath}.errors.ndjson`
  }

  async query(params: CatalogQuery): Promise<Result<CatalogEntry[]>> {
    const read = await readNdjsonFile<CatalogEntry>(this.catalogPath)
    if (!read.ok) return read
    return ok(applyQuery(read.value, params))
  }

  async get(source: string, name: string): Promise<Result<CatalogEntry | undefined>> {
    const read = await readNdjsonFile<CatalogEntry>(this.catalogPath)
    if (!read.ok) return read
    const entry = read.value.find((e) => e.source === source && e.name === name)
    return ok(entry)
  }

  async count(filter?: CatalogFilter): Promise<Result<number>> {
    const read = await readNdjsonFile<CatalogEntry>(this.catalogPath)
    if (!read.ok) return read as Result<never>
    return ok(applyFilter(read.value, filter).length)
  }

  async findStale(upstream: Map<string, string>): Promise<Result<StaleResult[]>> {
    const read = await readNdjsonFile<CatalogEntry>(this.catalogPath)
    if (!read.ok) return read as Result<never>

    const results: StaleResult[] = []
    for (const entry of read.value) {
      const key = entryKey(entry.source, entry.name)
      const upstreamHash = upstream.get(key)
      if (upstreamHash === undefined) {
        results.push({
          source: entry.source,
          name: entry.name,
          status: 'unknown',
          localHash: entry.contentHash,
        })
      } else if (entry.contentHash === upstreamHash) {
        results.push({
          source: entry.source,
          name: entry.name,
          status: 'current',
          localHash: entry.contentHash,
          upstreamHash,
        })
      } else {
        results.push({
          source: entry.source,
          name: entry.name,
          status: 'stale',
          localHash: entry.contentHash,
          upstreamHash,
        })
      }
    }
    return ok(results)
  }

  async upsert(entries: CatalogEntry[]): Promise<Result<number>> {
    const read = await readNdjsonFile<CatalogEntry>(this.catalogPath)
    if (!read.ok) return read as Result<never>

    const existing = new Map<string, CatalogEntry>()
    for (const e of read.value) existing.set(entryKey(e.source, e.name), e)

    let count = 0
    for (const entry of entries) {
      existing.set(entryKey(entry.source, entry.name), entry)
      count++
    }

    const writeResult = await writeNdjsonFile(this.catalogPath, [...existing.values()])
    if (!writeResult.ok) return writeResult as Result<never>
    return ok(count)
  }

  async remove(source: string, name: string): Promise<Result<boolean>> {
    const read = await readNdjsonFile<CatalogEntry>(this.catalogPath)
    if (!read.ok) return read as Result<never>

    const before = read.value.length
    const filtered = read.value.filter((e) => !(e.source === source && e.name === name))
    if (filtered.length === before) return ok(false)

    const writeResult = await writeNdjsonFile(this.catalogPath, filtered)
    if (!writeResult.ok) return writeResult as Result<never>
    return ok(true)
  }

  async merge(results: DiscoveryResult[]): Promise<Result<SyncResult>> {
    const read = await readNdjsonFile<CatalogEntry>(this.catalogPath)
    if (!read.ok) return read as Result<never>

    const existing = new Map<string, CatalogEntry>()
    for (const e of read.value) existing.set(entryKey(e.source, e.name), e)

    const syncResult: SyncResult = { added: 0, updated: 0, removed: 0, moved: 0, errors: 0 }

    for (const dr of results) {
      const key = entryKey(dr.source, dr.name)
      const prev = existing.get(key)
      if (prev) {
        existing.set(key, {
          ...prev,
          type: dr.type,
          mechanical: dr.mechanical,
          availability: 'available',
          discoveredAt: new Date().toISOString(),
        })
        syncResult.updated++
      } else {
        existing.set(key, {
          source: dr.source,
          name: dr.name,
          type: dr.type,
          availability: 'available',
          mechanical: dr.mechanical,
          discoveredAt: new Date().toISOString(),
        })
        syncResult.added++
      }
    }

    const writeResult = await writeNdjsonFile(this.catalogPath, [...existing.values()])
    if (!writeResult.ok) {
      return err(
        new SdkError(
          'Failed to write catalog during merge',
          'E_STORAGE_BACKEND',
          writeResult.error.message
        )
      )
    }
    return ok(syncResult)
  }

  async appendErrors(errors: ErrorRecord[]): Promise<Result<void>> {
    return appendNdjsonFile(this.errorLogPath, errors)
  }

  async close(): Promise<void> {
    // noop for file-based store
  }
}
