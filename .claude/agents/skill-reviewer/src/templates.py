"""Handlebars template support for generating content."""

import json
import re
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Try to import pybars3, fall back to chevron (mustache)
try:
    import pybars

    HAS_PYBARS = True
except ImportError:
    HAS_PYBARS = False

try:
    import chevron

    HAS_CHEVRON = True
except ImportError:
    HAS_CHEVRON = False


class TemplateEngine:
    """Template engine supporting Handlebars (.hbs) templates."""

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self._cache: dict[str, Any] = {}

        if not HAS_PYBARS and not HAS_CHEVRON:
            raise ImportError(
                "Template engine requires either 'pybars3' or 'chevron'. "
                "Install with: pip install pybars3 chevron"
            )

    def _load_template(self, name: str) -> str:
        """Load template content from file."""
        if name in self._cache:
            return self._cache[name]

        # Try .hbs first, then .mustache
        for ext in [".hbs", ".mustache", ".md.hbs"]:
            path = self.templates_dir / f"{name}{ext}"
            if path.exists():
                content = path.read_text()
                self._cache[name] = content
                return content

        raise FileNotFoundError(f"Template not found: {name}")

    def _prepare_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Prepare context for rendering, converting dataclasses etc."""
        result = {}
        for key, value in context.items():
            if is_dataclass(value) and not isinstance(value, type):
                result[key] = asdict(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, Path):
                result[key] = str(value)
            else:
                result[key] = value
        return result

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a template with the given context.

        Args:
            template_name: Name of template (without extension)
            context: Variables to pass to template

        Returns:
            Rendered string
        """
        template_str = self._load_template(template_name)
        ctx = self._prepare_context(context)

        if HAS_PYBARS:
            return self._render_pybars(template_str, ctx)
        else:
            return self._render_chevron(template_str, ctx)

    def _render_pybars(self, template_str: str, context: dict) -> str:
        """Render using pybars3 (full Handlebars support)."""
        compiler = pybars.Compiler()
        template = compiler.compile(template_str)

        # Register helpers
        helpers = {
            "json": lambda this, obj: json.dumps(obj, indent=2),
            "uppercase": lambda this, s: str(s).upper(),
            "lowercase": lambda this, s: str(s).lower(),
            "date": lambda this, fmt="%Y-%m-%d": datetime.now().strftime(fmt),
            "eq": lambda this, a, b: a == b,
            "gt": lambda this, a, b: a > b,
            "lt": lambda this, a, b: a < b,
        }

        return template(context, helpers=helpers)

    def _render_chevron(self, template_str: str, context: dict) -> str:
        """Render using chevron (Mustache, limited features)."""
        return chevron.render(template_str, context)

    def render_string(self, template_str: str, context: dict[str, Any]) -> str:
        """Render a template string directly.

        Args:
            template_str: Template content
            context: Variables to pass to template

        Returns:
            Rendered string
        """
        ctx = self._prepare_context(context)

        if HAS_PYBARS:
            return self._render_pybars(template_str, ctx)
        else:
            return self._render_chevron(template_str, ctx)


