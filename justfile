set unstable := true
# Claude Code configuration directory

CLAUDE_DIR := env("HOME") / ".claude"
EMBEDDING_MODEL := "nomic-embed-text"

# Install project dependencies (idempotent)
[group('install')]
init: _init-brew _init-python _init-docker _init-ollama _init-db
    @echo "✓ Project initialized"

[private]
_init-brew:
    @echo "Installing Homebrew dependencies..."
    @brew bundle --quiet

[private]
_init-python:
    @echo "Installing Python dependencies..."
    @uv sync --quiet

[private]
_init-docker: mcp-up

[private]
_init-ollama:
    #!/usr/bin/env bash
    echo "Checking Ollama embedding model..."
    if ollama list 2>/dev/null | grep -q "{{ EMBEDDING_MODEL }}"; then
        echo "  ✓ {{ EMBEDDING_MODEL }} available"
    else
        echo "  Pulling {{ EMBEDDING_MODEL }}..."
        ollama pull "{{ EMBEDDING_MODEL }}" || echo "  ⚠ Ollama not running - will use sentence-transformers fallback"
    fi

[private]
_init-db:
    @echo "Initializing knowledge graph database..."
    @just kg-init

# Docker MCP services
[group('docker')]
mcp-up:
    @"{{ which("docker") }}" compose -f .docker/compose.yaml up -d
    @echo "✓ MCP services started"
    @echo "  Add crawl4ai to Claude: claude mcp add --transport sse crawl4ai http://localhost:11235/mcp/sse"

[group('docker')]
mcp-down:
    @"{{ which("docker") }}" compose -f .docker/compose.yaml down

[group('docker')]
mcp-logs service="crawl4ai":
    @"{{ which("docker") }}" compose -f .docker/compose.yaml logs -f "{{ service }}"

[group('docker')]
mcp-status:
    @"{{ which("docker") }}" compose -f .docker/compose.yaml ps

# Install Claude Code components to ~/.claude/
[group('install')]
install target='all':
    @just _install-{{ target }}

[private]
_install-all: _install-claude

ls-tags:
    yq --output-format=json '.' "{{ justfile_directory() }}/components/skills/external.yaml" | jq '[ .manifest[] | add | .tags[] ] | unique'

[private]
_install-claude: _install-claude-commands _install-claude-rules _install-claude-skills _install-claude-hooks _install-claude-settings
    @echo "✓ Claude Code components installed to {{ CLAUDE_DIR }}"

[private]
_install-claude-settings:
    @echo "Installing settings..."
    @mkdir -p "{{ CLAUDE_DIR }}"
    @ln -sf "$(pwd)/settings/claude.json" "{{ CLAUDE_DIR }}/settings.json" && echo "  → ~/claude/settings.json" || true

[private]
_install-claude-commands:
    @echo "Installing commands..."
    @mkdir -p "{{ CLAUDE_DIR }}/commands"
    @for f in components/commands/*.md; do \
        [ -f "$f" ] && ln -sf "$(pwd)/$f" "{{ CLAUDE_DIR }}/commands/$(basename $f)" && echo "  → $(basename $f)"; \
    done || true

[private]
_install-claude-rules:
    @echo "Installing rules..."
    @mkdir -p "{{ CLAUDE_DIR }}/rules"
    @for f in components/rules/*.md; do \
        [ -f "$f" ] && ln -sf "$(pwd)/$f" "{{ CLAUDE_DIR }}/rules/$(basename $f)" && echo "  → $(basename $f)"; \
    done || true

[private]
_install-claude-skills:
    @echo "Installing skills..."
    @mkdir -p "{{ CLAUDE_DIR }}/skills"
    @for d in components/skills/*/; do \
        name=$(basename "$d"); \
        target="{{ CLAUDE_DIR }}/skills/$name"; \
        if [ -d "$d" ]; then \
            if [ -L "$target" ]; then \
                rm -f "$target"; \
            elif [ -d "$target" ]; then \
                rm -rf "$target"; \
            fi; \
            ln -sfn "$(pwd)/$d" "$target" && echo "  → $name/"; \
        fi; \
    done || true

