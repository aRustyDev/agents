# Plugin Brainstorm: swiftui-dev

## Domain & Purpose

**Domain**: SwiftUI / macOS / iOS Native Development
**Purpose**: Comprehensive SwiftUI development support focused on UI testing, integration testing, and interactive development practices with emphasis on data-driven applications.

## Use Cases

1. **Data Analytics App Development** - Building Marimo-like reactive notebooks with DuckDB, graph visualization, and Swift Charts
2. **General SwiftUI Development** - Broad support for SwiftUI app architecture, components, and patterns
3. **Portfolio Project Quality** - Ensuring production-ready polish, proper error handling, and architecture documentation

## Components

### Skills

| Name | Purpose | Priority |
|------|---------|----------|
| swiftui-architecture | SwiftUI app architecture patterns (MVVM, TCA, Clean Architecture) | must |
| swiftui-components | Common UI component patterns (lists, forms, navigation, sheets) | must |
| swiftui-data-flow | @Observable, @State, @Binding, environment values, data passing | must |
| swiftui-testing | XCTest + XCUITest patterns, ViewInspector, test organization | must |
| swift-concurrency | async/await, actors, structured concurrency, Task groups | must |
| duckdb-swift | DuckDB integration, SQL queries, CSV/Parquet/SQLite bridging | must |
| grdb-swift | GRDB.swift patterns, @Query, migrations, observation | should |
| swiftdata-patterns | SwiftData models, queries, relationships, CloudKit sync | should |
| kuzu-swift | Kuzu graph database integration, Cypher queries | should |
| dolt-swift | Dolt version-controlled database patterns | nice |
| swift-charts | Swift Charts API, PointMark, LineMark, BarMark, Chart3D | must |
| grape-graphs | Force-directed graph visualization with Grape library | should |
| accelerate-numerics | vDSP, BLAS, LAPACK for numerical computing | should |
| sketch-to-swiftui | Translating Sketch designs to SwiftUI views | should |
| xctest-patterns | Unit testing patterns, mocking, dependency injection | must |
| xcuitest-patterns | UI testing, accessibility identifiers, test plans | must |
| swift-package-manager | Package.swift, dependencies, targets, resources | must |
| xcode-previews | Preview providers, sample data, preview modifiers | should |
| instruments-profiling | Time Profiler, Allocations, Leaks, Metal System Trace | should |

### Commands

| Name | Purpose | Priority |
|------|---------|----------|
| /create-swiftui-view | Generate a new SwiftUI view with proper structure and previews | must |
| /create-viewmodel | Generate an @Observable ViewModel with dependency injection | must |
| /create-xctest | Generate XCTest unit test file with proper setup/teardown | must |
| /create-xcuitest | Generate XCUITest UI test with page object pattern | should |
| /create-swift-package | Initialize a new Swift Package with proper structure | must |
| /swiftui-preview-data | Generate preview sample data for SwiftUI previews | should |
| /analyze-view-performance | Analyze SwiftUI view for performance issues | nice |
| /migrate-to-observable | Migrate ObservableObject to @Observable macro | should |

### Agents

| Name | Purpose | Priority |
|------|---------|----------|
| swiftui-architect | Design SwiftUI app architecture, module boundaries, data flow | must |
| swiftui-code-reviewer | Review SwiftUI code for best practices, performance, accessibility | must |
| swift-test-generator | Generate comprehensive test suites for Swift code | should |
| sketch-translator | Translate Sketch designs into SwiftUI implementation plans | should |
| swift-debugger | Debug SwiftUI issues, view rendering problems, data flow bugs | should |

### Output Styles

| Name | Purpose | Priority |
|------|---------|----------|
| swift-code | Swift code formatting with proper conventions | must |
| swiftui-view | SwiftUI view code with preview providers | must |
| xctest-output | Test file output with assertions and setup | must |
| swift-package-manifest | Package.swift manifest formatting | should |

### Hooks

| Name | Purpose | Priority |
|------|---------|----------|
| swift-format-check | Run swift-format on Swift files | should |
| swiftlint-check | Run SwiftLint on Swift files | should |
| swift-build-check | Verify Swift package builds | should |

### MCP Servers

| Name | Purpose | Priority |
|------|---------|----------|
| xcode-mcp | Xcode project operations, build, test, run | must |
| swift-lsp | SourceKit-LSP integration for code intelligence | must |
| duckdb-mcp | DuckDB query execution and schema inspection | should |
| kuzu-mcp | Kuzu graph database queries and visualization | nice |

### LSP Servers

| Name | Purpose | Priority |
|------|---------|----------|
| sourcekit-lsp | Apple's official Swift/Xcode LSP | must |

## Summary

| Category | Must | Should | Nice | Total |
|----------|------|--------|------|-------|
| Skills   | 10   | 7      | 1    | 18    |
| Commands | 4    | 3      | 1    | 8     |
| Agents   | 2    | 3      | 0    | 5     |
| Styles   | 3    | 1      | 0    | 4     |
| Hooks    | 0    | 3      | 0    | 3     |
| MCP      | 2    | 1      | 1    | 4     |
| LSP      | 1    | 0      | 0    | 1     |
| **Total**| 22   | 18     | 3    | 43    |
