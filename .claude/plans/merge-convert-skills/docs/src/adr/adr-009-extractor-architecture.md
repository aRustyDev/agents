# ADR-009: Extractor Architecture

**Status**: Proposed
**Date**: 2026-02-05
**Context**: Convert Skills IR Validation & Tooling (Phase 5)
**Deciders**: Project maintainers

## Context

Phase 5 of the merge-convert-skills project requires building a Python extraction/synthesis pipeline to validate the IR schema design. The extractor must transform source code into the 5-layer IR while:

1. **Maintaining language consistency**: The same extraction approach should generalize across 9+ language families
2. **Capturing semantic information**: Beyond syntax, we need types, bindings, and cross-file references
3. **Supporting incremental development**: Python first, then Rust, TypeScript, and others in subsequent phases
4. **Achieving L3 semantic equivalence**: Extracted IR must round-trip with same I/O behavior

The challenge: Different languages have vastly different tooling ecosystems. Python has `ast`, `jedi`, and `pyright`. Rust has `syn` and `rust-analyzer`. TypeScript has the compiler API. A unified approach risks either lowest-common-denominator functionality or per-language maintenance burden.

### Requirements

| Requirement | Priority | Notes |
|-------------|----------|-------|
| Parse any valid source code | Must | Error-tolerant for partial files |
| Extract type information | Must | Explicit annotations + inferred types |
| Resolve cross-file references | Should | Imports, module resolution |
| Track source locations | Could | For debugging (Layer 0 optional) |
| Consistent API across languages | Must | Phase 6+ languages follow same pattern |
| Reasonable performance | Should | < 5 seconds for 1000 LOC |

## Decision

**Adopt a hybrid architecture**: Use tree-sitter for universal syntax parsing, combined with language-specific semantic enrichment tools.

### Architecture Overview

```
Source Code
    │
    ▼
┌─────────────────────────────┐
│     Tree-sitter Parser      │  Universal across 165+ languages
│  (tree-sitter-language-pack)│
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│      AST Normalizer         │  Convert CST to Generic AST
│   (per-language adapters)   │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│    Semantic Enrichment      │  Language-specific type analysis
│  (jedi/pyright for Python)  │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│      IR Generator           │  Produce 5-layer IR
│   (shared implementation)   │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│    Schema Validator         │  Validate against ir-v1.json
└─────────────────────────────┘
```

### Why Hybrid?

The hybrid approach balances several concerns:

1. **Tree-sitter provides**:
   - Consistent API across 165+ languages via a single interface
   - Fast, incremental, error-tolerant parsing
   - Community-maintained grammars with active development
   - Byte-level source spans for precise location tracking

2. **Semantic enrichment provides**:
   - Type information (explicit and inferred)
   - Name resolution and scope analysis
   - Cross-file reference resolution
   - Language-specific semantic understanding

3. **Generic AST layer enables**:
   - Reusable IR generation logic
   - Consistent handling of common constructs (functions, classes, loops)
   - Simplified testing via language-agnostic fixtures
   - Clear separation of parsing vs. semantic analysis

## Alternatives Considered

### Option A: Custom Parsers per Language

**Description**: Write custom parsers using each language's native AST library (Python `ast`, Rust `syn`, TypeScript compiler API).

**Pros**:
- Maximum fidelity to language semantics
- Direct access to compiler's type information
- No external dependencies beyond language runtime

**Cons**:
- Massive implementation effort (9+ separate parsers)
- Inconsistent APIs across languages
- Some languages lack good AST libraries
- Maintenance burden multiplied per language

**Verdict**: Rejected. The 5/5 implementation complexity outweighs the semantic richness benefit (4/5).

### Option B: Tree-sitter Only

**Description**: Use tree-sitter exclusively, extracting all information from the Concrete Syntax Tree.

**Pros**:
- Single parsing infrastructure
- Fast and memory-efficient
- Works on partial/invalid code
- Excellent cross-language consistency

**Cons**:
- No semantic information (types, bindings)
- Cannot resolve imports or cross-file references
- Limited to syntax; misses language-specific meaning
- Would require extensive custom type inference

