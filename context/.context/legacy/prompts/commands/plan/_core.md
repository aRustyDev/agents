---
module: PlanCore  
scope: context
triggers: []
conflicts: []
dependencies:
  - utilities.md
  - template-manager.md
  - scripts/session_management.sh
  - templates/error-codes.yaml
  - templates/session-structure.yaml
priority: high
---

# Plan Core - Shared Utilities

## Purpose
Core planning logic and shared utilities used by all plan subcommands.

## Overview
This module provides common functionality for session management, error handling, and utilities shared across all planning phases.

## Session Management

### Session Directory Structure
```
.plan/
├── sessions/
│   ├── 20240109_143022/
│   │   ├── requirements.md
│   │   ├── task-breakdown.yaml
│   │   ├── dependencies.md
│   │   ├── mvp-scope.md
│   │   ├── issues.json
│   │   ├── milestones.json
│   │   ├── projects.json
│   │   ├── labels.json
│   │   ├── execute_plan.sh
│   │   └── summary.md
│   └── [other sessions]/
├── backups/
│   └── [timestamp]/
└── templates/
    └── [custom templates]/
```

### Session Functions

Core session management functionality.

**Implementation**: See `scripts/session_management.sh`

Key functions:
- `create_session()` - Create new planning session
- `load_session()` - Load existing session
- `list_sessions()` - List all available sessions
- `get_repo_info()` - Get repository metadata

## Common Variables

Standard variables used across all plan modules:

```bash
# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
```

Repository information is retrieved via `get_repo_info()` function.

## Error Handling

Standardized error handling across all plan modules.

**Error Codes**: See `templates/error-codes.yaml`

Key functions:
- `handle_error()` - Display error and exit with code
- Error codes for common failures (1-7)
- Helpful error messages with remediation steps

### Validation Functions

- `check_prerequisites()` - Validates gh CLI, git repo, auth, and access
- Automatically called by all plan subcommands
- Exits with appropriate error code on failure

## Templates System

Template management functionality for saving and loading plan templates.

**Implementation**: See `template-manager.md`

Key functions:
- `load_template()` - Load saved template
- `save_template()` - Save current plan as template
- `list_templates()` - Show available templates

## Import/Export Functions

Import and export functionality for plan data.

**Implementation**: See `template-manager.md`

Supported formats:
- Markdown import/export
- JSON import/export
- Template-based import

## Utility Functions

Common utility functions used across plan modules.

**Implementation**: See `utilities.md`

Available utilities:
- `format_duration()` - Human-readable time formatting
- `show_progress()` - Progress bar display
- JSON helpers
- Date/time helpers
- String manipulation

## Integration Points

This core module is used by:
- `discovery.md` - Session creation and management
- `analysis.md` - Data storage and retrieval
- `design.md` - Template handling
- `implementation.md` - Progress tracking
- `cleanup.md` - Session listing and removal

All plan modules should import this for:
1. Session management
2. Error handling
3. Common utilities
4. Repository information
5. Template operations