# Feedback Submission

Output style for formatting user feedback submissions. Use this style when helping users submit bug reports, feature requests, or success stories.

## Bug Report Format

When the user wants to report a bug, gather information and format as:

```markdown
## Bug Report

**Component**: <plugin/skill/command name>
**Type**: <Plugin|Skill|Command|Agent|MCP Server|Hook|Other>
**Version**: <version from plugin.json or SKILL.md>
**Severity**: <Critical|High|Medium|Low>

### Steps to Reproduce

1. <step 1>
2. <step 2>
3. <step 3>

### Expected Behavior

<what should have happened>

### Actual Behavior

<what actually happened, include error messages>

### Environment

- OS: <operating system and version>
- Claude Code version: <version>
- Shell: <shell and version>

### Additional Context

<any other relevant information, logs, screenshots>
```

## Feature Request Format

When the user wants to request a feature, gather information and format as:

```markdown
## Feature Request

**Component**: <plugin/skill/command name, or "New">
**Type**: <Plugin|Skill|Command|Agent|MCP Server|Hook|Other|New>

### Use Case

<describe the problem or workflow improvement>

As a <role>, I want to <action> so that <benefit>.

### Proposed Solution

<how the feature should work>

1. <step 1>
2. <step 2>
3. <step 3>

### Alternatives Considered

- <alternative 1>: <why not chosen>
- <alternative 2>: <why not chosen>

### Priority

<Nice to have|Would significantly improve workflow|Critical for use case>
```

## Success Story Format

When the user wants to share a positive experience, gather information and format as:

```markdown
## Success Story

**Component**: <plugin/skill/command name>
**Type**: <Plugin|Skill|Command|Agent|MCP Server>

### What I Accomplished

<describe what you built or achieved>

### How It Helped

<describe the time saved, quality improvement, or other benefits>

- <benefit 1>
- <benefit 2>
- <benefit 3>

### Tips for Others

<advice for others who want to achieve similar results>

1. <tip 1>
2. <tip 2>
3. <tip 3>

### Would Recommend?

<Yes|Yes, with caveats|For specific use cases>
```

## Submission Guidance

After formatting the feedback:

1. **Bug Reports**: Direct user to create a GitHub issue using the bug-report template
2. **Feature Requests**: Direct user to create a GitHub issue using the feature-request template
3. **Success Stories**: Direct user to GitHub Discussions under the "Success Stories" category

Provide the appropriate link:

- Bug Report: `https://github.com/aRustyDev/ai/issues/new?template=bug-report.yml`
- Feature Request: `https://github.com/aRustyDev/ai/issues/new?template=feature-request.yml`
- Success Story: `https://github.com/aRustyDev/ai/discussions/new?category=success-stories`
