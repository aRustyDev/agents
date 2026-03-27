/**
 * Plugin and skill manifest I/O.
 *
 * Provides functions to read and validate plugin manifests, plugin source
 * definitions, and skill frontmatter from their canonical locations on disk.
 */

import { existsSync } from 'node:fs'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { err, ok, type Result, type SourceFormat } from '@agents/core/types'
import * as v from 'valibot'
import { SdkError } from '../util/errors'
import { parseMarkdownFrontmatter } from './frontmatter'
import {
  PluginManifest,
  PluginSourceExtended,
  PluginSourcePlanning,
  PluginSourcesManifest,
} from './plugin/schema'
import { SkillFrontmatter } from './skill/schema'

// ---------------------------------------------------------------------------
// Plugin manifest
// ---------------------------------------------------------------------------

/**
 * Read and validate a plugin's `plugin.json` manifest.
 *
 * @param dir - Path to the plugin directory (e.g. `content/plugins/blog-workflow`).
 *              The function looks for `.claude-plugin/plugin.json` inside this dir.
 * @returns Validated PluginManifest or a descriptive error.
 */
export async function readPluginManifest(dir: string): Promise<Result<PluginManifest>> {
  const manifestPath = join(dir, '.claude-plugin', 'plugin.json')

  if (!existsSync(manifestPath)) {
    return err(
      new SdkError(
        `Plugin manifest not found: ${manifestPath}`,
        'E_MANIFEST_NOT_FOUND',
        `Ensure the plugin directory contains .claude-plugin/plugin.json`
      )
    )
  }

  let raw: string
  try {
    raw = await readFile(manifestPath, 'utf-8')
  } catch (e) {
    return err(new SdkError(`Failed to read plugin manifest: ${manifestPath}`, 'E_READ_FAILED'))
  }

  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch (e) {
    return err(
      new SdkError(
        `Invalid JSON in plugin manifest: ${manifestPath}`,
        'E_INVALID_JSON',
        `Check the file for syntax errors`,
        e
      )
    )
  }

  const result = v.safeParse(PluginManifest, parsed)
  if (!result.success) {
    const issues = result.issues
      .map((issue) => {
        const path = issue.path?.map((p) => p.key).join('.') ?? '(root)'
        return `  ${path}: ${issue.message}`
      })
      .join('\n')
    return err(
      new SdkError(
        `Plugin manifest validation failed: ${manifestPath}`,
        'E_VALIDATION_FAILED',
        issues
      )
    )
  }

  return ok(result.output)
}

// ---------------------------------------------------------------------------
// Plugin sources
// ---------------------------------------------------------------------------

/**
 * Read and validate a plugin's `plugin.sources.json`.
 *
 * If the file does not exist, returns an empty sources manifest rather than
 * an error -- this is normal for plugins that have no external sources.
 *
 * @param dir - Path to the plugin directory.
 * @returns Validated PluginSourcesManifest (possibly with empty sources).
 */
export async function readPluginSources(dir: string): Promise<Result<PluginSourcesManifest>> {
  const sourcesPath = join(dir, '.claude-plugin', 'plugin.sources.json')

  if (!existsSync(sourcesPath)) {
    // Missing file is not an error -- return empty manifest
    return ok({ sources: {} })
  }

  let raw: string
  try {
    raw = await readFile(sourcesPath, 'utf-8')
  } catch (e) {
    return err(new SdkError(`Failed to read plugin sources: ${sourcesPath}`, 'E_READ_FAILED'))
  }

  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch (e) {
    return err(
      new SdkError(
        `Invalid JSON in plugin sources: ${sourcesPath}`,
        'E_INVALID_JSON',
        `Check the file for syntax errors`,
        e
      )
    )
  }

  const result = v.safeParse(PluginSourcesManifest, parsed)
  if (!result.success) {
    const issues = result.issues
      .map((issue) => {
        const path = issue.path?.map((p) => p.key).join('.') ?? '(root)'
        return `  ${path}: ${issue.message}`
      })
      .join('\n')
    return err(
      new SdkError(
        `Plugin sources validation failed: ${sourcesPath}`,
        'E_VALIDATION_FAILED',
        issues
      )
    )
  }

  return ok(result.output)
}

// ---------------------------------------------------------------------------
// Skill frontmatter
// ---------------------------------------------------------------------------