[private]
_install-claude-hooks:
    @echo "Installing hooks..."
    @mkdir -p "{{ CLAUDE_DIR }}/hooks"
    @for f in components/hooks/*; do \
        [ -f "$f" ] && [ "$(basename $f)" != ".gitkeep" ] && ln -sf "$(pwd)/$f" "{{ CLAUDE_DIR }}/hooks/$(basename $f)" && echo "  → $(basename $f)"; \
    done || true

# Uninstall Claude Code components from ~/.claude/
[group('install')]
uninstall target='all':
    @just _uninstall-{{ target }}

[private]
_uninstall-all: _uninstall-claude

[private]
_uninstall-claude:
    @echo "Uninstalling Claude Code components..."
    @for f in components/commands/*.md; do \
        [ -f "$f" ] && rm -f "{{ CLAUDE_DIR }}/commands/$(basename $f)"; \
    done || true
    @for f in components/rules/*.md; do \
        [ -f "$f" ] && rm -f "{{ CLAUDE_DIR }}/rules/$(basename $f)"; \
    done || true
    @for d in components/skills/*/; do \
        [ -d "$d" ] && rm -f "{{ CLAUDE_DIR }}/skills/$(basename $d)"; \
    done || true
    @for f in components/hooks/*; do \
        [ -f "$f" ] && [ "$(basename $f)" != ".gitkeep" ] && rm -f "{{ CLAUDE_DIR }}/hooks/$(basename $f)"; \
    done || true
    @echo "✓ Claude Code components uninstalled"

# List installed Claude Code components
[group('install')]
list-claude:
    @echo "Commands:"
    @ls -la "{{ CLAUDE_DIR }}/commands/" 2>/dev/null | grep -E "\.md$" || echo "  (none)"
    @echo "\nRules:"
    @ls -la "{{ CLAUDE_DIR }}/rules/" 2>/dev/null | grep -E "\.md$" || echo "  (none)"
    @echo "\nSkills:"
    @ls -la "{{ CLAUDE_DIR }}/skills/" 2>/dev/null | grep -v "^total" | grep -v "^\." || echo "  (none)"
    @echo "\nHooks:"
    @ls -la "{{ CLAUDE_DIR }}/hooks/" 2>/dev/null | grep -v "^total" | grep -v "^\." || echo "  (none)"

# Anthropic skills registry

ANTHROPIC_SKILLS_REPO := "https://github.com/anthropics/skills.git"
ANTHROPIC_VERSION_FILE := "components/skills/.anthropic-version"

# Mapping: local-name -> upstream-path

ANTHROPIC_SKILL_MAP := "claude-skill-dev:skills/skill-creator"

# Fetch/update skills from Anthropic's skills repository
[group('upstream')]
sync-anthropic-skills:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Fetching latest from anthropics/skills..."

    # Get current commit SHA
    NEW_SHA=$(curl -sL https://api.github.com/repos/anthropics/skills/commits/main | jq -r '.sha[:7]')
    OLD_SHA=$(cat "{{ ANTHROPIC_VERSION_FILE }}" 2>/dev/null || echo "none")

    if [ "$NEW_SHA" = "$OLD_SHA" ]; then
        echo "✓ Already up to date ($OLD_SHA)"
        exit 0
    fi

    echo "Updating: $OLD_SHA → $NEW_SHA"

    # Clone with sparse checkout
    TMPDIR=$(mktemp -d)
    trap "rm -rf $TMPDIR" EXIT

    git clone --depth 1 --filter=blob:none --sparse "{{ ANTHROPIC_SKILLS_REPO }}" "$TMPDIR/skills" 2>/dev/null
    cd "$TMPDIR/skills"

    # Parse skill map and checkout each
    IFS=' ' read -ra MAPPINGS <<< "{{ ANTHROPIC_SKILL_MAP }}"
    PATHS=""
    for mapping in "${MAPPINGS[@]}"; do
        upstream_path="${mapping#*:}"
        PATHS="$PATHS $upstream_path"
    done
    git sparse-checkout set $PATHS

    cd - > /dev/null

    # Copy each skill to local name
    for mapping in "${MAPPINGS[@]}"; do
        local_name="${mapping%%:*}"
        upstream_path="${mapping#*:}"

        rm -rf "components/skills/$local_name"
        cp -r "$TMPDIR/skills/$upstream_path" "components/skills/$local_name"
        echo "  → $local_name (from $upstream_path)"
    done

    # Save version
    echo "$NEW_SHA" > "{{ ANTHROPIC_VERSION_FILE }}"
    echo "✓ Updated to $NEW_SHA"

# Check if Anthropic skills have updates available
[group('upstream')]
check-anthropic-updates:
    #!/usr/bin/env bash
    set -euo pipefail

    NEW_SHA=$(curl -sL https://api.github.com/repos/anthropics/skills/commits/main | jq -r '.sha[:7]')
    OLD_SHA=$(cat "{{ ANTHROPIC_VERSION_FILE }}" 2>/dev/null || echo "not installed")

    if [ "$OLD_SHA" = "not installed" ]; then
        echo "Anthropic skills not installed. Run: just sync-anthropic-skills"
    elif [ "$NEW_SHA" = "$OLD_SHA" ]; then
        echo "✓ Up to date ($OLD_SHA)"
    else
        echo "Update available: $OLD_SHA → $NEW_SHA"
        echo "Run: just sync-anthropic-skills"
    fi

# Show current Anthropic skills version
[group('upstream')]
anthropic-version:
    @cat "{{ ANTHROPIC_VERSION_FILE }}" 2>/dev/null || echo "not installed"

# External skills manifest

EXTERNAL_MANIFEST := justfile_directory() / "components/skills/external.yaml"
EXTERNAL_VERSION_DIR := justfile_directory() / "components/skills/.versions"

# List available external skills (optionally filter by category)
[group('external')]
list-external-skills category='':
    #!/usr/bin/env bash
    set -euo pipefail

    if [ -z "{{ category }}" ]; then
        echo "Categories:"
        yq -r '.manifest | keys[]' "{{ EXTERNAL_MANIFEST }}" | while read cat; do
            count=$(yq -r ".manifest[\"$cat\"] | length" "{{ EXTERNAL_MANIFEST }}")
            printf "  %-30s (%d skills)\n" "$cat" "$count"
        done
    else
        echo "Skills in {{ category }}:"
        yq -r ".manifest[\"{{ category }}\"][] | \"  \" + .name + \" - \" + (.notes // \"(no description)\")" "{{ EXTERNAL_MANIFEST }}" 2>/dev/null || echo "  Category not found"
    fi

# Search external skills by name or tag
[group('external')]
search-skills query:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Searching for '{{ query }}'..."
    yq -o=json '.manifest' "{{ EXTERNAL_MANIFEST }}" | \
        jq -r --arg q "{{ query }}" '
            to_entries[] |
            .key as $cat |
            .value[] |
            select(
                (.name | test($q; "i")) or
                (.tags[]? | test($q; "i")) or
                (.notes? // "" | test($q; "i"))
            ) |
            "[\($cat)] \(.name) - \(.notes // "(no description)")"
        '

# Import a skill from an external repository
[group('external')]
import-skill repo skill local_name='':
    #!/usr/bin/env bash
    set -euo pipefail

    SKILL_NAME="{{ if local_name != '' { local_name } else { skill } }}"
    TARGET_DIR="{{ justfile_directory() }}/components/skills/$SKILL_NAME"

    echo "Importing $SKILL_NAME from {{ repo }}..."

    # Create version tracking directory
    mkdir -p "{{ EXTERNAL_VERSION_DIR }}"

    # Get current commit SHA
    NEW_SHA=$(curl -sL "https://api.github.com/repos/{{ repo }}/commits/main" 2>/dev/null | jq -r '.sha[:7]' || \
              curl -sL "https://api.github.com/repos/{{ repo }}/commits/master" | jq -r '.sha[:7]')

    VERSION_FILE="{{ EXTERNAL_VERSION_DIR }}/$SKILL_NAME"
    OLD_SHA=$(cat "$VERSION_FILE" 2>/dev/null || echo "none")

    if [ "$NEW_SHA" = "$OLD_SHA" ] && [ -d "$TARGET_DIR" ]; then
        echo "✓ Already up to date ($OLD_SHA)"
        exit 0
    fi

    echo "Fetching: $OLD_SHA → $NEW_SHA"

    # Clone with sparse checkout
    TMPDIR=$(mktemp -d)
    trap "rm -rf $TMPDIR" EXIT

    git clone --depth 1 --filter=blob:none --sparse "https://github.com/{{ repo }}.git" "$TMPDIR/repo" 2>/dev/null
    cd "$TMPDIR/repo"

    # Try to find the skill path (check if git ls-tree returns non-empty output)
    SKILL_PATH=""
    for path in "{{ skill }}" "skills/{{ skill }}" ".claude/skills/{{ skill }}"; do
        if [ -n "$(git ls-tree --name-only HEAD "$path" 2>/dev/null)" ]; then
            SKILL_PATH="$path"
            break
        fi
    done

    if [ -z "$SKILL_PATH" ]; then
        echo "Error: Could not find skill '{{ skill }}' in repository"
        echo "Tried: {{ skill }}, skills/{{ skill }}, .claude/skills/{{ skill }}"
        exit 1
    fi

    git sparse-checkout set "$SKILL_PATH"
    cd - > /dev/null

    # Copy to local
    rm -rf "$TARGET_DIR"
    cp -r "$TMPDIR/repo/$SKILL_PATH" "$TARGET_DIR"

    # Save version
    echo "$NEW_SHA" > "$VERSION_FILE"
    echo "✓ Imported $SKILL_NAME from {{ repo }} ($NEW_SHA)"

# Import skill by name from manifest
[group('external')]
import-skill-by-name name local_name='':
    #!/usr/bin/env bash
    set -euo pipefail

    # Find skill in manifest
    SKILL_DATA=$(yq -o=json '.manifest' "{{ EXTERNAL_MANIFEST }}" | \
        jq -r --arg name "{{ name }}" '
            to_entries[] |
            .value[] |
            select(.name == $name) |
            "\(.repo)|\(.path // .name)"
        ' | head -1)

    if [ -z "$SKILL_DATA" ]; then
        echo "Error: Skill '{{ name }}' not found in manifest"
        echo "Try: just search-skills {{ name }}"
        exit 1
    fi

    REPO=$(echo "$SKILL_DATA" | cut -d'|' -f1)
    SKILL_PATH=$(echo "$SKILL_DATA" | cut -d'|' -f2)
    SKILL_NAME=$(basename "$SKILL_PATH")

    LOCAL_NAME="{{ if local_name != '' { local_name } else { '' } }}"
    if [ -z "$LOCAL_NAME" ]; then
        LOCAL_NAME="$SKILL_NAME"
    fi

    echo "Found: $REPO / $SKILL_PATH"
    just import-skill "$REPO" "$SKILL_PATH" "$LOCAL_NAME"

# List external registries
[group('external')]
list-registries:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Registries:"
    yq -r '.registries[] | "  [" + .type + "] " + .name + " - " + (.notes // "")' "{{ EXTERNAL_MANIFEST }}"

# Show version of imported external skill
[group('external')]
external-version skill:
    @cat "{{ EXTERNAL_VERSION_DIR }}/{{ skill }}" 2>/dev/null || echo "not imported"

# Check for updates to imported external skills
[group('external')]
check-external-updates:
    #!/usr/bin/env bash
    set -euo pipefail

    if [ ! -d "{{ EXTERNAL_VERSION_DIR }}" ]; then
        echo "No external skills imported yet."
        exit 0
    fi

    echo "Checking for updates..."
    for version_file in "{{ EXTERNAL_VERSION_DIR }}"/*; do
        [ -f "$version_file" ] || continue
        skill=$(basename "$version_file")
        old_sha=$(cat "$version_file")

        # Find repo in manifest
        repo=$(yq -o=json '.manifest' "{{ EXTERNAL_MANIFEST }}" | \
            jq -r --arg name "$skill" '
                to_entries[] |
                .value[] |
                select(.name == $name) |
                .repo
            ' | head -1)

        if [ -n "$repo" ]; then
            new_sha=$(curl -sL "https://api.github.com/repos/$repo/commits/main" 2>/dev/null | jq -r '.sha[:7]' || echo "$old_sha")
            if [ "$new_sha" != "$old_sha" ]; then
                echo "  ⬆ $skill: $old_sha → $new_sha"
            else
                echo "  ✓ $skill: up to date ($old_sha)"
            fi
        fi
    done

# Skill management

SKILL_TEMPLATE_DIR := justfile_directory() / "components/skills/.templates"

# Create new skill from template
[group('skills')]
create-skill name:
    #!/usr/bin/env bash
    set -euo pipefail

    SKILL_NAME="{{ name }}"
    TARGET_DIR="{{ justfile_directory() }}/components/skills/$SKILL_NAME"

    # Validate naming convention (allows lowercase letters and numbers like k8s)
    if ! echo "$SKILL_NAME" | grep -qE '^[a-z0-9]+-([a-z0-9]+-)?[a-z0-9]+-[a-z]+$'; then
        echo "Error: Invalid skill name format"
        echo "Expected: <category>-[<subcategory>-]<tool>-<focus>"
        echo "Focus must be one of: ops, dev, eng, nub, xec"
        echo "Examples: lang-rust-cargo-dev, cloud-aws-terraform-eng"
        exit 1
    fi

    # Extract components
    FOCUS=$(echo "$SKILL_NAME" | rev | cut -d'-' -f1 | rev)
    if ! echo "$FOCUS" | grep -qE '^(ops|dev|eng|nub|xec)$'; then
        echo "Error: Invalid focus '$FOCUS'"
        echo "Must be one of: ops, dev, eng, nub, xec"
        exit 1
    fi

    if [ -d "$TARGET_DIR" ]; then
        echo "Error: Skill '$SKILL_NAME' already exists"
        exit 1
    fi

    echo "Creating skill: $SKILL_NAME"

    # Create directory structure
    mkdir -p "$TARGET_DIR/references"

    # Copy template
    cp "{{ SKILL_TEMPLATE_DIR }}/SKILL.md" "$TARGET_DIR/SKILL.md"

    # Replace basic placeholders
    CREATED_DATE=$(date -u +"%Y-%m-%dT%H:%M")
    sed -i '' "s/\{\{SKILL_NAME\}\}/$SKILL_NAME/g" "$TARGET_DIR/SKILL.md"
    sed -i '' "s/\{\{CREATED_DATE\}\}/$CREATED_DATE/g" "$TARGET_DIR/SKILL.md"
    sed -i '' "s/\{\{UPDATED_DATE\}\}/$CREATED_DATE/g" "$TARGET_DIR/SKILL.md"

    echo "✓ Created skill at: $TARGET_DIR"
    echo "  Edit SKILL.md to complete the skill definition"

# Validate skill naming and structure
[group('skills')]
validate-skill path:
    #!/usr/bin/env bash
    set -euo pipefail

    SKILL_PATH="{{ path }}"
    SKILL_NAME=$(basename "$SKILL_PATH")
    ERRORS=0

    echo "Validating: $SKILL_NAME"

    # Check naming convention (allows lowercase letters and numbers like k8s)
    if ! echo "$SKILL_NAME" | grep -qE '^[a-z0-9]+-([a-z0-9]+-)?[a-z0-9]+-[a-z]+$'; then
        echo "  ✗ Name doesn't match pattern: <category>-[<subcategory>-]<tool>-<focus>"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✓ Name follows convention"
    fi

    # Check focus
    FOCUS=$(echo "$SKILL_NAME" | rev | cut -d'-' -f1 | rev)
    if ! echo "$FOCUS" | grep -qE '^(ops|dev|eng|nub|xec)$'; then
        echo "  ✗ Invalid focus: $FOCUS (expected: ops, dev, eng, nub, xec)"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✓ Valid focus: $FOCUS"
    fi

    # Check SKILL.md exists
    if [ ! -f "$SKILL_PATH/SKILL.md" ]; then
        echo "  ✗ Missing SKILL.md"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✓ SKILL.md exists"

        # Check for required frontmatter
        if ! head -1 "$SKILL_PATH/SKILL.md" | grep -q '^---$'; then
            echo "  ✗ Missing YAML frontmatter"
            ERRORS=$((ERRORS + 1))
        else
            echo "  ✓ Has YAML frontmatter"
        fi

        # Check for required sections
        for section in "Overview" "Quick Reference" "Troubleshooting"; do
            if grep -q "^## $section" "$SKILL_PATH/SKILL.md"; then
                echo "  ✓ Has $section section"
            else
                echo "  ⚠ Missing $section section (recommended)"
            fi
        done
    fi

    if [ $ERRORS -gt 0 ]; then
        echo "Validation failed with $ERRORS error(s)"
        exit 1
    else
        echo "✓ Validation passed"
    fi

# List local skills with their focus levels
[group('skills')]
list-skills:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Local skills:"
    for d in "{{ justfile_directory() }}"/components/skills/*/; do
        [ -d "$d" ] || continue
        name=$(basename "$d")
        # Skip hidden directories and templates
        [[ "$name" == .* ]] && continue

        # Extract focus if follows convention (allows lowercase letters and numbers like k8s)
        if echo "$name" | grep -qE '^[a-z0-9]+-([a-z0-9]+-)?[a-z0-9]+-[a-z]+$'; then
            focus=$(echo "$name" | rev | cut -d'-' -f1 | rev)
            printf "  %-40s [%s]\n" "$name" "$focus"
        else
            printf "  %-40s [non-standard]\n" "$name"
        fi
    done

