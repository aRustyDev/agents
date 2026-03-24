import { afterEach, beforeEach, describe, expect, test } from 'bun:test'
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { computeAllMechanicalFields } from '../lib/catalog-discover'

// ---------------------------------------------------------------------------
// computeAllMechanicalFields (local directory, no clone needed)
// ---------------------------------------------------------------------------

describe('computeAllMechanicalFields', () => {
  let tmpDir: string
  let skillDir: string

  beforeEach(() => {
    tmpDir = mkdtempSync(join(tmpdir(), 'discover-'))
    skillDir = join(tmpDir, 'my-skill')
    mkdirSync(skillDir, { recursive: true })
  })
  afterEach(() => {
    rmSync(tmpDir, { recursive: true, force: true })
  })

  test('computes all fields for a simple skill', async () => {
    writeFileSync(
      join(skillDir, 'SKILL.md'),
      '---\nname: my-skill\ndescription: A test skill for unit testing\n---\n# My Skill\n\n## Setup\n\nInstall dependencies.\n\n## Usage\n\nRun the command.\n\n```typescript\nconst x = 1\n```\n'
    )

    const result = await computeAllMechanicalFields(
      join(skillDir, 'SKILL.md'),
      skillDir,
      tmpDir,
      'org/repo',
      'my-skill'
    )

    expect(result.source).toBe('org/repo')
    expect(result.skill).toBe('my-skill')

    const m = result.mechanical
    expect(m.wordCount).toBeGreaterThan(5)
    expect(m.sectionCount).toBe(3) // H1 + 2x H2
    expect(m.fileCount).toBe(1)
    expect(m.headingTree).toHaveLength(3)
    expect(m.headingTree[0]).toEqual({ depth: 1, title: 'My Skill' })
    expect(m.contentHash).toMatch(/^sha256:[a-f0-9]{64}$/)
    expect(m.keywords).toContain('typescript')
    expect(m.keywords).toContain('skill')
    expect(m.lineCount).toBeGreaterThan(10)
    expect(m.sectionMap).toHaveLength(3)
    expect(m.sectionMap?.[0]?.heading).toBe('My Skill')
    expect(m.sectionMap?.[0]?.line).toBe(5)
    expect(m.fileTree).toEqual(['SKILL.md'])
    expect(m.skillSizeBytes).toBeGreaterThan(0)
    expect(m.isSimple).toBe(true)
    expect(m.discoveredPath).toBe('my-skill')
    expect(m.lastSeenAt).toBeTruthy()
  })

  test('complex skill with subdirectories', async () => {
    writeFileSync(
      join(skillDir, 'SKILL.md'),
      '---\nname: complex\ndescription: Has resources\n---\n# Complex\n'
    )
    mkdirSync(join(skillDir, 'resources'))
    writeFileSync(join(skillDir, 'resources', 'guide.md'), '# Guide\n')
    writeFileSync(join(skillDir, 'examples.ts'), 'export const x = 1\n')

    const result = await computeAllMechanicalFields(
      join(skillDir, 'SKILL.md'),
      skillDir,
      tmpDir,
      'org/repo',
      'complex'
    )

    expect(result.mechanical.isSimple).toBe(false)
    expect(result.mechanical.fileCount).toBe(3)
    expect(result.mechanical.fileTree).toContain('SKILL.md')
    expect(result.mechanical.fileTree).toContain(join('resources', 'guide.md'))
    expect(result.mechanical.fileTree).toContain('examples.ts')
  })

  test('extracts keywords from headings + description + code fences', async () => {
    writeFileSync(
      join(skillDir, 'SKILL.md'),
      '---\nname: test\ndescription: Build React components with TypeScript\n---\n# React Development\n\n## Component Patterns\n\n```python\nprint("hello")\n```\n'
    )

    const result = await computeAllMechanicalFields(
      join(skillDir, 'SKILL.md'),
      skillDir,
      tmpDir,
      'org/repo',
      'test'
    )

    const kw = result.mechanical.keywords
    expect(kw).toContain('react')
    expect(kw).toContain('development')
    expect(kw).toContain('component')
    expect(kw).toContain('patterns')
    expect(kw).toContain('typescript')
    expect(kw).toContain('python')
  })

  test('handles empty SKILL.md', async () => {
    writeFileSync(join(skillDir, 'SKILL.md'), '')

    const result = await computeAllMechanicalFields(
      join(skillDir, 'SKILL.md'),
      skillDir,
      tmpDir,
      'org/repo',
      'empty'
    )

    expect(result.mechanical.wordCount).toBe(0)
    expect(result.mechanical.sectionCount).toBe(0)
    expect(result.mechanical.keywords).toEqual([])
    expect(result.mechanical.headingTree).toEqual([])
  })
})