/**
 * Read a SKILL.md file and parse/validate its YAML frontmatter.
 *
 * Uses `parseMarkdownFrontmatter` to extract the YAML block, then
 * validates it against the `SkillFrontmatter` schema.
 *
 * @param skillPath - Path to the SKILL.md file.
 * @returns Validated SkillFrontmatter or a descriptive error.
 */
export async function readSkillFrontmatter(skillPath: string): Promise<Result<SkillFrontmatter>> {
  if (!existsSync(skillPath)) {
    return err(
      new SdkError(
        `Skill file not found: ${skillPath}`,
        'E_SKILL_NOT_FOUND',
        `Ensure the SKILL.md file exists at the given path`
      )
    )
  }

  let raw: string
  try {
    raw = await readFile(skillPath, 'utf-8')
  } catch (e) {
    return err(new SdkError(`Failed to read skill file: ${skillPath}`, 'E_READ_FAILED'))
  }

  const { meta } = parseMarkdownFrontmatter(raw)

  if (!meta || Object.keys(meta).length === 0) {
    return err(
      new SdkError(
        `No frontmatter found in skill file: ${skillPath}`,
        'E_NO_FRONTMATTER',
        `SKILL.md files must start with YAML frontmatter (--- delimited)`
      )
    )
  }

  const result = v.safeParse(SkillFrontmatter, meta)
  if (!result.success) {
    const issues = result.issues
      .map((issue) => {
        const path = issue.path?.map((p) => p.key).join('.') ?? '(root)'
        return `  ${path}: ${issue.message}`
      })
      .join('\n')
    return err(
      new SdkError(
        `Skill frontmatter validation failed: ${skillPath}`,
        'E_VALIDATION_FAILED',
        issues
      )
    )
  }

  return ok(result.output)
}

// ---------------------------------------------------------------------------
// Source format detection and normalization
// ---------------------------------------------------------------------------

/**
 * Classify a plugin source entry as one of the three known formats.
 *
 * - `'legacy'`: bare string path (e.g. `"content/commands/foo.md"`)
 * - `'extended'`: object with `source` field (and optional `hash`, `forked`)
 * - `'planning'`: object with `type` field (and optional `base`, `notes`)
 *
 * @param entry - The raw source entry value from plugin.sources.json.
 * @returns The detected format.
 */
export function detectSourceFormat(entry: unknown): SourceFormat {
  if (typeof entry === 'string') {
    return 'legacy'
  }
  if (typeof entry === 'object' && entry !== null) {
    if ('source' in entry) {
      return 'extended'
    }
    if ('type' in entry) {
      return 'planning'
    }
  }
  // Default to legacy for unknown shapes
  return 'legacy'
}

/**
 * Inferred output type of the ExtendedSource schema.
 */
export type ExtendedSource = PluginSourceExtended

/**
 * Convert any source format to the canonical extended format.
 *
 * - Legacy strings become `{ source: "<path>" }` (no hash).
 * - Planning objects become `{ source: "", forked: true }` since they have
 *   no concrete source path yet.
 * - Extended objects pass through after validation.
 *
 * @param entry - The raw source entry value.
 * @returns Normalized ExtendedSource or a validation error.
 */
export function normalizeSource(entry: unknown): Result<ExtendedSource> {
  const format = detectSourceFormat(entry)

  switch (format) {
    case 'legacy': {
      if (typeof entry !== 'string') {
        return err(new SdkError('Expected a string for legacy source format', 'E_INVALID_SOURCE'))
      }
      return ok({ source: entry })
    }

    case 'planning': {
      const result = v.safeParse(PluginSourcePlanning, entry)
      if (!result.success) {
        return err(
          new SdkError(
            'Invalid planning source format',
            'E_INVALID_SOURCE',
            result.issues.map((i) => i.message).join(', ')
          )
        )
      }
      return ok({
        source: '',
        forked: true,
      })
    }

    case 'extended': {
      const result = v.safeParse(PluginSourceExtended, entry)
      if (!result.success) {
        return err(
          new SdkError(
            'Invalid extended source format',
            'E_INVALID_SOURCE',
            result.issues.map((i) => i.message).join(', ')
          )
        )
      }
      return ok(result.output)
    }
  }
}
