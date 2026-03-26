/**
 * Verb-first command: agents serve
 *
 * Starts the agents server. Two modes:
 *   --web (default): Start the graph viewer web UI (delegates to existing graph-viewer)
 *   --api: Start a minimal API-only server with health and component endpoints
 *
 * Options:
 *   --port <N>: Set port (default: 3000)
 */
import { existsSync, readdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { createOutput } from '@agents/core/output'
import { currentDir } from '@agents/core/runtime'
import { EXIT } from '@agents/core/types'
import { defineCommand } from 'citty'
import { globalArgs } from './shared-args'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Lazily computed project root. */
function getProjectRoot(): string {
  return resolve(currentDir(import.meta), '../../../..')
}

/** Count subdirectories in a path. */
function countSubdirs(dir: string): number {
  try {
    if (!existsSync(dir)) return 0
    return readdirSync(dir, { withFileTypes: true }).filter((d) => d.isDirectory()).length
  } catch {
    return 0
  }
}

/** Count files in a path. */
function countFiles(dir: string): number {
  try {
    if (!existsSync(dir)) return 0
    return readdirSync(dir, { withFileTypes: true }).filter((d) => d.isFile()).length
  } catch {
    return 0
  }
}

/** Gather component counts for the API. */
function getComponents(projectRoot: string) {
  const contentDir = join(projectRoot, 'content')
  const types = ['skills', 'plugins', 'rules', 'agents', 'commands', 'hooks', 'output-styles']
  const result: Record<string, { type: string; count: number; items: string[] }> = {}

  for (const type of types) {
    const dir = join(contentDir, type)
    if (!existsSync(dir)) {
      result[type] = { type, count: 0, items: [] }
      continue
    }
    const entries = readdirSync(dir, { withFileTypes: true })
    // For skills/plugins/agents, count dirs; for rules, count files
    const isDir = ['skills', 'plugins', 'agents', 'commands', 'hooks', 'output-styles'].includes(
      type
    )
    const items = isDir
      ? entries.filter((e) => e.isDirectory()).map((e) => e.name)
      : entries.filter((e) => e.isFile()).map((e) => e.name)
    result[type] = { type, count: items.length, items }
  }

  return result
}

// ---------------------------------------------------------------------------
// API-only server
// ---------------------------------------------------------------------------

async function startApiServer(port: number): Promise<void> {
  const projectRoot = getProjectRoot()

  const server = Bun.serve({
    port,
    fetch(req: Request) {
      const url = new URL(req.url)
      const { pathname } = url

      // GET /api/health
      if (pathname === '/api/health' && req.method === 'GET') {
        return Response.json({ status: 'ok' })
      }

      // GET /api/components
      if (pathname === '/api/components' && req.method === 'GET') {
        const components = getComponents(projectRoot)
        return Response.json(components)
      }

      // GET /api/components/:type
      const typeMatch = pathname.match(/^\/api\/components\/([a-z-]+)$/)
      if (typeMatch && req.method === 'GET') {
        const type = typeMatch[1]!
        const components = getComponents(projectRoot)
        if (components[type]) {
          return Response.json(components[type])
        }
        return Response.json({ error: `Unknown component type: ${type}` }, { status: 404 })
      }

      return Response.json({ error: 'Not found' }, { status: 404 })
    },
  })

  console.log(`Agents API server running at http://localhost:${server.port}`)
  console.log(`  Health:     http://localhost:${server.port}/api/health`)
  console.log(`  Components: http://localhost:${server.port}/api/components`)
}

// ---------------------------------------------------------------------------
// Command definition
// ---------------------------------------------------------------------------

export default defineCommand({
  meta: { name: 'serve', description: 'Start the agents server' },
  args: {
    ...globalArgs,
    web: {
      type: 'boolean',
      description: 'Start graph viewer web UI (default mode)',
      default: false,
    },
    api: {
      type: 'boolean',
      description: 'Start API-only mode (no web UI)',
      default: false,
    },
    port: {
      type: 'string',
      alias: 'p',
      description: 'Server port',
      default: '3000',
    },
  },
  async run({ args }) {
    const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
    const port = Number(args.port) || 3000

    // Determine mode: --api takes precedence, otherwise default to web
    const apiMode = args.api as boolean

    if (apiMode) {
      await startApiServer(port)
      return
    }

    // Default: delegate to graph-viewer serve (web mode)
    process.env.GV_PORT = String(port)
    out.info(`Starting graph viewer on port ${port}...`)
    await import('../bin/graph-viewer')
  },
})
