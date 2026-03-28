#!/usr/bin/env bun
import { defineCommand, runMain } from 'citty'
import { build } from './build'

const buildCommand = defineCommand({
  meta: { name: 'build', description: 'Build the matrix review viewer HTML' },
  args: {
    workspace: {
      type: 'positional',
      description: 'Path to the workspace directory',
      required: true,
    },
    'skill-path': {
      type: 'string',
      description: 'Path to the skill directory (auto-detected if omitted)',
    },
    output: {
      type: 'string',
      alias: 'o',
      description: 'Output HTML file path',
    },
    iteration: {
      type: 'string',
      alias: 'i',
      description: 'Iteration number (default: latest)',
    },
    open: {
      type: 'boolean',
      description: 'Open in browser after build',
      default: true,
    },
    previous: {
      type: 'string',
      description: 'Previous iteration workspace path (for diff view)',
    },
  },
  async run({ args }) {
    try {
      const outputPath = await build({
        workspace: args.workspace as string,
        skillPath: args['skill-path'] as string | undefined,
        output: args.output as string | undefined,
        iteration: args.iteration ? parseInt(args.iteration as string) : undefined,
        open: args.open as boolean,
        previous: args.previous as string | undefined,
      })
      console.log(`Viewer built: ${outputPath}`)
    } catch (err) {
      console.error(`Error: ${(err as Error).message}`)
      process.exit(1)
    }
  },
})

const main = defineCommand({
  meta: { name: 'matrixng', version: '0.1.0', description: 'Search matrix review viewer' },
  subCommands: {
    build: () => Promise.resolve(buildCommand),
  },
})

runMain(main)