# Validate all local skills
[group('skills')]
validate-all-skills:
    #!/usr/bin/env bash
    set -euo pipefail

    TOTAL=0
    PASSED=0
    FAILED=0

    for d in "{{ justfile_directory() }}"/components/skills/*/; do
        [ -d "$d" ] || continue
        name=$(basename "$d")
        [[ "$name" == .* ]] && continue

        TOTAL=$((TOTAL + 1))
        if just validate-skill "$d" >/dev/null 2>&1; then
            PASSED=$((PASSED + 1))
        else
            FAILED=$((FAILED + 1))
            echo "Failed: $name"
        fi
    done

    echo ""
    echo "Results: $PASSED/$TOTAL passed, $FAILED failed"

# Validate pillar coverage in a lang-*-dev skill
[group('skills')]
validate-pillars skill:
    #!/usr/bin/env bash
    set -euo pipefail

    SKILL_NAME="{{ skill }}"
    SKILL_FILE="{{ justfile_directory() }}/components/skills/$SKILL_NAME/SKILL.md"

    if [ ! -f "$SKILL_FILE" ]; then
        echo "❌ Skill not found: $SKILL_NAME"
        exit 1
    fi

    echo "Validating pillars for $SKILL_NAME..."
    echo ""

    PILLARS=0

    # Module System
    if grep -qiE "^## Module|import.*export|namespace|package structure" "$SKILL_FILE"; then
        echo "✓ Module System"
        PILLARS=$((PILLARS + 1))
    else
        echo "✗ Module System"
    fi

    # Error Handling
    if grep -qiE "^## Error|Result|Option|Exception" "$SKILL_FILE"; then
        echo "✓ Error Handling"
        PILLARS=$((PILLARS + 1))
    else
        echo "✗ Error Handling"
    fi

    # Concurrency
    if grep -qiE "^## Concur|async|thread|actor|channel|goroutine|process" "$SKILL_FILE"; then
        echo "✓ Concurrency"
        PILLARS=$((PILLARS + 1))
    else
        echo "✗ Concurrency"
    fi

    # Metaprogramming
    if grep -qiE "^## Meta|macro|decorator|reflection|annotation|code.*gen" "$SKILL_FILE"; then
        echo "✓ Metaprogramming"
        PILLARS=$((PILLARS + 1))
    else
        echo "✗ Metaprogramming"
    fi

    # Zero/Default Values
    if grep -qiE "^## Zero|^## Default|null|nil|None|Option|nullable" "$SKILL_FILE"; then
        echo "✓ Zero/Default Values"
        PILLARS=$((PILLARS + 1))
    else
        echo "✗ Zero/Default Values"
    fi

    # Serialization
    if grep -qiE "^## Serial|JSON|serde|codec|Encode|Decode|marshal" "$SKILL_FILE"; then
        echo "✓ Serialization"
        PILLARS=$((PILLARS + 1))
    else
        echo "✗ Serialization"
    fi

    # Build System
    if grep -qiE "^## Build|^## Dep|package.*manager|cargo|npm|pip|maven|gradle" "$SKILL_FILE"; then
        echo "✓ Build/Dependencies"
        PILLARS=$((PILLARS + 1))
    else
        echo "✗ Build/Dependencies"
    fi

    # Testing
    if grep -qiE "^## Test|unit test|property.*test|test.*framework" "$SKILL_FILE"; then
        echo "✓ Testing"
        PILLARS=$((PILLARS + 1))
    else
        echo "✗ Testing"
    fi

    echo ""
    echo "Coverage: $PILLARS/8 pillars"

    if [ $PILLARS -eq 8 ]; then
        echo "✅ Full coverage - ready for conversion skills"
    elif [ $PILLARS -ge 6 ]; then
        echo "⚠️  Acceptable coverage (6+/8) - minor gaps exist"
    else
        echo "❌ Below recommended coverage - address gaps before creating conversion skills"
        exit 1
    fi

# Validate all lang-*-dev skills for pillar coverage
[group('skills')]
validate-all-lang-skills:
    #!/usr/bin/env bash
    set -euo pipefail

    TOTAL=0
    FULL=0
    ACCEPTABLE=0
    GAPS=0

    echo "Validating all lang-*-dev skills..."
    echo "=================================="
    echo ""

    for d in "{{ justfile_directory() }}"/components/skills/lang-*-dev/; do
        [ -d "$d" ] || continue
        name=$(basename "$d")

        TOTAL=$((TOTAL + 1))
        echo "[$TOTAL] $name"
        echo "---"

        # Run validation and capture exit code
        if just validate-pillars "$name" 2>&1 | tail -n +2; then
            if grep -q "8/8" <<< "$(just validate-pillars "$name" 2>&1)"; then
                FULL=$((FULL + 1))
            else
                ACCEPTABLE=$((ACCEPTABLE + 1))
            fi
        else
            GAPS=$((GAPS + 1))
        fi

        echo ""
    done

    echo "=================================="
    echo "Summary: $TOTAL skills validated"
    echo "  ✅ Full coverage (8/8): $FULL"
    echo "  ⚠️  Acceptable (6-7/8): $ACCEPTABLE"
    echo "  ❌ Gaps (<6/8): $GAPS"

    if [ $GAPS -gt 0 ]; then
        echo ""
        echo "Run 'just validate-pillars <skill-name>' for details on specific gaps"
    fi

# Import external skill and normalize to naming convention
[group('skills')]
import-and-normalize repo skill target:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Importing and normalizing: {{ skill }} → {{ target }}"

    # Import the skill
    just import-skill "{{ repo }}" "{{ skill }}" "{{ target }}"

    # Validate the result
    just validate-skill "{{ justfile_directory() }}/components/skills/{{ target }}"

# Plugin management

# Install a plugin locally via symlinks
[group('plugins')]
install-plugin name:
    #!/usr/bin/env bash
    set -euo pipefail
    PLUGIN_DIR="context/plugins/{{ name }}"
    SOURCES="$PLUGIN_DIR/.claude-plugin/plugin.sources.json"
    if [ ! -f "$SOURCES" ]; then
      echo "Error: $SOURCES not found"; exit 1
    fi
    RECEIPT="{{ CLAUDE_DIR }}/plugins/{{ name }}.installed"
    mkdir -p "{{ CLAUDE_DIR }}/plugins"
    # Read each source mapping and create symlinks
    jq -r '.sources | to_entries[] | "\(.key)\t\(.value)"' "$SOURCES" | while IFS=$'\t' read -r local_path source_path; do
      target="{{ CLAUDE_DIR }}/$local_path"
      mkdir -p "$(dirname "$target")"
      ln -sfn "$(pwd)/$source_path" "$target"
      echo "  → $local_path"
    done
    # Write receipt
    jq -r '.sources | keys[]' "$SOURCES" > "$RECEIPT"
    echo "✓ Plugin {{ name }} installed"

# Build a plugin — copy source components into the plugin directory
[group('plugins')]
build-plugin name:
    #!/usr/bin/env bash
    set -euo pipefail
    PLUGIN_DIR="context/plugins/{{ name }}"
    SOURCES="$PLUGIN_DIR/.claude-plugin/plugin.sources.json"
    if [ ! -f "$SOURCES" ]; then
      echo "Error: $SOURCES not found"; exit 1
    fi
    # Copy each source component into the plugin directory
    jq -r '.sources | to_entries[] | "\(.key)\t\(.value)"' "$SOURCES" | while IFS=$'\t' read -r local_path source_path; do
      target="$PLUGIN_DIR/$local_path"
      mkdir -p "$(dirname "$target")"
      if [ -d "$source_path" ]; then
        rm -rf "$target"
        cp -r "$source_path" "$target"
      else
        cp "$source_path" "$target"
      fi
      echo "  → $local_path"
    done
    echo "✓ Plugin {{ name }} built"

# Uninstall a plugin
[group('plugins')]
uninstall-plugin name:
    #!/usr/bin/env bash
    set -euo pipefail
    RECEIPT="{{ CLAUDE_DIR }}/plugins/{{ name }}.installed"
    if [ ! -f "$RECEIPT" ]; then
      echo "Plugin {{ name }} is not installed"; exit 1
    fi
    while read -r local_path; do
      rm -f "{{ CLAUDE_DIR }}/$local_path"
      echo "  ✕ $local_path"
    done < "$RECEIPT"
    rm -f "$RECEIPT"
    echo "✓ Plugin {{ name }} uninstalled"

# Validate plugin source mappings
[group('plugins')]
check-plugin-sources name:
    #!/usr/bin/env bash
    set -euo pipefail
    PLUGIN_DIR="context/plugins/{{ name }}"
    SOURCES="$PLUGIN_DIR/.claude-plugin/plugin.sources.json"
    errors=0
    jq -r '.sources | to_entries[] | "\(.key)\t\(.value)"' "$SOURCES" | while IFS=$'\t' read -r local_path source_path; do
      if [ ! -e "$source_path" ]; then
        echo "MISSING: $source_path (for $local_path)"
        errors=$((errors + 1))
      fi
    done
    [ "$errors" -eq 0 ] && echo "✓ All sources exist" || exit 1

# List available and installed plugins
[group('plugins')]
list-plugins:
    #!/usr/bin/env bash
    echo "Available plugins:"
    for d in context/plugins/*/; do
      name=$(basename "$d")
      [ "$name" = "TODO.md" ] && continue
      installed=""
      [ -f "{{ CLAUDE_DIR }}/plugins/$name.installed" ] && installed=" [installed]"
      echo "  $name$installed"
    done

