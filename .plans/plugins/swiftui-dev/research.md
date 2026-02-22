# Plugin Research: swiftui-dev

## Existing Plugins

| Plugin | Domain | Coverage | Recommendation |
|--------|--------|----------|----------------|
| ios-dev | iOS Development | 30% | Extend - has skeleton infrastructure |

## Component Research

### Skills

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| swiftui-architecture | Embedded in lang-swift-dev | context/skills/lang-swift-dev/SKILL.md | 40% | extend |
| swiftui-components | Embedded in lang-swift-dev | context/skills/lang-swift-dev/SKILL.md | 50% | extend |
| swiftui-data-flow | Embedded in lang-swift-dev | context/skills/lang-swift-dev/SKILL.md | 60% | extend |
| swiftui-testing | Embedded in lang-swift-dev | context/skills/lang-swift-dev/SKILL.md | 40% | extend |
| swift-concurrency | Embedded in lang-swift-dev | context/skills/lang-swift-dev/SKILL.md | 70% | reuse |
| duckdb-swift | None | — | 0% | create |
| grdb-swift | None | — | 0% | create |
| swiftdata-patterns | Partially in lang-swift-dev | context/skills/lang-swift-dev/SKILL.md | 20% | create |
| kuzu-swift | None | — | 0% | create |
| dolt-swift | None | — | 0% | create |
| swift-charts | None | — | 0% | create |
| grape-graphs | None | — | 0% | create |
| accelerate-numerics | None | — | 0% | create |
| sketch-to-swiftui | None | — | 0% | create |
| xctest-patterns | Embedded in lang-swift-dev | context/skills/lang-swift-dev/SKILL.md | 50% | extend |
| xcuitest-patterns | Embedded in lang-swift-dev | context/skills/lang-swift-dev/SKILL.md | 30% | extend |
| swift-package-manager | lang-swift-library-dev | context/skills/lang-swift-library-dev/SKILL.md | 80% | reuse |
| xcode-previews | None | — | 0% | create |
| instruments-profiling | None | — | 0% | create |

### Commands

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| /create-swiftui-view | None | — | 0% | create |
| /create-viewmodel | None | — | 0% | create |
| /create-xctest | None | — | 0% | create |
| /create-xcuitest | None | — | 0% | create |
| /create-swift-package | None | — | 0% | create |
| /swiftui-preview-data | None | — | 0% | create |
| /analyze-view-performance | None | — | 0% | create |
| /migrate-to-observable | None | — | 0% | create |

### Agents

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| swiftui-architect | swift-expert | context/agents/swift-expert.md | 60% | extend |
| swiftui-code-reviewer | swift-expert | context/agents/swift-expert.md | 50% | extend |
| swift-test-generator | None | — | 0% | create |
| sketch-translator | None | — | 0% | create |
| swift-debugger | swift-expert | context/agents/swift-expert.md | 40% | extend |

### Output Styles

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| swift-code | None | — | 0% | create |
| swiftui-view | None | — | 0% | create |
| xctest-output | None | — | 0% | create |
| swift-package-manifest | None | — | 0% | create |

### Hooks

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| swift-format-check | None | — | 0% | create |
| swiftlint-check | None | — | 0% | create |
| swift-build-check | None | — | 0% | create |

### MCP Servers

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| xcode-mcp | None | — | 0% | research |
| swift-lsp | sourcekit-lsp | system | 90% | configure |
| duckdb-mcp | None | — | 0% | research |
| kuzu-mcp | None | — | 0% | research |

### LSP Servers

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| sourcekit-lsp | System installed | Xcode toolchain | 100% | configure |

## Summary

- **Reuse**: 3 components (swift-concurrency, swift-package-manager, sourcekit-lsp)
- **Extend**: 9 components (existing skills/agents with gaps)
- **Create**: 31 components (new skills, commands, styles, hooks)
- **Research**: 3 components (MCP servers to find/evaluate)

## Key Findings

### Strengths

1. Strong Swift foundation in `lang-swift-dev` skill (SwiftUI basics covered)
2. `swift-expert` agent available for architecture decisions
3. `lang-swift-library-dev` covers SPM workflows
4. `ios-dev` plugin skeleton exists for extension

### Gaps

1. No dedicated SwiftUI-specific skills (architecture, components, data flow)
2. No data layer skills (DuckDB, GRDB, Kuzu, Dolt)
3. No visualization skills (Swift Charts, Grape)
4. No SwiftUI testing commands
5. No output styles for Swift code
6. No hooks for Swift tooling (swift-format, SwiftLint)

### Legacy Assets to Activate

- SwiftUI guidelines in `.wip/` directory (migrate to production)
- iOS plugin skeleton (extend for swiftui-dev)