**Verdict**: Rejected. The semantic richness (2/5) is insufficient for our L3 equivalence target.

### Option C: Compiler APIs Only

**Description**: Use each language's compiler API (pyright, rust-analyzer, tsserver) for both parsing and semantics.

**Pros**:
- Highest semantic fidelity (5/5)
- Access to full type system, including inference
- Same analysis as production tools
- Excellent error messages

**Cons**:
- Each compiler has completely different API
- Cross-language consistency nearly impossible (1/5)
- Heavy dependencies (full compiler toolchains)
- Some languages have no suitable compiler API

**Verdict**: Rejected. The lack of cross-language consistency (1/5) makes this unsuitable for a unified pipeline.

### Option D: Language Server Protocol (LSP) Only

**Description**: Use LSP servers (pylsp, rust-analyzer, tsserver) via a unified protocol for all languages.

**Pros**:
- Standardized protocol across languages
- Good semantic information (4/5)
- Well-maintained production tooling
- Handles cross-file references

**Cons**:
- LSP designed for IDE features, not batch extraction
- Request/response model inefficient for bulk analysis
- Incomplete coverage (not all languages have good LSP servers)
- Setup complexity varies by language

**Verdict**: Rejected. LSP is better suited for interactive use than batch extraction.

### Option E: Hybrid Tree-sitter + Semantic Enrichment (Chosen)

**Description**: Tree-sitter for universal parsing, language-specific tools for semantic enrichment.

**Pros**:
- Balanced complexity (3/5) vs. richness (4/5)
- Consistent parsing API across all languages
- Semantic enrichment can use best available tool per language
- Graceful degradation (can work without semantic enrichment)
- Good cross-language consistency (4/5)

**Cons**:
- Two-phase architecture adds complexity
- Semantic enrichment tools vary in quality
- Must map between tree-sitter CST and semantic tool AST

**Verdict**: Accepted. Best balance of implementation effort and semantic fidelity.

### Comparison Matrix

| Approach | Impl. Complexity | Semantic Richness | Cross-Lang Consistency | Maintenance |
|----------|------------------|-------------------|------------------------|-------------|
| Custom Parsers | 5/5 | 4/5 | 5/5 | 5/5 |
| Tree-sitter Only | 2/5 | 2/5 | 4/5 | 2/5 |
| Compiler APIs | 4/5 | 5/5 | 1/5 | 4/5 |
| LSP Only | 3/5 | 4/5 | 3/5 | 2/5 |
| **Hybrid** | **3/5** | **4/5** | **4/5** | **3/5** |

(Lower scores are better for Complexity and Maintenance)

## Consequences

### Positive

1. **Consistent parsing**: Tree-sitter provides identical parsing API for Python, Rust, TypeScript, and all future languages
2. **Best-of-breed semantics**: Each language can use its best semantic analysis tool
3. **Graceful degradation**: Extraction works without semantic enrichment (types become `Any`)
4. **Incremental adoption**: Can add semantic enrichment for new languages over time
5. **Testability**: Generic AST layer enables language-agnostic test fixtures
6. **Performance**: Tree-sitter is fast; semantic enrichment can be optional

### Negative

1. **Two-phase complexity**: Must maintain mapping between tree-sitter CST and semantic tool AST
2. **Node alignment**: Aligning tree-sitter nodes with semantic tool nodes requires heuristics
3. **Dependency management**: Each language adds new dependencies (jedi, pyright, etc.)
4. **Semantic tool variability**: Quality of type information varies by language and tool

### Neutral

1. **Migration path**: Can upgrade semantic enrichment tools independently of parsing
2. **Future languages**: Adding a new language requires tree-sitter grammar + semantic tool adapter

## Implementation Details

### Generic AST Specification

The Generic AST (GAST) normalizes tree-sitter's Concrete Syntax Trees into a language-agnostic structure.

#### GAST Node Types