# Knowledge graph operations

# Initialize knowledge graph database
[group('kg')]
kg-init:
    @"{{which("uv")}}" run python scripts/init-db.py

# Ingest all context files into knowledge graph
[group('kg')]
kg-ingest:
    @"{{which("uv")}}" run python scripts/embed.py ingest --all

# Check for stale entities
[group('kg')]
kg-check:
    @"{{which("uv")}}" run python scripts/embed.py check

# Semantic search
[group('kg')]
kg-search query:
    @"{{which("uv")}}" run python scripts/embed.py search "{{ query }}"

# Find similar entities
[group('kg')]
kg-similar entity:
    @"{{which("uv")}}" run python scripts/embed.py similar "{{ entity }}"

# Compute similarity cache
[group('kg')]
kg-similarity:
    @"{{which("uv")}}" run python scripts/embed.py similarity

# Watch for changes and auto-embed
[group('kg')]
kg-watch:
    @"{{which("uv")}}" run python scripts/watch-embed.py

# Dump knowledge graph to SQL (essential tables only, ~40MB)
[group('kg')]
kg-dump:
    @"{{which("uv")}}" run python scripts/init-db.py --dump

# Load knowledge graph from SQL dump
[group('kg')]
kg-load:
    @"{{which("uv")}}" run python scripts/init-db.py --load

