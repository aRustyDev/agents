## MCP GAPS

- **Mustache/template rendering** — no MCP server found. The justfile pipeline handles this already.
- **JSON Schema Draft 2020-12 validation** — the mcpmarket one claims it but has 0 stars. AJV in the justfile pipeline is the reliable path. json-validate (draft-07) is a
reasonable fallback for quick checks.
- **Ruby syntax/linting** — no MCP server. brew mcp-server partially covers this via brew audit/brew style.
