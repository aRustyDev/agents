# Plugin Feedback Infrastructure Brainstorm

**Issue**: ai-44c
**Status**: Refined

## Research Findings

### What Exists (Legacy)

| Component | Location | Status |
|-----------|----------|--------|
| `/report` command system | `content/.content/legacy/prompts/commands/report*` | Legacy, not migrated |
| Bug memory filesystem | `content/.content/legacy/memory/bugs/` | Legacy pattern |
| Bug report template | `content/.content/legacy/prompts/templates/issues/bug-report.md` | Legacy |
| GitHub issue templates | `.github/ISSUE_TEMPLATE/*.yml` | Active, component-focused |

### What's Missing

1. **No feedback commands** - Legacy `/report` system never migrated
2. **No user-facing issue templates** - All templates are for adding components
3. **No CONTRIBUTING.md** - Not at repo root or in any plugin
4. **No plugin documentation** - `docs/` directories are stub placeholders
5. **No CHANGELOG.md** - No version history tracking
6. **config.yml incomplete** - Only links to README, no bug/feedback options

## Gap Analysis & Refinements

### Identified Gaps

| Gap | Impact | Resolution |
|-----|--------|------------|
| config.yml only links to README | Users can't find help | Add bug report + discussions links |
| No GitHub Discussions | No Q&A channel | Enable and link in config.yml |
| CHANGELOG format unspecified | Inconsistent histories | Use Keep a Changelog format |
| Template style inconsistency | Poor UX | Match existing add-*.yml structure |
| Phase 2 too large | Hard to track | Split into sub-tasks |
| No acceptance criteria | Unclear done state | Add to each phase |
| scaffold.md not updated | Missing from report | Add docs to generated files list |

### Design Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| Command name: `/report` or `/feedback`? | `/feedback` | Clearer user intent, avoids confusion with reporting tools |
| GitHub issues or local files? | GitHub issues | Centralized, searchable, collaborative |
| Auto-context level? | Moderate | Plugin versions + recent command, not full logs |

## Refined Implementation Plan

### Phase 1: GitHub Issue Templates (P0)

#### 1.1 Create bug-report.yml

```yaml
name: Bug Report
description: Report a bug in a plugin, skill, or command
title: "[BUG] "
labels: ["bug", "triage"]
body:
  - type: dropdown (affected component type)
  - type: input (component name)
  - type: input (version)
  - type: textarea (reproduction steps)
  - type: textarea (expected vs actual)
  - type: dropdown (severity)
  - type: textarea (environment)
  - type: checkboxes (pre-submission)
```

**Acceptance Criteria:**

- [ ] Template matches existing add-*.yml style
- [ ] All required fields have validation
- [ ] Labels auto-applied on creation

#### 1.2 Create feature-request.yml

```yaml
name: Feature Request
description: Suggest a new feature or enhancement
title: "[FEATURE] "
labels: ["enhancement"]
body:
  - type: dropdown (component type)
  - type: textarea (use case)
  - type: textarea (proposed solution)
  - type: textarea (alternatives considered)
  - type: checkboxes (pre-submission)
```

**Acceptance Criteria:**

- [ ] Template matches existing style
- [ ] Clear distinction from add-*.yml templates

#### 1.3 Update config.yml

Add contact links:

- Bug reports (link to bug-report template)
- Feature requests (link to feature-request template)
- Discussions (link to GitHub Discussions)

**Acceptance Criteria:**

- [ ] All links functional
- [ ] Descriptions clear and helpful

#### 1.4 Enable GitHub Discussions

Enable GitHub Discussions for positive feedback and success stories.

Categories to create:

- 🎉 Success Stories - Share how plugins/skills helped you
- 💡 Ideas & Suggestions - Open-ended feature discussions
- ❓ Q&A - Questions and help

**Acceptance Criteria:**

- [ ] GitHub Discussions enabled
- [ ] At least 3 categories created
- [ ] config.yml includes Discussions link

#### 1.5 Create feedback-submission output style

Location: `content/output-styles/feedback-submission.md`

Output style for formatting feedback submissions with templates for:

- Bug Report (component, version, severity, reproduction steps)
- Feature Request (use case, proposed solution, alternatives)
- Success Story (accomplishment, how it helped, tips)

**Acceptance Criteria:**

- [ ] Output style supports all 3 feedback types
- [ ] Clear section markers for each type
- [ ] Examples included for guidance

---

### Phase 2: Plugin Template Documentation (P0)

#### 2.1 Create USAGE.md template

Location: `content/plugins/.template/docs/USAGE.md`

Sections:

- Installation
- Quick Start
- Commands (placeholder table)
- Skills (placeholder table)
- Configuration
- Examples

**Acceptance Criteria:**

- [ ] Clear structure with placeholders
- [ ] Instructions for customization

#### 2.2 Create TROUBLESHOOTING.md template

