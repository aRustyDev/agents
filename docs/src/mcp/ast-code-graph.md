# AST Code Graph Retrieval

This document describes how Abstract Syntax Tree (AST) code graphs are retrieved and gathered for MCP server analysis.

## Overview

The assessment schema includes a `codebase_ast` field for storing AST analysis results:

```sql
-- Field in mcp_server_assessments
codebase_ast TEXT  -- JSON structure containing AST summary
```

AST analysis provides structural understanding of MCP server codebases, enabling:
- Tool function identification
- Handler pattern recognition
- Dependency mapping
- Complexity assessment

## AST Extraction Methods

### Method 1: Tree-sitter (Preferred)

[Tree-sitter](https://tree-sitter.github.io/tree-sitter/) provides fast, incremental parsing for 100+ languages.

**Supported languages for MCP servers:**

| Language | Grammar | Common in MCP |
|----------|---------|---------------|
| Python | `tree-sitter-python` | High |
| TypeScript | `tree-sitter-typescript` | High |
| JavaScript | `tree-sitter-javascript` | Medium |
| Rust | `tree-sitter-rust` | Medium |
| Go | `tree-sitter-go` | Low |

**Extraction workflow:**

```python
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

# Initialize parser
parser = Parser(Language(tspython.language()))

# Parse source file
with open("server.py", "rb") as f:
    tree = parser.parse(f.read())

# Extract function definitions
def extract_functions(node, functions=[]):
    if node.type == "function_definition":
        name = node.child_by_field_name("name")
        functions.append({
            "name": name.text.decode(),
            "start_line": node.start_point[0],
            "end_line": node.end_point[0]
        })
    for child in node.children:
        extract_functions(child, functions)
    return functions
```

### Method 2: Language Server Protocol (LSP)

LSP servers provide symbol information without custom parsing.

**Workflow:**

1. Start language server for the codebase
2. Request document symbols via `textDocument/documentSymbol`
3. Extract function, class, and method definitions

**Example using pylsp:**

```bash
# Start Python language server
pylsp --tcp --port 2087

# Query symbols (via LSP client)
{
  "method": "textDocument/documentSymbol",
  "params": {
    "textDocument": {"uri": "file:///path/to/server.py"}
  }
}
```

### Method 3: Built-in AST Modules

For Python specifically, use the `ast` module:

```python
import ast

with open("server.py") as f:
    tree = ast.parse(f.read())

# Extract all function and class definitions
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        print(f"Function: {node.name} at line {node.lineno}")
    elif isinstance(node, ast.ClassDef):
        print(f"Class: {node.name} at line {node.lineno}")
```

### Method 4: MCP Code Graph Servers

Several MCP servers specialize in code graph extraction:

| Server | Method | Languages |
|--------|--------|-----------|
| `mcp-server-tree-sitter` | Tree-sitter | 12+ languages |
| `codegraph-rust` | Tree-sitter + PDG | 14 languages |
| `code-graph-rag-mcp` | Tree-sitter | TypeScript, Python |
| `CodeGraphContext` | Tree-sitter + Neo4j | 13 languages |

**Using mcp-server-tree-sitter:**

```json
{
  "tool": "parse_file",
  "arguments": {
    "file_path": "/path/to/server.py",
    "language": "python"
  }
}
```

## AST Data Structure

The `codebase_ast` field stores a JSON summary:

```json
{
  "language": "python",
  "parser": "tree-sitter",
  "analyzed_at": "2026-02-03T12:00:00Z",
  "files_analyzed": 5,
  "summary": {
    "total_functions": 23,
    "total_classes": 4,
    "total_lines": 1250,
    "avg_function_length": 18
  },
  "symbols": [
    {
      "type": "class",
      "name": "MCPServer",
      "file": "src/server.py",
      "line": 15,
      "methods": ["handle_request", "start", "stop"]
    },
    {
      "type": "function",
      "name": "handle_tool_call",
      "file": "src/handlers.py",
      "line": 42,
      "decorators": ["@tool"]
    }
  ],
  "mcp_tools": [
    {
      "name": "search_code",
      "handler": "handle_search_code",
      "file": "src/tools.py",
      "line": 78
    }
  ]
}
```

## MCP-Specific Extraction

### Identifying MCP Tools

Look for tool registration patterns:

**Python (FastMCP):**
```python
@mcp.tool()
def search_code(query: str) -> list[dict]:
    """Search code using semantic similarity."""
    ...
```

**TypeScript (@modelcontextprotocol/sdk):**
```typescript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "search_code") {
    ...
  }
});
```

### Identifying MCP Resources

**Python:**
```python
@mcp.resource("file://{path}")
def get_file(path: str) -> str:
    ...
```

**TypeScript:**
```typescript
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    { uri: "file://config", name: "Configuration" }
  ]
}));
```

## Extraction Workflow

### Step 1: Clone Repository

```bash
# Shallow clone for analysis
git clone --depth 1 https://github.com/<owner>/<repo> /tmp/mcp-analysis/<slug>
```

### Step 2: Identify Entry Points

```bash
# Find main server files
find /tmp/mcp-analysis/<slug> -name "*.py" -exec grep -l "mcp\|MCP" {} \;
find /tmp/mcp-analysis/<slug> -name "*.ts" -exec grep -l "modelcontextprotocol" {} \;
```

### Step 3: Parse with Tree-sitter

```python
from tree_sitter_languages import get_parser

parser = get_parser("python")
for file in server_files:
    tree = parser.parse(open(file, "rb").read())
    # Extract symbols...
```

### Step 4: Extract MCP Patterns

```python
# Find @mcp.tool() decorated functions
def find_mcp_tools(tree, source_bytes):
    tools = []
    for node in tree_walk(tree.root_node):
        if node.type == "decorated_definition":
            decorators = [n for n in node.children if n.type == "decorator"]
            for dec in decorators:
                if "tool" in dec.text.decode():
                    func = node.child_by_field_name("definition")
                    tools.append(func.child_by_field_name("name").text.decode())
    return tools
```

### Step 5: Store Results

```sql
UPDATE mcp_server_assessments SET
  codebase_ast = '<json_summary>'
WHERE server_id = <entity_id> AND domain = '<need>';
```

## Querying AST Data

Find servers with specific patterns:

```sql
SELECT e.name, e.slug,
       json_extract(a.codebase_ast, '$.summary.total_functions') as functions,
       json_extract(a.codebase_ast, '$.mcp_tools') as tools
FROM mcp_server_assessments a
JOIN entities e ON a.server_id = e.id
WHERE a.codebase_ast IS NOT NULL
  AND json_array_length(json_extract(a.codebase_ast, '$.mcp_tools')) > 5;
```

## Current Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Schema field | Implemented | `codebase_ast TEXT` |
| Tree-sitter parsing | Available | Via MCP servers |
| LSP extraction | Planned | Requires server setup |
| Tool pattern detection | Partial | Framework-specific |
| Automated extraction | Planned | Manual only |
| Storage format | Defined | JSON schema above |

## Tools for AST Analysis

| Tool | Purpose | Install |
|------|---------|---------|
| `tree-sitter-cli` | Parse any language | `npm i -g tree-sitter-cli` |
| `ast-grep` | Structural search | `brew install ast-grep` |
| `semgrep` | Pattern matching | `pip install semgrep` |
| `ctags` | Symbol extraction | `brew install universal-ctags` |

## Future Improvements

- [ ] Automated AST extraction on server discovery
- [ ] Call graph generation for dependency analysis
- [ ] Complexity metrics (cyclomatic, cognitive)
- [ ] Security pattern detection (input validation, auth checks)
- [ ] Compare AST across server versions
- [ ] Build searchable symbol index
