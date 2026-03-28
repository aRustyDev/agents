# Plugin Roadmap: swiftui-dev

## Summary

| Action | Count |
|--------|-------|
| Reuse  | 3     |
| Extend | 9     |
| Create | 31    |
| Research | 3   |

---

## P0 - MVP (Must Have)

### Reuse (add to plugin.sources.json)

| Component | Type | Source Path |
|-----------|------|-------------|
| swift-concurrency | skill | content/skills/lang-swift-dev/SKILL.md (embedded) |
| swift-package-manager | skill | content/skills/lang-swift-library-dev/SKILL.md |
| sourcekit-lsp | lsp | system (Xcode toolchain) |

### Extend

| Component | Type | Base | Gap | Effort |
|-----------|------|------|-----|--------|
| swiftui-architecture | skill | lang-swift-dev | MVVM/TCA patterns, @Observable, navigation | medium |
| swiftui-data-flow | skill | lang-swift-dev | @Observable macro, @Bindable, environment | small |
| swiftui-testing | skill | lang-swift-dev | ViewInspector, snapshot testing, preview testing | medium |
| xctest-patterns | skill | lang-swift-dev | Async testing, dependency injection, mocking | small |
| swiftui-architect | agent | swift-expert | SwiftUI-specific architecture decisions | small |

### Create

| Component | Type | Description | Dependencies |
|-----------|------|-------------|--------------|
| duckdb-swift | skill | DuckDB integration, SQL queries, CSV/Parquet reading | — |
| swift-charts | skill | Swift Charts API, PointMark, LineMark, Chart3D | — |
| /create-swiftui-view | command | Generate SwiftUI view with previews | swiftui-architecture |
| /create-viewmodel | command | Generate @Observable ViewModel | swiftui-data-flow |
| /create-xctest | command | Generate XCTest unit test file | xctest-patterns |
| /create-swift-package | command | Initialize Swift Package structure | swift-package-manager |
| swift-code | style | Swift code output formatting | — |
| swiftui-view | style | SwiftUI view code with previews | swift-code |

---

## P1 - Enhancement (Should Have)

### Extend

| Component | Type | Base | Gap | Effort |
|-----------|------|------|-----|--------|
| swiftui-components | skill | lang-swift-dev | Lists, forms, navigation, sheets, popovers | medium |
| xcuitest-patterns | skill | lang-swift-dev | Page object pattern, accessibility IDs | small |
| swiftui-code-reviewer | agent | swift-expert | SwiftUI best practices, performance, a11y | medium |
| swift-debugger | agent | swift-expert | SwiftUI view debugging, data flow issues | small |

### Create

| Component | Type | Description | Dependencies |
|-----------|------|-------------|--------------|
| grdb-swift | skill | GRDB.swift patterns, @Query, migrations | duckdb-swift |
| swiftdata-patterns | skill | SwiftData models, queries, relationships | — |
| grape-graphs | skill | Force-directed graph visualization | swift-charts |
| sketch-to-swiftui | skill | Translating Sketch designs to SwiftUI | swiftui-components |
| xcode-previews | skill | Preview providers, sample data, modifiers | swiftui-view |
| accelerate-numerics | skill | vDSP, BLAS, LAPACK for numerical computing | — |
| /create-xcuitest | command | Generate XCUITest with page objects | xcuitest-patterns |
| /swiftui-preview-data | command | Generate preview sample data | xcode-previews |
| /migrate-to-observable | command | Migrate ObservableObject to @Observable | swiftui-data-flow |
| swift-test-generator | agent | Generate comprehensive test suites | xctest-patterns, xcuitest-patterns |
| sketch-translator | agent | Translate Sketch to SwiftUI plans | sketch-to-swiftui |
| xctest-output | style | Test file output formatting | swift-code |
| swift-package-manifest | style | Package.swift formatting | swift-code |
| swift-format-check | hook | Run swift-format on Swift files | — |
| swiftlint-check | hook | Run SwiftLint on Swift files | — |

---

## P2 - Nice to Have

### Create

| Component | Type | Description | Dependencies |
|-----------|------|-------------|--------------|
| kuzu-swift | skill | Kuzu graph database, Cypher queries | grape-graphs |
| dolt-swift | skill | Dolt version-controlled database | grdb-swift |
| instruments-profiling | skill | Time Profiler, Allocations, Metal debugging | — |
| /analyze-view-performance | command | Analyze SwiftUI view performance | instruments-profiling |
| swift-build-check | hook | Verify Swift package builds | swift-package-manager |

### Research (MCP Servers)

| Component | Type | Description | Action |
|-----------|------|-------------|--------|
| xcode-mcp | mcp | Xcode project operations | Find or create |
| duckdb-mcp | mcp | DuckDB query execution | Find or create |
| kuzu-mcp | mcp | Kuzu graph queries | Find or create |

---

## Dependency Graph

```text
                    ┌─────────────────┐
                    │ lang-swift-dev  │ (reuse)
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│swiftui-architect│ │ swiftui-data-   │ │ xctest-patterns │
│     (extend)    │ │   flow (extend) │ │    (extend)     │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│/create-swiftui- │ │ /create-        │ │  /create-xctest │
│   view (create) │ │viewmodel(create)│ │    (create)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘

         ┌─────────────────┐
         │   duckdb-swift  │ (create - P0)
         └────────┬────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌─────────┐ ┌───────────┐ ┌───────────┐
│grdb-swift│ │swift-charts│ │grape-graphs│
│  (P1)    │ │   (P0)    │ │   (P1)    │
└────┬────┘ └───────────┘ └─────┬─────┘
     │                          │
     ▼                          ▼
┌─────────┐                ┌───────────┐
│dolt-swift│               │kuzu-swift │
│  (P2)    │               │   (P2)    │
└─────────┘                └───────────┘
```

---

## Effort Estimates

| Priority | Skills | Commands | Agents | Styles | Hooks | Total |
|----------|--------|----------|--------|--------|-------|-------|
| P0       | 7      | 4        | 1      | 2      | 0     | 14    |
| P1       | 6      | 3        | 2      | 2      | 2     | 15    |
| P2       | 3      | 1        | 0      | 0      | 1     | 5     |
| **Total**| 16     | 8        | 3      | 4      | 3     | 34    |

---

## Implementation Notes

### Data Layer Strategy

Based on research report recommendations:

1. **DuckDB** as central SQL engine for CSV/Parquet/SQLite queries
2. **GRDB.swift** for reactive SQLite with @Query integration
3. **SwiftData** for modern persistence with CloudKit sync
4. **Kuzu** for graph relationships (P2)
5. **Dolt** for version-controlled data (P2)

### Testing Strategy

1. **XCTest** for unit tests with dependency injection
2. **XCUITest** for UI automation with page object pattern
3. **ViewInspector** for SwiftUI view unit testing
4. **Snapshot testing** for visual regression

### Visualization Strategy

1. **Swift Charts** for 2D plots (PointMark, LineMark, BarMark)
2. **Chart3D** for 3D scatter plots (macOS 26+)
3. **Grape** for force-directed graph visualization
4. **Metal/Core Graphics** fallback for large datasets

### Architecture Patterns

1. **@Observable** macro for state management (modern approach)
2. **MVVM** with dependency injection
3. **TCA** reference for complex state management
4. **Navigation stack** patterns for deep linking
