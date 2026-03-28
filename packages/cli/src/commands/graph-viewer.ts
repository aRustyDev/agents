/**
 * Graph Viewer commands — serve, build, dev.
 *
 * Delegates to the @agents/graph-viewer package.
 *
 * Subcommands:
 *   serve - Start the Bun server (production: serves built assets)
 *   build - Build the Vite client
 *   dev   - Start both Vite dev server and Bun API server
 */

import { defineCommand } from 'citty'

export default defineCommand({
  meta: { name: 'graph-viewer', description: 'Interactive graph visualization tool' },
  subCommands: {
    serve: defineCommand({
      meta: { name: 'serve', description: 'Start the graph viewer server' },
      args: {
        port: { type: 'string', default: '3000', description: 'Server port' },
      },
      async run({ args }) {
        process.env.GV_PORT = args.port
        await import('@agents/graph-viewer/bin')
      },
    }),
    build: defineCommand({
      meta: { name: 'build', description: 'Build the graph viewer client' },
      async run() {
        const { execSync } = await import('node:child_process')
        execSync('bun run build', { cwd: 'packages/graph-viewer', stdio: 'inherit' })
      },
    }),
    dev: defineCommand({
      meta: { name: 'dev', description: 'Start dev mode' },
      async run() {
        const { execSync } = await import('node:child_process')
        execSync('bun run dev', { cwd: 'packages/graph-viewer', stdio: 'inherit' })
      },
    }),
  },
})
