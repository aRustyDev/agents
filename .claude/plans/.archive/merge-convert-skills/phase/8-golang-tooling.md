# Phase 8: Golang Extractor & Synthesizer

Implement Go language support for the IR extraction/synthesis pipeline.

## Goal

Build Go extractor and synthesizer, focusing on Go's simplicity, explicit error handling, and goroutine-based concurrency model.

## Dependencies

- **Phase 5**: Python MVP
- **Phase 6**: Rust tooling (systems language patterns)
- **Phase 7**: TypeScript tooling (cross-language matrix)

### Go-Specific IR Requirements

From `docs/src/ir-schema/layer-2.md` (Control Flow IR):
- Goroutines and channels
- Multiple return values (including error)
- Defer statements

From `docs/src/ir-schema/cross-cutting.md`:
- Annotation kinds: `CC-003` (CSP channels), `EF-001` (Exceptions→Result)

## Deliverables

- [ ] Go extractor using `go/ast` and `go/types`
- [ ] Go synthesizer with idiomatic patterns
- [ ] Cross-language tests
- [ ] 25+ Go-specific test cases
- [ ] Validation report

---

## Go-Specific Challenges

### Error Handling Pattern

```go
// Go's explicit error handling
func ReadFile(path string) ([]byte, error) {
    f, err := os.Open(path)
    if err != nil {
        return nil, fmt.Errorf("open: %w", err)
    }
    defer f.Close()
    return io.ReadAll(f)
}
```

**IR Representation**:

```yaml
function:
  name: ReadFile
  parameters:
    - name: path
      type: string
  returns:
    - type: "[]byte"
    - type: error  # Multiple returns
  effects:
    - kind: EF-001
      value: { pattern: error_return }
  control_flow:
    - type: error_check
      condition: "err != nil"
      on_error: return_early
```

### Concurrency Model

```go
func process(items []int) []int {
    results := make(chan int, len(items))

    for _, item := range items {
        go func(x int) {
            results <- x * 2
        }(item)
    }

    output := make([]int, 0, len(items))
    for range items {
        output = append(output, <-results)
    }
    return output
}
```

**IR Representation**:

```yaml
function:
  name: process
  concurrency:
    model: channels  # CC-003
    constructs:
      - type: channel
        name: results
        direction: bidirectional
      - type: goroutine
        captures: [x]
```

---

## Tasks

### 8.1 Go Extractor Implementation

**Implementation Approach**:
- **Primary**: Go standard library (`go/ast`, `go/types`, `go/parser`)
- Go's tooling is excellent - use native APIs

```go
// tools/ir-extract/golang/extract.go
package main

import (
    "go/ast"
    "go/parser"
    "go/token"
    "go/types"
)

func ExtractIR(source string) (*IR, error) {
    fset := token.NewFileSet()
    file, err := parser.ParseFile(fset, "source.go", source, parser.ParseComments)
    if err != nil {
        return nil, err
    }

    // Type check for semantic information
    conf := types.Config{Importer: importer.Default()}
    info := &types.Info{
        Types: make(map[ast.Expr]types.TypeAndValue),
        Defs:  make(map[*ast.Ident]types.Object),
        Uses:  make(map[*ast.Ident]types.Object),
    }
    _, err = conf.Check("source", fset, []*ast.File{file}, info)
    // ...
}
```

**Deliverable**: `tools/ir-extract/golang/`

---

### 8.2 Go Synthesizer Implementation

**Key Patterns**:
- Error handling with `if err != nil`
- Defer for cleanup
- Multiple return values
- Channel operations

**Deliverable**: `tools/ir-synthesize/golang/`

---

### 8.3-8.6 Testing, Cross-Language, Report, Review

Follow standard structure from previous phases.

---

## Success Criteria

- [ ] Go extractor working (20+ fixtures)
- [ ] Go synthesizer producing `go build` valid code
- [ ] Error handling patterns preserved
- [ ] Channel/goroutine patterns captured
- [ ] 25+ test cases passing

## Effort Estimate

5-7 days (Go tooling is excellent)

## Output Files

| File | Description |
|------|-------------|
| `tools/ir-extract/golang/` | Go extractor |
| `tools/ir-synthesize/golang/` | Go synthesizer |
| `tests/fixtures/golang/` | Test fixtures |
| `analysis/phase8-validation-report.md` | Results |