| Category | Node Types | Notes |
|----------|------------|-------|
| Structural | `module`, `import`, `export`, `definition` | Maps to Layer 4 |
| Type | `type_def`, `type_param`, `type_ref`, `type_alias` | Maps to Layer 3 |
| Control Flow | `function`, `class`, `method`, `block`, `branch`, `loop`, `match`, `try` | Maps to Layer 2 |
| Data Flow | `binding`, `assignment`, `parameter`, `return` | Maps to Layer 1 |
| Expression | `call`, `operator`, `literal`, `identifier`, `lambda` | Maps to Layer 0 (optional) |

#### GAST Structure

```python
@dataclass
class GASTNode:
    """Base node in the Generic AST."""
    kind: str                    # Node type from table above
    span: SourceSpan            # Location in source
    children: list[GASTNode]    # Child nodes
    attributes: dict[str, Any]  # Kind-specific attributes

@dataclass
class SourceSpan:
    """Source location (byte offsets, 0-indexed)."""
    file: str
    start_byte: int
    end_byte: int
    start_point: tuple[int, int]  # (row, column)
    end_point: tuple[int, int]

@dataclass
class TypedGASTNode(GASTNode):
    """GAST node with semantic enrichment."""
    resolved_type: TypeRef | None
    binding_ref: str | None       # For identifiers
    definition_ref: str | None    # For references
```

### Per-Language Strategy

#### Python (Phase 5 - MVP)

| Component | Tool | Rationale |
|-----------|------|-----------|
| Parsing | `tree-sitter-python` via `tree-sitter-language-pack` | Fast, error-tolerant |
| Semantic (default) | `jedi` | Simple setup, single-file analysis |
| Semantic (advanced) | `pyright` | Cross-file types, py.typed packages |
| Formatting | `black` | Clean, deterministic output |
| Formatting (preserve) | `libcst` | Comment preservation |

#### Rust (Phase 6)

| Component | Tool | Rationale |
|-----------|------|-----------|
| Parsing | `tree-sitter-rust` | Standard grammar |
| Semantic | `rust-analyzer` (via LSP or `ra_ap_*` crates) | Best-in-class Rust analysis |
| Formatting | `rustfmt` | Standard Rust formatter |

#### TypeScript (Phase 7)

| Component | Tool | Rationale |
|-----------|------|-----------|
| Parsing | `tree-sitter-typescript` | Handles both TS and TSX |
| Semantic | TypeScript Compiler API | First-party type information |
| Formatting | `prettier` | Standard TS formatter |

#### Go (Phase 8)

| Component | Tool | Rationale |
|-----------|------|-----------|
| Parsing | `tree-sitter-go` | Standard grammar |
| Semantic | `gopls` (via LSP) | Official Go language server |
| Formatting | `gofmt` | Built-in, canonical |

#### Future Languages

| Language | Parsing | Semantic | Notes |
|----------|---------|----------|-------|
| Scala | `tree-sitter-scala` | Metals LSP | HKT, implicits |
| Roc | Custom (small language) | Roc compiler | Algebraic effects |
| Elixir | `tree-sitter-elixir` | ElixirLS | BEAM semantics |
| Haskell | `tree-sitter-haskell` | HLS | Type inference |

### Pyright vs Jedi Decision Criteria

For Python semantic enrichment, the choice between `jedi` and `pyright` depends on project characteristics:

| Criterion | Use Pyright | Use Jedi |
|-----------|-------------|----------|
| Project has `py.typed` marker | Yes | |
| Type stubs available (`.pyi` files) | Yes | |
| Need cross-file type resolution | Yes | |
| Typed codebase (PEP 484+) | Yes | |
| Simple single-file extraction | | Yes |
| No LSP/node setup available | | Yes |
| Performance critical (many files) | | Yes |
| Dynamic/untyped codebase | | Yes |

**Default Strategy**: Start with `jedi` for simplicity and speed.

**Upgrade Trigger**: Switch to `pyright` when any of these are true:
- `py.typed` marker present
- `.pyi` stub files in project
- Cross-file type errors in extraction
- User explicitly requests `--type-inference=pyright`

