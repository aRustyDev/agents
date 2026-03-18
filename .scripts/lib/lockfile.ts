/**
 * Schema-driven lockfile operations.
 *
 * Provides an extensible registry of lockfile schemas.  Each schema knows
 * how to validate its data and check staleness of the entries it contains.
 * Two schemas are pre-registered: `skills` and `plugins`.
 */

import { existsSync } from 'node:fs'
import { readFile, writeFile } from 'node:fs/promises'
import { join, dirname } from 'node:path'
import * as v from 'valibot'
import { ok, err, CliError, type Result } from './types'
import { computeHash, formatHash, parseHash } from './hash'
import {
  LockfileV1,
  PluginSourcesManifest,
  type PluginSourceExtended,
} from './schemas'

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface StalenessEntry {
  name: string
  status: 'fresh' | 'stale' | 'missing' | 'no-hash'
  expectedHash?: string
  actualHash?: string
}

export interface StalenessReport {
  entries: StalenessEntry[]
  allFresh: boolean
}

export interface LockfileSchema<T> {
  name: string
  filename: string
  schema: v.BaseSchema<unknown, T, v.BaseIssue<unknown>>
  checkStaleness(data: T, basePath: string): Promise<StalenessReport>
}

// ---------------------------------------------------------------------------
// Schema registry
// ---------------------------------------------------------------------------

const registry = new Map<string, LockfileSchema<unknown>>()

/**
 * Register a lockfile schema with the global registry.
 *
 * Registered schemas can later be looked up by name when calling
 * `readLockfile`, `writeLockfile`, or `checkStaleness`.
 */
export function registerSchema<T>(schema: LockfileSchema<T>): void {
  registry.set(schema.name, schema as LockfileSchema<unknown>)
}

/**
 * Look up a registered schema by name.
 *
 * Returns `undefined` if no schema with that name has been registered.
 */
export function getSchema(name: string): LockfileSchema<unknown> | undefined {
  return registry.get(name)
}

// ---------------------------------------------------------------------------
// Core operations
// ---------------------------------------------------------------------------

/**
 * Read a JSON file and validate it against a registered lockfile schema.
 *
 * @param schemaName - Name of the registered schema to validate against.
 * @param path - Absolute path to the JSON file.
 * @returns Validated data wrapped in a Result.
 */
export async function readLockfile<T>(
  schemaName: string,
  path: string,
): Promise<Result<T>> {
  const schema = registry.get(schemaName)
  if (!schema) {
    return err(
      new CliError(
        `No lockfile schema registered with name "${schemaName}"`,
        'E_SCHEMA_NOT_FOUND',
        `Available schemas: ${[...registry.keys()].join(', ') || '(none)'}`,
      ),
    )
  }

  let raw: string
  try {
    raw = await readFile(path, 'utf-8')
  } catch (e) {
    return err(
      new CliError(
        `Failed to read lockfile: ${path}`,
        'E_READ_FAILED',
        `Ensure the file exists and is readable`,
        e,
      ),
    )
  }

  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch (e) {
    return err(
      new CliError(
        `Invalid JSON in lockfile: ${path}`,
        'E_INVALID_JSON',
        `Check the file for syntax errors`,
        e,
      ),
    )
  }

  const result = v.safeParse(schema.schema, parsed)
  if (!result.success) {
    const issues = result.issues
      .map((issue) => {
        const path = issue.path?.map((p) => p.key).join('.') ?? '(root)'
        return `  ${path}: ${issue.message}`
      })
      .join('\n')
    return err(
      new CliError(
        `Lockfile validation failed: ${path}`,
        'E_VALIDATION_FAILED',
        `Schema: ${schemaName}\n${issues}`,
      ),
    )
  }

  return ok(result.output as T)
}

/**
 * Validate data against a registered schema and write it to disk.
 *
 * Writes JSON with 2-space indentation and a trailing newline to match
 * the project's formatting conventions.
 *
 * @param schemaName - Name of the registered schema to validate against.
 * @param path - Absolute path to write the JSON file.
 * @param data - Data to validate and write.
 */
export async function writeLockfile(
  schemaName: string,
  path: string,
  data: unknown,
): Promise<Result<void>> {
  const schema = registry.get(schemaName)
  if (!schema) {
    return err(
      new CliError(
        `No lockfile schema registered with name "${schemaName}"`,
        'E_SCHEMA_NOT_FOUND',
        `Available schemas: ${[...registry.keys()].join(', ') || '(none)'}`,
      ),
    )
  }

  const result = v.safeParse(schema.schema, data)
  if (!result.success) {
    const issues = result.issues
      .map((issue) => {
        const path = issue.path?.map((p) => p.key).join('.') ?? '(root)'
        return `  ${path}: ${issue.message}`
      })
      .join('\n')
    return err(
      new CliError(
        `Data does not match schema "${schemaName}"`,
        'E_VALIDATION_FAILED',
        issues,
      ),
    )
  }

  try {
    const json = JSON.stringify(result.output, null, 2) + '\n'
    await writeFile(path, json, 'utf-8')
    return ok(undefined)
  } catch (e) {
    return err(
      new CliError(
        `Failed to write lockfile: ${path}`,
        'E_WRITE_FAILED',
        `Ensure the directory exists and is writable`,
        e,
      ),
    )
  }
}