# Template definitions for common outputs
TEMPLATES = {
    "commit_message": """{{type}}({{scope}}): {{description}}

{{#if added}}
### Added
{{#each added}}
- {{this}}
{{/each}}
{{/if}}

{{#if changed}}
### Changed
{{#each changed}}
- {{this}}
{{/each}}
{{/if}}

{{#if fixed}}
### Fixed
{{#each fixed}}
- {{this}}
{{/each}}
{{/if}}

{{#if closes}}
Closes #{{closes}}
{{/if}}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
""",
    "pr_body": """## Summary

{{#each summary}}
- {{this}}
{{/each}}

## Changes

{{#if added}}
### Added
{{#each added}}
- {{this}}
{{/each}}
{{/if}}

{{#if changed}}
### Changed
{{#each changed}}
- {{this}}
{{/each}}
{{/if}}

## Linked Issues

{{#each issues}}
Closes #{{this}}
{{/each}}

## Validation

- [ ] Token budget: SKILL.md < 500 lines
- [ ] Pillar coverage improved
- [ ] Cross-references valid
- [ ] Examples are idiomatic

## Test Plan

- [ ] Run `/validate-lang-conversion-skill`
- [ ] Verify examples compile/run
- [ ] Check cross-reference links

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
""",
    "issue_comment_start": """## Skill Review Started

**Session**: `{{session_id}}`
**Started**: {{started_at}}

### Skill
`{{skill_path}}`

### Estimated Tokens
- Input: ~{{estimated_input}} tokens
- Output: ~{{estimated_output}} tokens
- Estimated cost: ~${{estimated_cost}}

### Status
🔄 Review in progress...
""",
    "issue_comment_complete": """## Skill Review Complete

**Session**: `{{session_id}}`
**Duration**: {{duration}}

### Results
- Pillars before: {{pillars_before}}/8
- Pillars after: {{pillars_after}}/8
- Lines added: {{lines_added}}
- Files modified: {{files_modified}}

### Pull Request
{{pr_url}}

### Token Usage
- Input: {{actual_input}} tokens
- Output: {{actual_output}} tokens
- Actual cost: ${{actual_cost}}
""",
    "validation_summary": """## Validation Results

**Skill**: `{{skill_path}}`
**Type**: {{skill_type}}

### Token Budget
- Lines: {{token_count}}
- Status: {{token_budget_status}}

### Pillar Coverage ({{pillars_present}}/{{pillars_total}})

| Pillar | Present |
|--------|---------|
{{#each pillars}}
| {{name}} | {{#if present}}✅{{else}}❌{{/if}} |
{{/each}}

{{#if missing_pillars}}
### Missing Pillars
{{#each missing_pillars}}
- {{this}}
{{/each}}
{{/if}}

{{#if recommendations}}
### Recommendations
{{#each recommendations}}
- {{this}}
{{/each}}
{{/if}}
""",
}


def get_template_engine(templates_dir: Path | None = None) -> TemplateEngine:
    """Get a template engine instance.

    Args:
        templates_dir: Path to templates directory (defaults to ../templates)

    Returns:
        TemplateEngine instance
    """
    if templates_dir is None:
        templates_dir = Path(__file__).parent.parent / "templates"

    return TemplateEngine(templates_dir)


def render_inline(template_name: str, context: dict[str, Any]) -> str:
    """Render a built-in template.

    Args:
        template_name: Name of template in TEMPLATES dict
        context: Variables to pass to template

    Returns:
        Rendered string
    """
    if template_name not in TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}")

    template_str = TEMPLATES[template_name]

    # Simple mustache-like rendering for inline templates
    # This avoids requiring pybars for basic usage
    result = template_str

    # Handle simple variables: {{var}}
    for key, value in context.items():
        if isinstance(value, (str, int, float)):
            result = result.replace(f"{{{{{key}}}}}", str(value))

    # Handle conditionals: {{#if var}}...{{/if}}
    for key, value in context.items():
        pattern = rf"\{{\{{#if {key}\}}\}}(.*?)\{{\{{/if\}}\}}"
        if value:
            result = re.sub(pattern, r"\1", result, flags=re.DOTALL)
        else:
            result = re.sub(pattern, "", result, flags=re.DOTALL)

    # Handle each: {{#each var}}...{{/each}}
    for key, value in context.items():
        if isinstance(value, list):
            pattern = rf"\{{\{{#each {key}\}}\}}(.*?)\{{\{{/each\}}\}}"
            match = re.search(pattern, result, flags=re.DOTALL)
            if match:
                item_template = match.group(1)
                items_rendered = []
                for item in value:
                    if isinstance(item, dict):
                        item_result = item_template
                        for k, v in item.items():
                            item_result = item_result.replace(f"{{{{{k}}}}}", str(v))
                        items_rendered.append(item_result)
                    else:
                        items_rendered.append(item_template.replace("{{this}}", str(item)))
                result = re.sub(pattern, "".join(items_rendered), result, flags=re.DOTALL)

    return result.strip()