# Rebuild vector embeddings from existing chunks (after loading from dump)
[group('kg')]
kg-rebuild-embeddings:
    @"{{which("uv")}}" run python scripts/embed.py rebuild-embeddings
    @just kg-similarity

# Show knowledge graph statistics
[group('kg')]
kg-stats:
    @"{{which("uv")}}" run python scripts/kg-stats.py

# Force re-embed all entities
[group('kg')]
kg-rebuild:
    @echo "Rebuilding knowledge graph..."
    @rm -f .data/mcp/knowledge-graph.db
    @just kg-init
    @just kg-ingest
    @just kg-similarity
    @just kg-dump
    @echo "✓ Knowledge graph rebuilt"

# MCP registry cache management
[group('mcp')]
mcp-cache-load:
    @mkdir -p .data/mcp
    @sqlite3 .data/mcp/registry-cache.db < .data/mcp/registry-cache.sql
    @echo "✓ MCP registry cache loaded"

[group('mcp')]
mcp-cache-dump:
    @sqlite3 .data/mcp/registry-cache.db .dump > .data/mcp/registry-cache.sql
    @echo "✓ MCP registry cache dumped to .data/mcp/registry-cache.sql"

[group('mcp')]
mcp-cache-stats:
    @sqlite3 .data/mcp/registry-cache.db "SELECT count(*) || ' servers, ' || count(DISTINCT source_registry) || ' registries' FROM mcp_servers;"

[group('mcp')]
mcp-cache-search query:
    @sqlite3 -header -column .data/mcp/registry-cache.db "SELECT name, description, install_method, source_registry FROM mcp_servers_fts WHERE mcp_servers_fts MATCH '{{ query }}' LIMIT 20;"

opencode:
    echo "TODO: Setup repo for OpenCode integration, using .ai/* contents"

zed:
    echo "TODO: Setup repo for zed agent integration, using .ai/* contents"

vscode:
    echo "TODO: Setup repo for vscode integration, using .ai/* contents"

windsurf:
    echo "TODO: Setup repo for windsurf agent integration, using .ai/* contents"

cursor:
    echo "TODO: Setup repo for cursor agent integration, using .ai/* contents"

mcp-tools:
    echo "TODO: Setup mcp-tools for repo"

sitemap root:
    echo "TODO: Generate sitemap for repo"
    which("tree") -H '.' \
            -L 1 \
            --noreport \
            --houtro "" \
            --dirsfirst \
            --charset utf-8 \
            --ignore-case \
            --timefmt '%d-%b-%Y %H:%M' \
            -I "index.html" \
            -T 'AI Contexts' \
            -s -D \
            -P "*.zip|*.gz" \
            -o index.html
