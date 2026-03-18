import { defineCommand } from 'citty'
import { globalArgs } from './shared-args'

export default defineCommand({
  meta: { name: 'skill', description: 'Skill validation, hashing, and dependency management' },
  subCommands: {
    validate: defineCommand({
      meta: { name: 'validate', description: 'Validate SKILL.md frontmatter and structure' },
      args: { ...globalArgs, name: { type: 'positional', description: 'Skill name', required: true } },
      run() { console.error('skill validate: not yet implemented (Phase 4a)'); process.exit(2) },
    }),
    hash: defineCommand({
      meta: { name: 'hash', description: 'Compute skill directory hash' },
      args: { ...globalArgs, name: { type: 'positional', description: 'Skill name', required: true } },
      run() { console.error('skill hash: not yet implemented (Phase 4a)'); process.exit(2) },
    }),
    lint: defineCommand({
      meta: { name: 'lint', description: 'Lint skill files (via cclint)' },
      args: { ...globalArgs, name: { type: 'positional', description: 'Skill name' } },
      run() { console.error('skill lint: not yet implemented (Phase 4a)'); process.exit(2) },
    }),
    'check-all': defineCommand({
      meta: { name: 'check-all', description: 'Validate all skills' },
      args: { ...globalArgs },
      run() { console.error('skill check-all: not yet implemented (Phase 4a)'); process.exit(2) },
    }),
    deps: defineCommand({
      meta: { name: 'deps', description: 'Manage external skill dependencies' },
      subCommands: {
        check: defineCommand({
          meta: { name: 'check', description: 'Check upstream drift and symlink health' },
          args: { ...globalArgs },
          run() { console.error('skill deps check: not yet implemented (Phase 4b)'); process.exit(2) },
        }),
        sync: defineCommand({
          meta: { name: 'sync', description: 'Sync external dependencies, update lockfile' },
          args: { ...globalArgs, force: { type: 'boolean', description: 'Force sync all', default: false } },
          run() { console.error('skill deps sync: not yet implemented (Phase 4b)'); process.exit(2) },
        }),
        issues: defineCommand({
          meta: { name: 'issues', description: 'Open GH issues for upstream drift' },
          args: { ...globalArgs, dryRun: { type: 'boolean', description: 'Preview without creating', default: false } },
          run() { console.error('skill deps issues: not yet implemented (Phase 4b)'); process.exit(2) },
        }),
        links: defineCommand({
          meta: { name: 'links', description: 'Create/refresh passthrough symlinks' },
          args: { ...globalArgs },
          run() { console.error('skill deps links: not yet implemented (Phase 4b)'); process.exit(2) },
        }),
        status: defineCommand({
          meta: { name: 'status', description: 'Show combined dependency status' },
          args: { ...globalArgs },
          run() { console.error('skill deps status: not yet implemented (Phase 4b)'); process.exit(2) },
        }),
      },
    }),
  },
})
