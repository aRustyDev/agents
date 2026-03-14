# Changelog

All notable changes to this plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.2] - 2026-03-14

### Added

- Add `argument-hint` to all 31 commands for ghost text hints in Claude Code

### Fixed

- Fix command name separators (`:` to `/`) for consistent namespace

## [2.0.1] - 2026-03-14

### Fixed

- Remove unsupported `hooks` and `requiredDirectories` fields from manifest

## [2.0.0] - 2026-03-14

### Added

- Full phase workflow: idea -> research -> content -> post -> publish
- Persona system with practitioner and educator defaults
- 18 outline templates for different post types
- Hook delegation model for customization
- `/blog/init` command for project setup
- Template frontmatter specifications
- Review checklists for all phases
- SEO review and pre-check commands
- Promote/validate publish workflow

### Changed

- Command namespace: legacy commands -> `/blog/` prefix
- Template location: organized in `.templates/`
- Version bump from 1.6.0 to 2.0.0 (major redesign)

### Deprecated

- Legacy commands (`draft-post`, `gather-resources`, `outline-post`, `publish-prep`, `refine-research-plan`, `research-topic`, `seo-pass`)
- Will be removed in v3.0.0

### Migration

See README.md for migration guide from v1.x commands.

## [1.6.0] - 2026-03-14

### Added

- Publish commands: seo-review, pre-check, promote, validate
- Hook scripts: validate-blog-frontmatter.sh, promote-safety.sh
- SEO review checklist

## [1.5.0] - 2026-03-14

### Added

- Post writing commands: spec, plan, draft, review, refine
- Post specification and outline templates
- Post review checklists

## [1.4.0] - 2026-03-14

### Added

- Content planning commands: draft, plan, review, refine
- Content brainstorm and phase templates
- Content review checklists

## [1.3.0] - 2026-03-14

### Added

- Research commands: spec/draft, spec/plan, spec/review, draft, plan, refine, review
- Research templates and checklists

## [1.2.0] - 2026-03-14

### Added

- Persona/template management commands
- Idea phase commands: brainstorm, review, refine, draft-plan

## [1.0.6] - 2026-02-20

### Changed

- Migrated plugin.sources.json to extended format with content-addressed hashing
- Internalized feedback-submission.md output style (previously external reference)
- Added SHA256 hash verification for shared components

## [1.0.5] - 2026-02-19

### Added

- Initial plugin structure

## [0.1.0] - YYYY-MM-DD

### Added

- Initial release
- Basic plugin structure with commands, skills, and agents directories
- MCP server configuration
- Documentation templates

[Unreleased]: https://github.com/aRustyDev/ai/compare/blog-workflow-v0.1.0...HEAD
[0.1.0]: https://github.com/aRustyDev/ai/releases/tag/blog-workflow-v0.1.0

## Git History

```
02c289d No signature
fix: remove explicit hooks field from all plugin manifests
bdca651 No signature
fix(blog-workflow): correct hooks.json structure to use event type keys
ce70eed No signature
fix: use explicit file arrays in plugin manifests instead of directory paths
b4b4695 No signature
chore(blog-workflow): bump version to 1.0.2
5ff0c38 No signature
fix(blog-workflow): remove .gitkeep from agents directory
a45cc9b No signature
chore(blog-workflow): bump version to 1.0.1
b00750c No signature
fix(blog-workflow): remove unsupported extends field from agents
2b7385c No signature
feat(blog-workflow): Complete P2 - series-architect agent
7b16cbe No signature
feat(blog-workflow): Implement P1 components
e046995 No signature
feat(blog-workflow): Implement P0 components
```
