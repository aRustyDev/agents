---
name: blog/init
description: Initialize blog workflow directory structure and copy default templates
argument-hint: [--force] [--no-templates] [--with-hooks]
arguments:
  - name: force
    description: Overwrite existing templates
    required: false
  - name: no-templates
    description: Create directories only, skip template copying
    required: false
  - name: with-hooks
    description: Generate .claude/settings.json with hook configuration
    required: false
---

# Init Command

Initialize the blog workflow in the target project by creating directory structure and copying bundled templates.

## Tools

- `Glob` - Check existing structure
- `Bash` - Create directories
- `Read` - Load bundled templates
- `Write` - Copy templates to project

## Behavior

1. **Check existing structure**:
   - Use `Glob` to check if `content/_templates/` exists
   - If exists and `--force` not set, list existing files and report

2. **Create directory structure**:

   ```bash
   mkdir -p content/_projects
   mkdir -p content/_drafts
   mkdir -p content/_templates/personas
   mkdir -p content/_templates/outlines
   mkdir -p content/_templates/research-plans
   mkdir -p content/_templates/review-checklists
   mkdir -p content/_templates/brainstorm-plans
   ```

3. **Copy bundled templates** (unless `--no-templates`):

   From plugin `.templates/` copy to `content/_templates/`:

   | Source | Destination | Count |
   |--------|-------------|-------|
   | `.templates/outlines/*.md` | `outlines/` | 18 |
   | `.templates/personas/*.md` | `personas/` | 2 |
   | `.templates/research-plans/*.md` | `research-plans/` | 1 |
   | `.templates/review-checklists/*.md` | `review-checklists/` | 12 |
   | `.templates/brainstorm-plans/*.md` | `brainstorm-plans/` | 1 |

   For each template:
   - Read from plugin bundle
   - Write to project location
   - Skip if exists (unless `--force`)
   - Track created vs skipped

4. **Generate settings.json** (if `--with-hooks`):

   a. Check if `.claude/settings.json` exists

   b. If exists, merge hook configuration:
   - Parse existing JSON
   - Add/update PostToolUse and PreToolUse hooks
   - Preserve other settings

   c. If not exists, create with blog workflow hooks:

   ```json
   {
     "hooks": {
       "PostToolUse": [
         {
           "matcher": "Write|Edit",
           "hooks": [
             {
               "type": "command",
               "command": "bash -c 'FILE=\"$TOOL_INPUT_FILE_PATH\"; case \"$FILE\" in content/_drafts/*|content/_projects/*) ~/.claude/plugins/blog-workflow/hooks/validate-blog-frontmatter.sh \"$FILE\";; esac; true'",
               "timeout": 10
             }
           ]
         }
       ],
       "PreToolUse": [
         {
           "matcher": "Write",
           "hooks": [
             {
               "type": "command",
               "command": "bash -c 'FILE=\"$TOOL_INPUT_FILE_PATH\"; case \"$FILE\" in src/data/blog/*) ~/.claude/plugins/blog-workflow/hooks/promote-safety.sh \"$FILE\";; esac; true'",
               "timeout": 5
             }
           ]
         }
       ]
     }
   }
   ```

5. **Self-review**:
   - Verify all directories exist using `Glob`
   - Verify template counts match expected
   - Report any missing files

6. **Report summary**

## Output (Success)

```text
## Blog Workflow Initialized

### Directories Created
- [x] content/_projects/
- [x] content/_drafts/
- [x] content/_templates/personas/
- [x] content/_templates/outlines/
- [x] content/_templates/research-plans/
- [x] content/_templates/review-checklists/
- [x] content/_templates/brainstorm-plans/

### Templates Copied
- 18 outline templates
- 2 persona templates (practitioner.md, educator.md)
- 1 research plan template
- 12 review checklists
- 1 brainstorm plan template

Total: 34 templates

### Hooks
{{if --with-hooks}}
- [x] .claude/settings.json created/updated
{{else}}
- [ ] Hooks not configured (use --with-hooks to enable)
{{/if}}

## Next Steps

1. Review personas in `content/_templates/personas/`
2. Customize templates as needed
3. Start with: `/blog/idea/brainstorm "Your topic"`
```

## Output (Partial - Existing Structure)

```text
## Blog Workflow Initialization

### Existing Structure Detected

The following already exists:
- content/_templates/outlines/ (18 files)
- content/_templates/personas/ (2 files)

Options:
1. Run `/blog/init --force` to overwrite
2. Run `/blog/init --no-templates` to create missing directories only
3. Manually review and update templates

### Directories
- [x] content/_projects/ (exists)
- [x] content/_drafts/ (created)
- [x] content/_templates/ (exists)
```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Permission denied | "Cannot create directory: {{path}}" | Check write permissions |
| Plugin templates missing | "Plugin templates not found at {{path}}" | Reinstall plugin |
| Partial copy failure | "Failed to copy: {{file}}" | Check disk space, retry |
| Settings.json parse error | "Invalid JSON in .claude/settings.json" | Fix JSON syntax |
| Settings.json conflict | "Existing hooks detected" | Show diff, suggest merge |

## Example Usage

```text
# Full initialization
/blog/init

# Directories only (no templates)
/blog/init --no-templates

# Overwrite existing templates
/blog/init --force

# Include hook configuration
/blog/init --with-hooks

# Full setup with hooks
/blog/init --force --with-hooks
```
