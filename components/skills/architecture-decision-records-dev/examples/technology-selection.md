# Example: Technology Selection ADR

```markdown
---
id: a1b2c3d4-e5f6-7890-abcd-ef1234567890
project:
  id: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
title: "ADR-002: Use clap for CLI Argument Parsing"
status: accepted
tags: [adr, cli, rust]
related:
  supersedes: []
  depends-on: [f0e1d2c3-b4a5-6789-0abc-def123456789]
---

# ADR-002: Use clap for CLI Argument Parsing

## Status

Accepted

## Date

2025-11-15

## Deciders

- @aRustyDev (maintainer)

## Context and Problem Statement

git-atomic needs to parse complex CLI arguments including subcommands,
flags, positional arguments, and git-style options (e.g., `--no-verify`).
The parser must produce helpful error messages and support shell completions.

As a git subcommand, the CLI surface is the primary user interface.
Poor argument parsing directly degrades user experience.

## Decision Drivers

- Derive macro support (reduce boilerplate)
- Quality of auto-generated help and error messages
- Shell completion generation
- Ecosystem adoption and maintenance activity
- Compile time impact

## Considered Options

### Option 1: clap (derive)

Full-featured argument parser with derive macro support.

| Pros | Cons |
|------|------|
| Derive macros reduce boilerplate | Slower compile times (~4s added) |
| Excellent error messages out of the box | Large dependency tree (50+ transitive) |
| Built-in shell completion generation | Learning curve for advanced features |
| Most popular Rust CLI library | |

### Option 2: argh

Google's derive-based argument parser focused on simplicity.

| Pros | Cons |
|------|------|
| Minimal dependency tree | No shell completion generation |
| Fast compile times | Less flexible subcommand handling |
| Simple derive API | Smaller community, fewer examples |
| | Limited error message customization |

### Option 3: pico-args

Zero-dependency, manual argument parser.

| Pros | Cons |
|------|------|
| Zero dependencies | No derive macros (manual parsing) |
| Fastest compile times | No auto-generated help text |
| Full control over parsing | No shell completions |
| | More code to write and maintain |

## Decision Outcome

Chose **Option 1: clap (derive)** because shell completion generation and
quality error messages are critical for a git subcommand. The compile time
cost is acceptable given the significant reduction in boilerplate and
maintenance burden. Ecosystem dominance means better documentation and
community support.

## Diagram

` ``mermaid
graph TD
    A[User Input] --> B[clap Parser]
    B --> C{Subcommand}
    C --> D[atomic commit]
    C --> E[atomic branch]
    C --> F[atomic config]
    B --> G[Shell Completions]
    G --> H[bash/zsh/fish]
    B --> I[Help Text]
    B --> J[Error Messages]
` ``

## Consequences

### Positive

- Derive macros keep CLI definition co-located with types
- Shell completions available for bash, zsh, fish, PowerShell
- Error messages guide users to correct usage

### Negative

- Adds ~4s to clean build time
- 50+ transitive dependencies increase audit surface
- Upgrading clap major versions requires migration effort

### Neutral

- clap is the de facto standard — new contributors will expect it
- Version 4.x API is stable with no breaking changes expected soon

## References

- [clap documentation](https://docs.rs/clap)
- [ADR-001: Use Rust for git-atomic](./adr-001-use-rust-for-git-atomic.md)
```
