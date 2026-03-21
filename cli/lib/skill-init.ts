/**
 * Skill scaffolding module.
 *
 * Creates a new skill from a template by:
 * 1. Validating the skill name (lowercase kebab-case)
 * 2. Ensuring the target directory does not already exist
 * 3. Locating a template (explicit path, project default, or built-in)
 * 4. Rendering the template with `{{name}}` and `{{description}}` placeholders
 * 5. Validating the rendered output with `readSkillFrontmatter`
 *
 * The public `initSkill` function never throws -- all errors are returned
 * as structured `InitResult` objects.
 */

import { existsSync } from 'node:fs'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { join, resolve } from 'node:path'
import { CliError } from './types'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface InitOptions {
  /** Working directory (project root). Defaults to cwd. */
  cwd?: string
  /** Short description for the skill. */
  description?: string
  /** Explicit template file path. */
  template?: string
  /** Base directory for the new skill. Defaults to `context/skills/`. */
  baseDir?: string
}

export interface InitResult {
  /** Whether the operation completed successfully. */
  ok: boolean
  /** Absolute path to the created SKILL.md file. */
  skillPath?: string
  /** Absolute path to the created skill directory. */
  skillDir?: string
  /** Error that caused the operation to fail. */
  error?: CliError
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Valid skill name pattern: lowercase kebab-case, 2+ chars. */
const NAME_RE = /^[a-z][a-z0-9-]*[a-z0-9]$/

/**
 * Built-in template used when no template file is found on disk.
 * Matches the contents of `cli/templates/SKILL.md.tmpl`.
 */
const BUILTIN_TEMPLATE = `---
name: {{name}}
description: {{description}}
version: 0.1.0
tags: []
---

# {{name}}

{{description}}

## Usage

<!-- Describe when and how to use this skill -->

## References

<!-- Links to relevant documentation -->
`

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Scaffold a new skill directory with a rendered SKILL.md file.
 *
 * Never throws -- all errors are captured in the returned `InitResult`.
 */
export async function initSkill(name: string, opts: InitOptions = {}): Promise<InitResult> {
  const cwd = opts.cwd ?? process.cwd()
  const description = opts.description ?? `A new skill called ${name}`
  const baseDir = opts.baseDir ?? join(cwd, 'context', 'skills')

  // Step 1: Validate name
  const nameError = validateSkillName(name)
  if (nameError) {
    return { ok: false, error: nameError }
  }

  // Step 2: Check target directory
  const skillDir = join(baseDir, name)
  if (existsSync(skillDir)) {
    return {
      ok: false,
      error: new CliError(
        `Skill directory already exists: ${skillDir}`,
        'E_DIR_EXISTS',
        `Choose a different name or remove the existing directory`
      ),
    }
  }

  // Step 3: Load template
  const template = await loadTemplate(opts.template, cwd)

  // Step 4: Render template
  const rendered = template.replaceAll('{{name}}', name).replaceAll('{{description}}', description)

  // Step 5: Write the file
  const skillPath = join(skillDir, 'SKILL.md')
  await mkdir(skillDir, { recursive: true })
  await writeFile(skillPath, rendered, 'utf-8')

  // Step 6: Validate the rendered output
  const { readSkillFrontmatter } = await import('./manifest')
  const validateResult = await readSkillFrontmatter(skillPath)
  if (!validateResult.ok) {
    return {
      ok: false,
      skillPath,
      skillDir,
      error: new CliError(
        `Template produced invalid SKILL.md: ${validateResult.error.message}`,
        'E_TEMPLATE_INVALID',
        'Check your template file for valid YAML frontmatter'
      ),
    }
  }

  return { ok: true, skillPath, skillDir }
}

// ---------------------------------------------------------------------------
// Name validation
// ---------------------------------------------------------------------------

/**
 * Validate a skill name. Returns a CliError if invalid, undefined if valid.
 */
export function validateSkillName(name: string): CliError | undefined {
  if (!name) {
    return new CliError(
      'Skill name is required',
      'E_INVALID_NAME',
      'Provide a lowercase kebab-case name (e.g., my-skill)'
    )
  }

  if (name.length < 2) {
    return new CliError(
      `Skill name too short: "${name}" (minimum 2 characters)`,
      'E_INVALID_NAME',
      'Provide a name with at least 2 characters'
    )
  }

  if (!NAME_RE.test(name)) {
    return new CliError(
      `Invalid skill name: "${name}"`,
      'E_INVALID_NAME',
      'Names must be lowercase kebab-case (e.g., my-skill, lang-rust-dev)'
    )
  }

  return undefined
}

// ---------------------------------------------------------------------------
// Template loading
// ---------------------------------------------------------------------------

/**
 * Load a template from (in priority order):
 * 1. Explicit `templatePath` argument
 * 2. Project default at `cli/templates/SKILL.md.tmpl`
 * 3. Built-in hardcoded template
 */
async function loadTemplate(templatePath: string | undefined, cwd: string): Promise<string> {
  // Priority 1: explicit template
  if (templatePath) {
    const resolved = resolve(cwd, templatePath)
    if (existsSync(resolved)) {
      return readFile(resolved, 'utf-8')
    }
    // Fall through to defaults if explicit template doesn't exist
  }

  // Priority 2: project default
  const projectTemplate = join(cwd, 'cli', 'templates', 'SKILL.md.tmpl')
  if (existsSync(projectTemplate)) {
    return readFile(projectTemplate, 'utf-8')
  }

  // Priority 3: built-in
  return BUILTIN_TEMPLATE
}
