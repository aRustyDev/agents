/**
 * Graph Viewer commands — serve, build, dev.
 *
 * Subcommands:
 *   serve - Start the Bun server (production: serves built assets)
 *   build - Build the Vite client
 *   dev   - Start both Vite dev server and Bun API server
 */

import { defineCommand } from 'citty'
import { currentDir } from '../lib/runtime'

const serveCommand = defineCommand({
  meta: { name: 'serve', description: 'Start the graph viewer server' },
  args: {
    port: { type: 'string', default: '3000', description: 'Server port' },
  },
  async run({ args }) {
    process.env.GV_PORT = args.port
    await import('../bin/graph-viewer')
  },
})

const buildCommand = defineCommand({
  meta: { name: 'build', description: 'Build the graph viewer client' },
  async run() {
    const { execSync } = await import('node:child_process')
    const { resolve } = await import('node:path')
    const scriptsDir = resolve(currentDir(import.meta), '..')
    execSync('npx vite build --config vite.graph-viewer.config.ts', {
      cwd: scriptsDir,
      stdio: 'inherit',
    })
  },
})

const devCommand = defineCommand({
  meta: { name: 'dev', description: 'Start graph viewer in dev mode (Vite HMR + Bun API)' },
  args: {
    port: { type: 'string', default: '3000', description: 'API server port' },
  },
  async run({ args }) {
    const { execSync } = await import('node:child_process')
    const { resolve } = await import('node:path')
    const scriptsDir = resolve(currentDir(import.meta), '..')
    process.env.GV_PORT = args.port
    execSync(
      `npx concurrently "bun --watch run bin/graph-viewer.ts" "npx vite --config vite.graph-viewer.config.ts"`,
      {
        cwd: scriptsDir,
        stdio: 'inherit',
      }
    )
  },
})

export default defineCommand({
  meta: { name: 'graph-viewer', description: 'Interactive graph visualization tool' },
  subCommands: {
    serve: serveCommand,
    build: buildCommand,
    dev: devCommand,
  },
})
