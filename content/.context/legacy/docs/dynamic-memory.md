# Dynamic Memory

When Claude Code is in interactive mode you can have Claude modify its own CLAUDE.md temporarily to run tasks with a specific context. After the task is completed you can ask Claude to revert the CLAUDE.md back to its previous state. There are several ways of backing up the CLAUDE.md:

- **Git versioning**: Use git stash or commit before changes for easy rollback.
- **File duplication**: Have Claude copy to a backup filename like CLAUDE.md.backup.

To change the information persisted through the CLAUDE.md interface you can use 'quick Memory' with #.

This mechanic is useful if you have a CLAUDE.md library which specifies the processes for performing different tasks. Unfortunately, Claude is currently unable to read changes to his CLAUDE.md into 'memory' unless it utilises explicit commands such as:

- **Quick Memory**: Using # commands to temporarily change persisted information.
- **Memory refresh commands**: Explicitly asking Claude to re-read the modified CLAUDE.md.
- **Session restart**: Starting a new Claude Code session to pick up changes.
- **Explicit file** reads: Using read commands to load the updated content.

This led to me exploring getting Claude to spawn another instance of itself in a directory which has a different CLAUDE.md. The benefits being:

- **Cleaner context separation**: Each spawned instance operates with its own specific CLAUDE.md context.
- **No memory reload issues**: New instances automatically load their directory's CLAUDE.md.
- **Parallel processing**: Multiple contexts can run simultaneously without interference.
- **Reduced context pollution**: Previous session context doesn't bleed into the new specialized task.

**Note**: Claude instances will automatically crawl up the directory structure and read any CLAUDE.md files they encounter. So to have a strict separation of context ensure the project directory CLAUDE.md is lightweight and non-specific.

### Directory Crawling

Claude instances will automatically crawl up the directory structure and read any CLAUDE.md files they encounter. So to have a strict separation of context ensure the project directory CLAUDE.md is lightweight and non-specific.