**Fallback Chain**:

```
pyright (if configured)
    │
    ├── Success: Use pyright types
    │
    └── Failure/Unavailable
            │
            ▼
        jedi
            │
            ├── Success: Use jedi completions/types
            │
            └── Failure
                    │
                    ▼
                typing.Any + E003 annotation
```

### Formatting Strategy

| Use Case | Tool | When to Use |
|----------|------|-------------|
| Clean conversion output | `black` | Default for all synthesis |
| Refactoring (preserve comments) | `libcst` | `--preserve-formatting` flag |
| Round-trip testing | `black` | Normalize both sides before comparison |
| CI/validation | `black --check` | Verify output is well-formed |

**Black Configuration** (in `pyproject.toml`):

```toml
[tool.black]
line-length = 88
target-version = ['py310']
```

**LibCST Use Cases**:
- Preserving existing comments during refactoring
- Maintaining author's formatting preferences
- Source-to-source transformations

### Cross-File Analysis

Python imports create cross-file dependencies. The extractor handles these in three modes:

| Mode | Behavior | Use Case |
|------|----------|----------|
| `single` | Extract one file; imports as references | Quick testing |
| `package` | Extract all files in package | Library conversion |
| `project` | Full dependency graph resolution | Complete migration |

**Module Resolution Rules**:

| Import Type | Resolution | IR Representation |
|-------------|------------|-------------------|
| `import foo` (local) | Find `foo.py` or `foo/__init__.py` | Full extraction |
| `import foo` (stdlib) | Mark as `stdlib:foo` | Reference only |
| `import foo` (third-party) | Mark as `external:foo` | Reference + stubs if available |
| `from . import bar` | Resolve relative to package | Full extraction |
| `from typing import X` | Mark as `stdlib:typing` | Type reference only |

**Unresolved Imports**:
1. Log warning with `E004` error code
2. Create placeholder: `external:<module>.<name>`
3. Continue extraction
4. Include in IR metadata for downstream handling

### Error Handling

| Code | Category | Description | Recovery |
|------|----------|-------------|----------|
| `E001` | Parse Error | Syntax error in source | Skip file, report location |
| `E002` | Unsupported Syntax | Valid but unsupported | Mark as gap, continue |
| `E003` | Type Inference Failed | Cannot determine type | Use `Any`, annotate |
| `E004` | Cross-File Reference | Unresolved import | Record as dependency |
| `E005` | Metaprogramming | Dynamic code generation | Mark as impossible gap |

### Implementation Checklist

Phase 5 (Python MVP):

- [ ] `TreeSitterAdapter` with Python grammar loading
- [ ] `PythonNormalizer` to convert CST to GAST
- [ ] `JediEnricher` for default type analysis
- [ ] `PyrightEnricher` for advanced type analysis (optional)
- [ ] `IRGenerator` to produce 5-layer IR from typed GAST
- [ ] `SchemaValidator` to validate against `ir-v1.json`
- [ ] `GapDetector` to identify semantic gaps
- [ ] CLI tool: `just ir-extract file.py`
- [ ] 15+ test fixtures with expected IR output

## References

- **Phase 5 Plan**: `.claude/plans/merge-convert-skills/phase/5-validation-tooling.md`
- **IR Schema Overview**: `.claude/plans/merge-convert-skills/docs/src/ir-schema/overview.md`
- **Layer Specifications**: `.claude/plans/merge-convert-skills/docs/src/ir-schema/layer-{0-4}.md`
- **ADR-008 (Content Hashing)**: `docs/src/adr/008-ir-content-hashing.md`
- **Tree-sitter**: https://tree-sitter.github.io/tree-sitter/
- **tree-sitter-language-pack**: https://pypi.org/project/tree-sitter-language-pack/
- **Jedi**: https://jedi.readthedocs.io/
- **Pyright**: https://microsoft.github.io/pyright/
- **Black**: https://black.readthedocs.io/
- **LibCST**: https://libcst.readthedocs.io/

---

*Generated: 2026-02-05*
