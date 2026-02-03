// cclint configuration for AI context repository
// Context files are symlinked into .claude/ so cclint discovers them naturally.
// Run with --follow-symlinks to lint both project-local and marketplace files.

export default {
  agentSchema: {
    extend: {
      // AskUserQuestion is a valid Claude Code tool not in cclint's built-in list
    },
  },

  commandSchema: {
    extend: {
      // AskUserQuestion is a valid Claude Code tool not in cclint's built-in list
    },
  },

  rules: {
    unknownFields: 'warning',
    excludePatterns: [
      '**/README.md',
      '**/TODO.md',
      '**/claude-code-dev-kit/**',
      '**/01-*/**',
      '**/02-*/**',
      '**/03-*/**',
      '**/04-*/**',
      '**/05-*/**',
      '**/06-*/**',
      '**/07-*/**',
      '**/08-*/**',
      '**/09-*/**',
      '**/10-*/**',
    ],
  },
}
