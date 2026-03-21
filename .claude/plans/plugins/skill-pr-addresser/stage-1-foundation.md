# Stage 1: Foundation

> Scaffold the Cement CLI application with basic structure.

## Objective

Create the basic Cement application skeleton that can be invoked but doesn't do anything yet.

## Dependencies

- Stage 0 complete (skill-agents-common exists)

## Steps

### 1.1 Create directory structure

```bash
mkdir -p .claude/agents/skill-pr-addresser/{src,config,data,subagents,templates,tests}
mkdir -p .claude/agents/skill-pr-addresser/src/{controllers,ext,tui}
```

- [ ] Create all directories
- [ ] Create `__init__.py` files

### 1.2 Create pyproject.toml

```toml
[project]
name = "skill-pr-addresser"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "cement>=3.0.10",
    "colorlog>=6.8.0",
    "textual>=0.47.0",
    "opentelemetry-api>=1.22.0",
    "opentelemetry-sdk>=1.22.0",
    "opentelemetry-exporter-otlp-proto-grpc>=1.22.0",
    "chevron>=0.14.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.2.0",
]

[projectcli]
skill-pr-addresser = "skill_pr_addresser.main:main"
```

- [ ] Create `pyproject.toml`
- [ ] Verify dependencies install: `pip install -e .`

### 1.3 Create main.py

```python
#!/usr/bin/env python3
"""CLI entry point for skill-pr-addresser."""

from .src.app import SkillPRAddresser

def main():
    with SkillPRAddresser() as app:
        app.run()

if __name__ == "__main__":
    main()
```

- [ ] Create `main.py`
- [ ] Create `__main__.py` for `python -m` invocation

### 1.4 Create src/app.py

```python
"""Cement application class."""

from cement import App, Controller, ex
from cement.ext.ext_colorlog import ColorLogHandler

class Base(Controller):
    class Meta:
        label = 'base'
        description = 'Address PR review feedback for skills'

    @ex(help='Address review feedback on a PR')
    def address(self):
        self.app.log.info("Address command (not implemented)")

    @ex(help='Check addressing status')
    def status(self):
        self.app.log.info("Status command (not implemented)")

class SkillPRAddresser(App):
    class Meta:
        label = 'skill-pr-addresser'
        handlers = [Base, ColorLogHandler]
        extensions = ['colorlog']
        config_files = ['config/skill-pr-addresser.conf']
```

- [ ] Create `src/app.py`
- [ ] Verify `python -m skill_pr_addresser --help` works

### 1.5 Create src/exceptions.py

```python
"""Custom exceptions for skill-pr-addresser."""

class AddresserError(Exception):
    """Base exception."""
    exit_code = 1

class PRNotFoundError(AddresserError):
    """PR does not exist."""
    pass

class PRClosedError(AddresserError):
    """PR is already merged or closed."""
    exit_code = 0

class NoFeedbackError(AddresserError):
    """No feedback to address."""
    exit_code = 0

class WorktreeError(AddresserError):
    """Worktree operation failed."""
    pass

class ConflictError(AddresserError):
    """Git conflict detected."""
    pass

class IterationLimitError(AddresserError):
    """Max iterations reached."""
    pass
```

- [ ] Create `src/exceptions.py`

### 1.6 Create config file

```ini
# config/skill-pr-addresser.conf
[skill-pr-addresser]
repo_owner = aRustyDev
repo_name = ai
max_iterations = 3
rate_limit_delay = 1.0

[otel]
enabled = false
endpoint = http://localhost:4317
service_name = skill-pr-addresser
version = 0.1.0
```

- [ ] Create `config/skill-pr-addresser.conf`

### 1.7 Create justfile

```just
# Justfile for skill-pr-addresser

set shell := ["bash", "-c"]

# Default recipe
default:
    @just --list

# Address review feedback on a PR
address-skill-reviews pr_number *FLAGS:
    python -m skill_pr_addresser address {{pr_number}} {{FLAGS}}

# Check addressing status
address-status pr_number:
    python -m skill_pr_addresser status {{pr_number}}

# Run tests
test *FLAGS:
    pytest tests/ {{FLAGS}}

# Install dependencies
install:
    pip install -e ".[dev]"
```

- [ ] Create `justfile`
- [ ] Verify `just address-skill-reviews 795 --help` works

### 1.8 Create agent entry point

```markdown
<!-- .claude/agents/skill-pr-addresser.md -->
---
description: Address PR review feedback for skills, continuing development until approved
tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Skill PR Addresser

...
```

- [ ] Create `.claude/agents/skill-pr-addresser.md`

## Checklist Gate

Before proceeding to Stage 2:

- [ ] `pip install -e .` succeeds
- [ ] `python -m skill_pr_addresser --help` shows help
- [ ] `python -m skill_pr_addresser address --help` shows address help
- [ ] `just address-skill-reviews 795` runs (prints "not implemented")
- [ ] Config file loads correctly
- [ ] Exceptions module imports without errors

## Files Created

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package definition |
| `main.py` | CLI entry point |
| `__main__.py` | Module invocation |
| `src/__init__.py` | Package marker |
| `src/app.py` | Cement App class |
| `src/exceptions.py` | Custom exceptions |
| `config/skill-pr-addresser.conf` | Default config |
| `justfile` | Task runner recipes |
| `.claude/agents/skill-pr-addresser.md` | Agent entry point |

## Estimated Effort

- Scaffolding: ~1 hour
- Testing CLI: ~30 minutes
- **Total: ~1.5 hours**
