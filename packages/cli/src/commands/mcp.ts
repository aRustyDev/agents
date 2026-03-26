/**
 * MCP server management commands.
 *
 * Subcommands:
 *   search  - Search for MCP servers on Smithery
 *   add     - Add an MCP server to a client config
 *   list    - List MCP servers in a client config
 *   remove  - Remove an MCP server from a client config
 *   info    - Show details for an MCP server from Smithery
 *   publish - Publish an MCP server to Smithery
 */

import { createOutput } from '@agents/core/output'
import { EXIT } from '@agents/core/types'
import { defineCommand } from 'citty'
import { createComponentManager } from '../lib/component/factory'
import { globalArgs } from './shared-args'

export default defineCommand({
  meta: { name: 'mcp', description: 'MCP server management' },
  subCommands: {
    search: defineCommand({
      meta: { name: 'search', description: 'Search for MCP servers on Smithery' },
      args: {
        ...globalArgs,
        query: { type: 'positional', description: 'Search query', required: false },
        limit: { type: 'string', description: 'Max results (default: 10)', default: '10' },
        page: { type: 'string', description: 'Page number (default: 1)', default: '1' },
        verified: { type: 'boolean', description: 'Only verified servers', default: false },
        namespace: { type: 'string', description: 'Filter by namespace' },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const manager = createComponentManager()
        const result = await manager.search({
          query: (args.query as string) ?? '',
          type: 'mcp-server',
          limit: Number.parseInt(args.limit as string, 10),
          page: Number.parseInt(args.page as string, 10),
          verified: args.verified as boolean,
          namespace: args.namespace as string | undefined,
        })
        if (!result.ok) {
          out.error(result.error.display())
          process.exit(EXIT.ERROR)
        }
        if (args.json) {
          out.raw(result.value)
          return
        }
        if (result.value.items.length === 0) {
          out.info('No MCP servers found')
          return
        }
        out.table(
          result.value.items.map((c) => ({
            name: c.name,
            description: (c.description ?? '').slice(0, 60),
            installs: c.installs ?? '-',
            verified: c.verified ? 'yes' : '-',
          })),
          ['name', 'description', 'installs', 'verified']
        )
        if (result.value.hasMore) {
          out.info(`Page ${result.value.page}. Use --page ${result.value.page + 1} for more.`)
        }
      },
    }),

    add: defineCommand({
      meta: { name: 'add', description: 'Add an MCP server to a client config' },
      args: {
        ...globalArgs,
        source: {
          type: 'positional',
          description: 'Server source (smithery://ns/slug or URL)',
          required: true,
        },
        client: {
          type: 'string',
          alias: 'c',
          description: 'Target client (claude-desktop, cursor, vscode, ...)',
        },
        name: { type: 'string', description: 'Server name/ID in client config' },
        transport: {
          type: 'string',
          description: 'Transport type: stdio, http, http-oauth',
          default: 'http',
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const clientId = args.client as string | undefined

        if (!clientId) {
          out.info('Usage: agents mcp add <source> --client <client-name>')
          out.info('Available clients: claude-desktop, cursor, windsurf, vscode, cline, ...')
          out.info('Run: agents mcp add --help for full options')
          return
        }

        const { getClientConfig } = await import('@agents/core/component/clients')
        const clientConfig = getClientConfig(clientId)
        if (!clientConfig) {
          out.error(`Unknown client: "${clientId}"`)
          out.info('Available: claude-desktop, cursor, windsurf, vscode, cline, roo-code, ...')
          process.exit(EXIT.ERROR)
        }

        const serverName =
          (args.name as string) || (args.source as string).split('/').pop() || 'mcp-server'
        const { writeServerToClient } = await import('@agents/core/component/client-config')
        const result = await writeServerToClient(clientId, serverName, {
          name: serverName,
          transport: args.transport as string as 'stdio' | 'http' | 'http-oauth',
          url: args.source as string,
        })

        if (!result.ok) {
          out.error(result.error.display())
          process.exit(EXIT.ERROR)
        }
        out.success(`Added "${serverName}" to ${clientConfig.displayName}`)
      },
    }),

    list: defineCommand({
      meta: { name: 'list', description: 'List MCP servers in a client config' },
      args: {
        ...globalArgs,
        client: {
          type: 'string',
          alias: 'c',
          description: 'Client to list from',
          required: true,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const { listServersInClient } = await import('@agents/core/component/client-config')
        const result = await listServersInClient(args.client as string)
        if (!result.ok) {
          out.error(result.error.display())
          process.exit(EXIT.ERROR)
        }
        if (args.json) {
          out.raw(result.value)
          return
        }
        if (result.value.length === 0) {
          out.info('No MCP servers configured')
          return
        }
        out.table(
          result.value.map((s) => ({
            name: s.name,
            transport: s.transport,
            url: s.url ?? s.command ?? '-',
          })),
          ['name', 'transport', 'url']
        )
      },
    }),

    remove: defineCommand({
      meta: { name: 'remove', description: 'Remove an MCP server from a client config' },
      args: {
        ...globalArgs,
        name: { type: 'positional', description: 'Server name to remove', required: true },
        client: {
          type: 'string',
          alias: 'c',
          description: 'Target client',
          required: true,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const { removeServerFromClient } = await import('@agents/core/component/client-config')
        const result = await removeServerFromClient(args.client as string, args.name as string)
        if (!result.ok) {
          out.error(result.error.display())
          process.exit(EXIT.ERROR)
        }
        out.success(`Removed "${args.name}" from ${args.client}`)
      },
    }),

    info: defineCommand({
      meta: { name: 'info', description: 'Show details for an MCP server from Smithery' },
      args: {
        ...globalArgs,
        name: {
          type: 'positional',
          description: 'Server qualified name (namespace/slug)',
          required: true,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const manager = createComponentManager()
        const result = await manager.search({
          query: args.name as string,
          type: 'mcp-server',
          limit: 1,
        })
        if (!result.ok) {
          out.error(result.error.display())
          process.exit(EXIT.ERROR)
        }
        const server = result.value.items.find(
          (c) => c.name === args.name || c.name.includes(args.name as string)
        )
        if (!server) {
          out.error(`MCP server "${args.name}" not found`)
          process.exit(EXIT.ERROR)
        }
        if (args.json) {
          out.raw(server)
          return
        }
        out.info(`Name: ${server.name}`)
        out.info(`Description: ${server.description}`)
        if (server.url) out.info(`URL: ${server.url}`)
        if (server.installs) out.info(`Installs: ${server.installs}`)
        if (server.verified) out.info('Verified: yes')
        if (server.namespace) out.info(`Namespace: ${server.namespace}`)
      },
    }),

    publish: defineCommand({
      meta: { name: 'publish', description: 'Publish an MCP server to Smithery' },
      args: {
        ...globalArgs,
        name: {
          type: 'string',
          alias: 'n',
          description: 'Qualified name (namespace/server)',
          required: true,
        },
        url: { type: 'string', description: 'External server URL' },
        'bundle-dir': { type: 'string', description: 'Pre-built bundle directory' },
        'config-schema': { type: 'string', description: 'JSON Schema for server config' },
        'api-key': {
          type: 'string',
          description: 'Smithery API key (or set SMITHERY_API_KEY)',
        },
        'dry-run': {
          type: 'boolean',
          description: 'Validate without uploading',
          default: false,
        },
      },
      async run({ args }) {
        const out = createOutput({ json: args.json as boolean, quiet: args.quiet as boolean })
        const manager = createComponentManager()

        let configSchema: Record<string, unknown> | undefined
        if (args['config-schema']) {
          try {
            configSchema = JSON.parse(args['config-schema'] as string)
          } catch {
            out.error('Invalid JSON in --config-schema')
            process.exit(EXIT.ERROR)
          }
        }

        const result = await manager.publish('mcp-server', {
          name: args.name as string,
          apiKey: args['api-key'] as string | undefined,
          externalUrl: args.url as string | undefined,
          bundleDir: args['bundle-dir'] as string | undefined,
          configSchema,
          dryRun: args['dry-run'] as boolean,
        })

        if (!result.ok) {
          out.error(result.error.display())
          process.exit(EXIT.ERROR)
        }
        if (args.json) {
          out.raw(result.value)
          return
        }
        if (result.value.status === 'published') {
          out.success(`Published to ${result.value.registryUrl ?? 'Smithery'}`)
        } else if (result.value.status === 'failed') {
          out.error(`Publish failed: ${result.value.error ?? 'unknown'}`)
          process.exit(EXIT.FAILURES)
        }
        for (const w of result.value.warnings) out.warn(w)
      },
    }),
  },
})
