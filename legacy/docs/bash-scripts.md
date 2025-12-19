# Bash Scripts

Claude Code operates within your development environment and can reliably create easy-medium complexity bash scripts to automate various processes. These scripts are particularly useful because he can iterate on them and test the functionality using standard system utilities.

During my usage of Claude Code I observed one of the slowest processes is edit/writing operations.

### Claude's explanation of the lag

- Tool call overhead: Each edit requires a separate API invocation with network latency.
- Safety validation: Every operation needs confirmation and error checking before execution.
- Sequential processing: File operations happen one-at-a-time rather than in parallel batches.
- Context switching: Managing state across multiple files creates cognitive overhead.
- Token processing: Large edits consume significant input/output token processing time.

My solution was to create a Bash script that performs multiple write/edit operations asynchronously, reducing multiple tool call round trips into a single execution. The script takes a JSON input file defining the absolute file paths to target files, the specific file names to create or edit, the exact line numbers that need modification, and the new content that should replace or be inserted into those locations.

My CLAUDE.md was then updated to inform Claude of the system's existence so that I could opt into using it when necessary.

Performing multiple writes with a bash script is token efficient but not as fast as Task/ Agent based orchestration (though Task/ Agent based orchestration is more costly token wise).

Implementing this mechanic can speed up write/edit dependent workflows significantly depending on how many write/edit operations you need to perform and their complexity.

### Mechanic Benefits:

- **Reduced API overhead**: Single tool call instead of multiple individual edit operations.
- **Batch processing**: Handle dozens of files simultaneously in one execution.
- **Token efficiency**: Lower overall token consumption compared to sequential edits.
- **Asynchronous execution**: Files processed in parallel rather than sequentially.
- **JSON-driven workflow**: Structured, predictable input format for complex operations.
- **Reusable automation**: Scripts can be saved and reused for similar future tasks.
- **Network latency reduction**: Eliminates multiple round-trips between Claude and your system.

### Benchmark

Consider having Claude build a Bash-based benchmarking tool that can measure and compare different speed optimisation mechanics.
