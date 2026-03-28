import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { existsSync } from 'node:fs'
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises'
import { homedir } from 'node:os'
import { join } from 'node:path'
import { unzip, zipDirectory } from '@agents/core/archive'
import {
  getClientSkillsDir,
  getInstallableClients,
  installSkillToClient,
} from '@agents/sdk/providers/clients/install'

// ---------------------------------------------------------------------------
// Temp directory setup
// ---------------------------------------------------------------------------

let tmp: string

beforeEach(async () => {
  tmp = await mkdtemp(join(require('node:os').tmpdir(), 'install-test-'))
})

afterEach(async () => {
  await rm(tmp, { recursive: true, force: true })
})

// ---------------------------------------------------------------------------
// getClientSkillsDir
// ---------------------------------------------------------------------------

describe('getClientSkillsDir', () => {
  test('returns path for claude-code', () => {
    const dir = getClientSkillsDir('claude-code')
    expect(dir).toBe(join(homedir(), '.claude', 'skills'))
  })

  test('returns path for claude-desktop', () => {
    const dir = getClientSkillsDir('claude-desktop')
    expect(dir).toBe(join(homedir(), '.claude', 'skills'))
  })

  test('returns undefined for unknown client', () => {
    const dir = getClientSkillsDir('unknown-client')
    expect(dir).toBeUndefined()
  })
})

// ---------------------------------------------------------------------------
// getInstallableClients
// ---------------------------------------------------------------------------

describe('getInstallableClients', () => {
  test('lists known clients', () => {
    const clients = getInstallableClients()
    expect(clients).toContain('claude-code')
    expect(clients).toContain('claude-desktop')
    expect(clients.length).toBeGreaterThanOrEqual(2)
  })
})

// ---------------------------------------------------------------------------
// installSkillToClient — error paths
// ---------------------------------------------------------------------------

describe('installSkillToClient', () => {
  test('fails for unknown client', async () => {
    const result = await installSkillToClient(join(tmp, 'skill.zip'), 'my-skill', 'unknown-client')

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_PROVIDER_UNAVAILABLE')
    expect(result.error.message).toContain('Unknown client')
  })

  test('fails for missing zip', async () => {
    const result = await installSkillToClient(
      join(tmp, 'nonexistent.zip'),
      'my-skill',
      'claude-code'
    )

    expect(result.ok).toBe(false)
    if (result.ok) return
    expect(result.error.code).toBe('E_COMPONENT_NOT_FOUND')
    expect(result.error.message).toContain('Zip not found')
  })
})

// ---------------------------------------------------------------------------
// installSkillToClient — success path (using unzip directly with tmpdir)
// ---------------------------------------------------------------------------

describe('installSkillToClient integration', () => {
  test('extracts zip to correct directory structure', async () => {
    // Create a skill directory and package it
    const skillDir = join(tmp, 'my-skill')
    await mkdir(skillDir, { recursive: true })
    await writeFile(
      join(skillDir, 'SKILL.md'),
      '---\nname: my-skill\ndescription: A test skill\n---\n# My Skill'
    )
    await writeFile(join(skillDir, 'helper.ts'), 'export const x = 1')

    // Create zip
    const zipPath = join(tmp, 'my-skill.zip')
    const zipResult = await zipDirectory(skillDir, zipPath)
    expect(zipResult.ok).toBe(true)

    // Install using unzip directly to a tmpdir (simulating what installSkillToClient does)
    const installDir = join(tmp, 'installed', 'my-skill')
    const extracted = await unzip(zipPath, installDir)

    expect(extracted.ok).toBe(true)
    if (!extracted.ok) return
    expect(extracted.value).toContain('SKILL.md')
    expect(extracted.value).toContain('helper.ts')

    // Verify files are actually there
    expect(existsSync(join(installDir, 'SKILL.md'))).toBe(true)
    expect(existsSync(join(installDir, 'helper.ts'))).toBe(true)

    // Verify content is preserved
    const content = await readFile(join(installDir, 'SKILL.md'), 'utf-8')
    expect(content).toContain('# My Skill')
  })
})