/**
 * Read a lockfile and check the staleness of all entries.
 *
 * Delegates to the schema's `checkStaleness` implementation which knows
 * how to hash the relevant source paths and compare to stored digests.
 *
 * @param schemaName - Name of the registered schema.
 * @param path - Absolute path to the lockfile.
 * @param basePath - Base directory for resolving relative source paths.
 */
export async function checkStaleness(
  schemaName: string,
  path: string,
  basePath: string,
): Promise<Result<StalenessReport>> {
  const data = await readLockfile<unknown>(schemaName, path)
  if (!data.ok) return data

  const schema = registry.get(schemaName)!
  try {
    const report = await schema.checkStaleness(data.value, basePath)
    return ok(report)
  } catch (e) {
    return err(
      new CliError(
        `Staleness check failed for schema "${schemaName}"`,
        'E_STALENESS_CHECK',
        `Error during hash computation`,
        e,
      ),
    )
  }
}

// ---------------------------------------------------------------------------
// Pre-registered schemas
// ---------------------------------------------------------------------------

/**
 * Skills lockfile schema.
 *
 * Checks staleness by hashing each skill directory (resolved relative to
 * basePath) and comparing the computed digest to the stored `computedHash`.
 */
const skillsSchema: LockfileSchema<LockfileV1> = {
  name: 'skills',
  filename: 'skills-lock.json',
  schema: LockfileV1 as v.BaseSchema<unknown, LockfileV1, v.BaseIssue<unknown>>,

  async checkStaleness(data, basePath): Promise<StalenessReport> {
    const entries: StalenessEntry[] = []

    for (const [name, entry] of Object.entries(data.skills)) {
      // Skills are typically stored under context/skills/<name>
      const skillPath = join(basePath, 'context', 'skills', name)

      if (!existsSync(skillPath)) {
        entries.push({
          name,
          status: 'missing',
          expectedHash: entry.computedHash,
        })
        continue
      }

      const actualHash = await computeHash(skillPath)
      if (actualHash === entry.computedHash) {
        entries.push({
          name,
          status: 'fresh',
          expectedHash: entry.computedHash,
          actualHash,
        })
      } else {
        entries.push({
          name,
          status: 'stale',
          expectedHash: entry.computedHash,
          actualHash,
        })
      }
    }

    return {
      entries,
      allFresh: entries.every((e) => e.status === 'fresh'),
    }
  },
}

/**
 * Plugin sources manifest schema.
 *
 * Checks staleness by hashing each source path (resolved relative to
 * basePath) and comparing the computed digest to the stored hash.
 * Entries without a hash are reported as `no-hash`.
 */
const pluginsSchema: LockfileSchema<PluginSourcesManifest> = {
  name: 'plugins',
  filename: 'plugin.sources.json',
  schema: PluginSourcesManifest as v.BaseSchema<
    unknown,
    PluginSourcesManifest,
    v.BaseIssue<unknown>
  >,

  async checkStaleness(data, basePath): Promise<StalenessReport> {
    const entries: StalenessEntry[] = []

    for (const [name, sourceDef] of Object.entries(data.sources)) {
      // Legacy string format has no hash information
      if (typeof sourceDef === 'string') {
        const sourcePath = join(basePath, sourceDef)
        if (!existsSync(sourcePath)) {
          entries.push({ name, status: 'missing' })
        } else {
          entries.push({ name, status: 'no-hash' })
        }
        continue
      }

      // Planning format (has type but no source) -- skip
      const ext = sourceDef as PluginSourceExtended
      if (!ext.source && (sourceDef as Record<string, unknown>).type) {
        entries.push({ name, status: 'no-hash' })
        continue
      }

      // Extended format
      if (!ext.hash) {
        entries.push({ name, status: 'no-hash' })
        continue
      }

      const sourcePath = join(basePath, ext.source)
      if (!existsSync(sourcePath)) {
        entries.push({
          name,
          status: 'missing',
          expectedHash: ext.hash,
        })
        continue
      }

      const actualHex = await computeHash(sourcePath)
      const expectedHex = parseHash(ext.hash)
      const actualPrefixed = formatHash(actualHex)

      if (actualHex === expectedHex) {
        entries.push({
          name,
          status: 'fresh',
          expectedHash: ext.hash,
          actualHash: actualPrefixed,
        })
      } else {
        entries.push({
          name,
          status: 'stale',
          expectedHash: ext.hash,
          actualHash: actualPrefixed,
        })
      }
    }

    return {
      entries,
      allFresh: entries.every((e) => e.status === 'fresh'),
    }
  },
}

// Register built-in schemas
registerSchema(skillsSchema)
registerSchema(pluginsSchema)
