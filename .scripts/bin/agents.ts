#!/usr/bin/env bun
import { defineCommand, runMain } from 'citty'

const main = defineCommand({
  meta: { name: 'agents', version: '0.1.0', description: 'AI context library tooling' },
  subCommands: {
    plugin: () => import('../commands/plugin').then((m) => m.default),
    skill: () => import('../commands/skill').then((m) => m.default),
    mcp: () => import('../commands/mcp').then((m) => m.default),
    component: () => import('../commands/component').then((m) => m.default),
    kg: () => import('../commands/kg').then((m) => m.default),
    registry: () => import('../commands/registry').then((m) => m.default),
    'graph-viewer': () => import('../commands/graph-viewer').then((m) => m.default),
  },
})

runMain(main)