Location: `content/plugins/.template/docs/TROUBLESHOOTING.md`

Sections:

- Common Issues (table: symptom, cause, solution)
- FAQ
- Getting Help (link to bug report)
- Debug Mode instructions

**Acceptance Criteria:**

- [ ] At least 3 placeholder issues
- [ ] Links to feedback channels

#### 2.3 Create CHANGELOG.md template

Location: `content/plugins/.template/CHANGELOG.md`

Format: [Keep a Changelog](https://keepachangelog.com/)

```markdown
# Changelog

All notable changes to this plugin will be documented in this file.

## [Unreleased]

## [0.1.0] - YYYY-MM-DD

### Added

- Initial release
```

**Acceptance Criteria:**

- [ ] Follows Keep a Changelog format
- [ ] Unreleased section at top
- [ ] Version links at bottom

#### 2.4 Create CONTRIBUTING.md template

Location: `content/plugins/.template/CONTRIBUTING.md`

Sections:

- How to Contribute
- Development Setup
- Adding Components (commands, skills, agents)
- Testing
- Pull Request Process

**Acceptance Criteria:**

- [ ] Plugin-specific, not repo-level
- [ ] Clear step-by-step instructions

#### 2.5 Update docs/SUMMARY.md

Replace stub with:

```markdown
# Summary

- [Usage](./USAGE.md)
- [Troubleshooting](./TROUBLESHOOTING.md)
```

**Acceptance Criteria:**

- [ ] Links to actual documentation
- [ ] mdBook compatible

#### 2.6 Update scaffold.md

- Add docs files to generated files list in Step 10
- Ensure CHANGELOG.md and CONTRIBUTING.md are copied

**Acceptance Criteria:**

- [ ] Report shows all generated files
- [ ] Scaffold copies all template files

---

### Phase 3: Feedback Command (P1)

#### 3.1 Create /feedback command

Location: `content/commands/feedback.md`

Subcommands:

- `/feedback bug` - Opens bug report with auto-context
- `/feedback feature` - Opens feature request
- `/feedback` - Interactive menu

Auto-gathered context:

- Current working directory
- Installed plugins (from marketplace.json)
- Recent command (if available)
- Claude Code version

**Acceptance Criteria:**

- [ ] All subcommands functional
- [ ] Context gathering non-intrusive
- [ ] Opens browser to pre-filled GitHub issue

---

### Phase 4: Retrofit Existing Plugins (P2)

#### 4.1 Create retrofit justfile task

```just
add-feedback-infra plugin:
  # Copy template docs to plugin
  # Generate CHANGELOG from git log
  # Add CONTRIBUTING.md
```

**Acceptance Criteria:**

- [ ] Works on all existing plugins
- [ ] Non-destructive (doesn't overwrite existing)
- [ ] Reports what was added

#### 4.2 Retrofit existing plugins

Apply to:

- homebrew-dev
- browser-extension-dev
- blog-workflow
- job-hunting

**Acceptance Criteria:**

- [ ] All plugins have USAGE.md
- [ ] All plugins have TROUBLESHOOTING.md
- [ ] All plugins have CHANGELOG.md
- [ ] All plugins have CONTRIBUTING.md

---

## Dependencies

- ✅ Template fixes (ai-brx, ai-gmn, ai-dok, ai-b8p)
- ✅ Marketplace.json step (ai-p4n)

## Issue Breakdown

| ID | Title | Phase | Priority | Blocks | Beads |
|----|-------|-------|----------|--------|-------|
| 1 | Create bug-report.yml template | 1.1 | P0 | 1.3 | ai-s67 |
| 2 | Create feature-request.yml template | 1.2 | P0 | 1.3 | ai-vao |
| 3 | Update config.yml with feedback links | 1.3 | P0 | — | ai-9vt |
| 4 | Enable GitHub Discussions | 1.4 | P0 | 1.3 | ai-u4w |
| 5 | Create feedback-submission output style | 1.5 | P0 | 3.1 | ai-74w |
| 6 | Create USAGE.md template | 2.1 | P0 | 2.6 | ai-1lq |
| 7 | Create TROUBLESHOOTING.md template | 2.2 | P0 | 2.6 | ai-cax |
| 8 | Create CHANGELOG.md template | 2.3 | P0 | 2.6 | ai-5nf |
| 9 | Create CONTRIBUTING.md template | 2.4 | P0 | 2.6 | ai-mvz |
| 10 | Update docs/SUMMARY.md | 2.5 | P0 | 2.6 | ai-oub |
| 11 | Update scaffold.md for docs | 2.6 | P0 | — | ai-ehi |
| 12 | Create /feedback command | 3.1 | P1 | — | ai-947 |
| 13 | Create retrofit justfile task | 4.1 | P2 | 4.2 | ai-aap |
| 14 | Retrofit existing plugins | 4.2 | P2 | — | ai-18p |
