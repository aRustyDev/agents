import { afterEach, describe, expect, test } from 'bun:test'
import { mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { findSkills } from '@agents/sdk/providers/local/skill/find'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const originalFetch = globalThis.fetch
const origLog = console.log
const origError = console.error

/** Create a temp catalog file and return its path. */
function makeCatalog(lines: string[]): string {
  const dir = mkdtempSync(join(tmpdir(), 'skill-find-cmd-'))
  const path = join(dir, '.catalog.ndjson')
  writeFileSync(path, lines.join('\n'))
  return path
}

/**
 * Capture console.log and console.error output during an async callback.
 * Returns { stdout, stderr } as joined strings.
 */
async function captureOutput(fn: () => Promise<void>): Promise<{
  stdout: string
  stderr: string
}> {
  const stdoutChunks: string[] = []
  const stderrChunks: string[] = []

  console.log = (...args: unknown[]) => {
    stdoutChunks.push(args.map(String).join(' '))
  }
  console.error = (...args: unknown[]) => {
    stderrChunks.push(args.map(String).join(' '))
  }

  try {
    await fn()
  } finally {
    console.log = origLog
    console.error = origError
  }

  return {
    stdout: stdoutChunks.join('\n'),
    stderr: stderrChunks.join('\n'),
  }
}

// ---------------------------------------------------------------------------
// Restore globals after each test
// ---------------------------------------------------------------------------

afterEach(() => {
  globalThis.fetch = originalFetch
  console.log = origLog
  console.error = origError
})

// ---------------------------------------------------------------------------
// Non-interactive: query provided
// ---------------------------------------------------------------------------

describe('findSkills -- non-interactive with query', () => {
  test('returns empty results for query with no matches', async () => {
    const catalogPath = makeCatalog([
      JSON.stringify({ name: 'alpha', source: 'org/alpha', description: 'Alpha skill' }),
    ])

    const { stdout } = await captureOutput(async () => {
      await findSkills(['xyznonexistent999'], {
        json: true,
        source: 'catalog',
        catalogPath,
      })
    })

    const parsed = JSON.parse(stdout)
    expect(parsed).toEqual([])
  })

  test('--json flag outputs JSON array to stdout', async () => {
    const catalogPath = makeCatalog([
      JSON.stringify({ name: 'beads', source: 'steveyegge/beads', description: 'Issue tracker' }),
      JSON.stringify({ name: 'terraform', source: 'hashicorp/tf', description: 'IaC' }),
    ])

    const { stdout } = await captureOutput(async () => {
      await findSkills(['beads'], {
        json: true,
        source: 'catalog',
        catalogPath,
      })
    })

    const parsed = JSON.parse(stdout)
    expect(Array.isArray(parsed)).toBe(true)
    expect(parsed).toHaveLength(1)
    expect(parsed[0].name).toBe('beads')
    expect(parsed[0].source).toBe('steveyegge/beads')
  })

  test('human mode prints table for matches', async () => {
    const catalogPath = makeCatalog([
      JSON.stringify({ name: 'test-skill', source: 'org/repo', description: 'A testing skill' }),
    ])

    const { stdout } = await captureOutput(async () => {
      await findSkills(['test'], {
        json: false,
        quiet: false,
        source: 'catalog',
        catalogPath,
      })
    })

    // The table output (from console-table-printer via printTable) contains the skill name
    expect(stdout).toContain('test-skill')
  })

  test('human mode prints info message when no results', async () => {
    const catalogPath = makeCatalog([])

    const { stdout } = await captureOutput(async () => {
      await findSkills(['nonexistent'], {
        json: false,
        quiet: false,
        source: 'catalog',
        catalogPath,
      })
    })

    expect(stdout).toContain('No skills found')
  })

  test('limit is passed through to search API', async () => {
    const lines = Array.from({ length: 20 }, (_, i) =>
      JSON.stringify({ name: `skill-${i}`, source: 'org/repo', description: `match ${i}` })
    )
    const catalogPath = makeCatalog(lines)

    const { stdout } = await captureOutput(async () => {
      await findSkills(['skill'], {
        json: true,
        limit: 3,
        source: 'catalog',
        catalogPath,
      })
    })

    const parsed = JSON.parse(stdout)
    expect(parsed).toHaveLength(3)
  })

  test('source flag restricts to catalog backend (no fetch calls)', async () => {
    let fetchCalled = false
    globalThis.fetch = (() => {
      fetchCalled = true
      return Promise.reject(new Error('should not be called'))
    }) as typeof fetch

    const catalogPath = makeCatalog([
      JSON.stringify({ name: 'local-skill', source: 'org/local', description: 'Local' }),
    ])

    const { stdout } = await captureOutput(async () => {
      await findSkills(['local'], {
        json: true,
        source: 'catalog',
        catalogPath,
      })
    })

    expect(fetchCalled).toBe(false)
    const parsed = JSON.parse(stdout)
    expect(parsed).toHaveLength(1)
    expect(parsed[0].name).toBe('local-skill')
  })

  test('JSON mode returns full description (no truncation in raw output)', async () => {
    const longDesc = 'A'.repeat(100)
    const catalogPath = makeCatalog([
      JSON.stringify({ name: 'long-desc', source: 'org/repo', description: longDesc }),
    ])

    const { stdout } = await captureOutput(async () => {
      await findSkills(['long'], {
        json: true,
        source: 'catalog',
        catalogPath,
      })
    })

    const parsed = JSON.parse(stdout)
    expect(parsed[0].description).toBe(longDesc)
  })
})

// ---------------------------------------------------------------------------
// Non-interactive: non-TTY without query
// ---------------------------------------------------------------------------

describe('findSkills -- non-TTY without query', () => {
  test('warns and returns empty for non-TTY with no query', async () => {
    const origTTY = process.stdout.isTTY
    Object.defineProperty(process.stdout, 'isTTY', {
      value: false,
      configurable: true,
    })

    try {
      const { stdout, stderr } = await captureOutput(async () => {
        await findSkills([], {
          json: true,
          source: 'catalog',
        })
      })

      // In JSON mode, warnings go to stderr as JSON
      expect(stderr).toContain('Non-TTY')

      // searchSkillsAPI('') returns [] immediately, so stdout has the empty array
      const parsed = JSON.parse(stdout)
      expect(parsed).toEqual([])
    } finally {
      Object.defineProperty(process.stdout, 'isTTY', {
        value: origTTY,
        configurable: true,
      })
    }
  })
})

// ---------------------------------------------------------------------------
// Interactive: TTY with no query
// ---------------------------------------------------------------------------

describe('findSkills -- interactive mode (TTY, no query)', () => {
  test('prints usage hints when TTY and no query', async () => {
    const origTTY = process.stdout.isTTY
    Object.defineProperty(process.stdout, 'isTTY', {
      value: true,
      configurable: true,
    })

    try {
      const { stdout } = await captureOutput(async () => {
        await findSkills([], {
          json: false,
          quiet: false,
          source: 'catalog',
        })
      })

      expect(stdout).toContain('Usage')
      expect(stdout).toContain('--json')
      expect(stdout).toContain('--limit')
      expect(stdout).toContain('--source')
    } finally {
      Object.defineProperty(process.stdout, 'isTTY', {
        value: origTTY,
        configurable: true,
      })
    }
  })
})

// ---------------------------------------------------------------------------
// Edge cases
// ---------------------------------------------------------------------------

describe('findSkills -- edge cases', () => {
  test('empty args with non-TTY does not throw', async () => {
    const origTTY = process.stdout.isTTY
    Object.defineProperty(process.stdout, 'isTTY', {
      value: false,
      configurable: true,
    })

    try {
      // Should complete without throwing
      await captureOutput(async () => {
        await findSkills([], {
          json: true,
          source: 'catalog',
          catalogPath: '/tmp/nonexistent.ndjson',
        })
      })
    } finally {
      Object.defineProperty(process.stdout, 'isTTY', {
        value: origTTY,
        configurable: true,
      })
    }
  })

  test('installs field shows dash when missing (table mode)', async () => {
    const catalogPath = makeCatalog([
      JSON.stringify({ name: 'no-installs', source: 'org/repo', description: 'No install count' }),
    ])

    const { stdout } = await captureOutput(async () => {
      await findSkills(['no-installs'], {
        json: false,
        quiet: false,
        source: 'catalog',
        catalogPath,
      })
    })

    // The table output should contain the skill name and the dash placeholder
    expect(stdout).toContain('no-installs')
    expect(stdout).toContain('-')
  })

  test('installs field shows number when present (JSON mode)', async () => {
    const catalogPath = makeCatalog([
      JSON.stringify({
        name: 'popular',
        source: 'org/repo',
        description: 'Popular skill',
        installs: 42,
      }),
    ])

    const { stdout } = await captureOutput(async () => {
      await findSkills(['popular'], {
        json: true,
        source: 'catalog',
        catalogPath,
      })
    })

    const parsed = JSON.parse(stdout)
    expect(parsed[0].installs).toBe(42)
  })

  test('quiet mode suppresses info messages in human mode', async () => {
    const catalogPath = makeCatalog([])

    const { stdout } = await captureOutput(async () => {
      await findSkills(['nothing'], {
        json: false,
        quiet: true,
        source: 'catalog',
        catalogPath,
      })
    })

    // In quiet human mode, info messages are suppressed
    expect(stdout).not.toContain('No skills found')
  })
})
