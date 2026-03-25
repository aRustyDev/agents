#!/usr/bin/env bun
import { defineCommand, runMain } from 'citty'

const main = defineCommand({
  meta: { name: 'agents', version: '0.1.0', description: 'AI context library tooling' },
  subCommands: {
    // Verb-first commands (Phase 7)
    add: () => import('../commands/add').then((m) => m.default),
    remove: () => import('../commands/remove').then((m) => m.default),
    list: () => import('../commands/list').then((m) => m.default),
    search: () => import('../commands/search').then((m) => m.default),
    info: () => import('../commands/info').then((m) => m.default),
    init: () => import('../commands/init').then((m) => m.default),
    lint: () => import('../commands/lint').then((m) => m.default),
    update: () => import('../commands/update').then((m) => m.default),
    // Pipeline operations (noun-first exceptions)
    catalog: () => import('../commands/catalog').then((m) => m.default),
    // Legacy noun-first commands (to be aliased in 7.3)
    plugin: () => import('../commands/plugin').then((m) => m.default),
    skill: () => import('../commands/skill').then((m) => m.default),
    mcp: () => import('../commands/mcp').then((m) => m.default),
    // Configuration
    config: () => import('../commands/config').then((m) => m.default),
    // Other
    component: () => import('../commands/component').then((m) => m.default),
    kg: () => import('../commands/kg').then((m) => m.default),
    registry: () => import('../commands/registry').then((m) => m.default),
    'graph-viewer': () => import('../commands/graph-viewer').then((m) => m.default),
    completions: () => import('../commands/completions').then((m) => m.default),
  },
})

runMain(main)
