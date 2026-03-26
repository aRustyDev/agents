import { afterAll, beforeAll, describe, expect, it } from 'bun:test'
import { mkdir, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

// Import the barrel to trigger auto-registration of all modules
import '../../src/context/index'
import { parseComponent } from '../../src/context/parser'
import { getRegisteredModules } from '../../src/context/registry'

const TMP_DIR = join(tmpdir(), `sdk-parser-test-${Date.now()}`)

beforeAll(async () => {
  await mkdir(TMP_DIR, { recursive: true })
})

afterAll(async () => {
  await rm(TMP_DIR, { recursive: true, force: true })
})

describe('parseComponent', () => {
  it('dispatches to skill parser after barrel import', async () => {
    const path = join(TMP_DIR, 'dispatcher-SKILL.md')
    await writeFile(
      path,
      `---
name: dispatcher-test
description: Testing the generic dispatcher
---
# Dispatcher Test

Body content here.
`
    )

    const result = await parseComponent('skill', path)
    expect(result.ok).toBe(true)
    if (!result.ok) return

    expect(result.value.type).toBe('skill')
    expect(result.value.name).toBe('dispatcher-test')
  })

  it('dispatches to rule parser', async () => {
    const path = join(TMP_DIR, 'test-rule.md')
    await writeFile(
      path,
      `---
name: test-rule
description: A test rule
---
# Test Rule

Rule content.
`
    )

    const result = await parseComponent('rule', path)
    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.type).toBe('rule')
    expect(result.value.name).toBe('test-rule')
  })

  it('dispatches to plugin parser', async () => {
    const path = join(TMP_DIR, 'plugin.json')
    await writeFile(
      path,
      JSON.stringify({
        name: 'test-plugin',
        version: '1.0.0',
        description: 'A test plugin',
      })
    )

    const result = await parseComponent('plugin', path)
    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.value.type).toBe('plugin')
    expect(result.value.name).toBe('test-plugin')
  })

  it('returns error for file not found', async () => {
    const result = await parseComponent('skill', join(TMP_DIR, 'does-not-exist.md'))
    expect(result.ok).toBe(false)
  })
})

describe('auto-registration', () => {
  it('registers all 10 built-in modules after barrel import', () => {
    const modules = getRegisteredModules()
    // 10 modules: skill, rule, hook, command, output-style, agent,
    // mcp-server, mcp-client, mcp-tool, plugin
    expect(modules.size).toBeGreaterThanOrEqual(10)
    expect(modules.has('skill')).toBe(true)
    expect(modules.has('rule')).toBe(true)
    expect(modules.has('hook')).toBe(true)
    expect(modules.has('command')).toBe(true)
    expect(modules.has('output-style')).toBe(true)
    expect(modules.has('agent')).toBe(true)
    expect(modules.has('mcp-server')).toBe(true)
    expect(modules.has('mcp-client')).toBe(true)
    expect(modules.has('mcp-tool')).toBe(true)
    expect(modules.has('plugin')).toBe(true)
  })
})
