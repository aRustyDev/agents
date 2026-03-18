import { defineCommand } from 'citty'
import { globalArgs } from './shared-args'

export default defineCommand({
  meta: { name: 'plugin', description: 'Plugin build and verification' },
  subCommands: {
    build: defineCommand({
      meta: { name: 'build', description: 'Build a plugin (copy sources, verify hashes)' },
      args: {
        ...globalArgs,
        name: { type: 'positional', description: 'Plugin name', required: true },
        force: { type: 'boolean', description: 'Force rebuild', default: false },
        checkOnly: { type: 'boolean', description: 'Verify without copying', default: false },
        updateHashes: { type: 'boolean', description: 'Update hashes after build', default: false },
      },
      run({ args }) {
        console.error(`plugin build: not yet implemented (Phase 3)`)
        process.exit(2)
      },
    }),
    check: defineCommand({
      meta: { name: 'check', description: 'Verify plugin source hashes' },
      args: { ...globalArgs, name: { type: 'positional', description: 'Plugin name', required: true } },
      run() { console.error('plugin check: not yet implemented (Phase 3)'); process.exit(2) },
    }),
    hash: defineCommand({
      meta: { name: 'hash', description: 'Compute hash of a path' },
      args: { ...globalArgs, path: { type: 'positional', description: 'File or directory', required: true } },
      run() { console.error('plugin hash: not yet implemented (Phase 3)'); process.exit(2) },
    }),
    lint: defineCommand({
      meta: { name: 'lint', description: 'Lint plugin Claude Code files (via cclint)' },
      args: { ...globalArgs, name: { type: 'positional', description: 'Plugin name' } },
      run() { console.error('plugin lint: not yet implemented (Phase 3)'); process.exit(2) },
    }),
    'check-all': defineCommand({
      meta: { name: 'check-all', description: 'Verify all plugin sources' },
      args: { ...globalArgs },
      run() { console.error('plugin check-all: not yet implemented (Phase 3)'); process.exit(2) },
    }),
    'build-all': defineCommand({
      meta: { name: 'build-all', description: 'Build all plugins' },
      args: { ...globalArgs, force: { type: 'boolean', default: false }, updateHashes: { type: 'boolean', default: false } },
      run() { console.error('plugin build-all: not yet implemented (Phase 3)'); process.exit(2) },
    }),
  },
})
