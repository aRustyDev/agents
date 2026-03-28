# SwiftUI Development Plugin

Comprehensive SwiftUI development support for UI testing, integration testing, data-driven apps, and interactive development practices.

## Components

| Type | Count | Status |
|------|-------|--------|
| Skills | 5 | P0 implemented |
| Commands | 4 | P0 implemented |
| Agents | 1 | P0 implemented |
| Styles | 2 | Planned |
| Hooks | 0 | Planned |
| MCP Servers | 0 | Research needed |
| LSP Servers | 1 | Configured |

## Skills

### P0 (Implemented)

- **swiftui-architecture** - MVVM, @Observable, navigation, dependency injection
- **swiftui-data-flow** - @State, @Binding, @Observable, environment values
- **swiftui-testing** - XCTest, XCUITest, ViewInspector, snapshot testing
- **duckdb-swift** - DuckDB integration, SQL over CSV/Parquet/SQLite
- **swift-charts** - Swift Charts API, marks, interactivity, performance

### Inherited (via plugin.sources.json)

- **lang-swift-dev** - Core Swift patterns
- **lang-swift-library-dev** - Swift Package Manager
- **swift-expert** - Swift architecture agent

## Commands

- `/create-swiftui-view` - Generate SwiftUI view with previews
- `/create-viewmodel` - Generate @Observable ViewModel
- `/create-xctest` - Generate XCTest unit tests
- `/create-swift-package` - Initialize Swift Package

## Data Layer Support

This plugin supports multiple data backends:

- **SQLite** - Via GRDB.swift or SwiftData
- **DuckDB** - Analytical SQL engine (CSV, Parquet, SQLite queries)
- **Kuzu** - Graph database (P2)
- **Dolt** - Version-controlled database (P2)

## Setup

1. Install dependencies:

   ```bash
   just install-plugin swiftui-dev
   ```

2. Configure LSP (sourcekit-lsp via Xcode toolchain)

## Roadmap

See `.plans/plugins/swiftui-dev/roadmap.md` for full development plan.

### P1 (Enhancement)

- grdb-swift, swiftdata-patterns, grape-graphs skills
- /create-xcuitest, /swiftui-preview-data commands
- swift-format-check, swiftlint-check hooks

### P2 (Nice to Have)

- kuzu-swift, dolt-swift, instruments-profiling skills
- MCP server research (xcode-mcp, duckdb-mcp, kuzu-mcp)
