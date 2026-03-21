# Plugin Component Audit

Audit of existing plugins and potential shared components from `context/`.

## Summary

| Plugin | Status | Potential Shared Components |
|--------|--------|----------------------------|
| android-dev | Placeholder | api-designer, mobile-app-developer agents |
| api-dev | Placeholder | api-designer, api-documenter, graphql-architect agents |
| blog-workflow | List format | content-marketer, technical-writer agents |
| browser-extension-dev | Partial | Has MCP/skills defined, needs agent mapping |
| cad-dev | Placeholder | No matching components |
| content-creation | Placeholder | content-marketer, seo-specialist agents |
| frontend-dev | Placeholder | frontend-developer, react-specialist, vue-expert agents |
| go-projects | Placeholder | golang-pro agent, convert skills |
| homebrew-dev | Complete | Already migrated |
| infrastructure | Placeholder | terraform-engineer, kubernetes-specialist agents |
| ios-dev | Placeholder | swift-expert, mobile-app-developer agents |
| job-hunting | No sources | No matching components |
| mcp-server-dev | No sources | mcp-developer agent |
| model-dev | Placeholder | ml-engineer, data-scientist agents |
| pcb-design | No sources | embedded-systems agent (partial) |
| rust-projects | No sources | rust-engineer agent, convert skills |
| siem-ops | Placeholder | security-engineer, incident-responder agents |
| terraform | No sources | terraform-engineer, cloud-architect agents |

## Detailed Recommendations

### Ready for Component Mapping

These plugins could use existing context/ components:

#### api-dev
```json
{
  "agents/api-designer.md": "context/agents/api-designer.md",
  "agents/api-documenter.md": "context/agents/api-documenter.md",
  "agents/graphql-architect.md": "context/agents/graphql-architect.md"
}
```

#### frontend-dev
```json
{
  "agents/frontend-developer.md": "context/agents/frontend-developer.md",
  "agents/react-specialist.md": "context/agents/react-specialist.md",
  "agents/vue-expert.md": "context/agents/vue-expert.md",
  "agents/nextjs-developer.md": "context/agents/nextjs-developer.md"
}
```

#### go-projects
```json
{
  "agents/golang-pro.md": "context/agents/golang-pro.md"
}
```

#### infrastructure
```json
{
  "agents/terraform-engineer.md": "context/agents/terraform-engineer.md",
  "agents/kubernetes-specialist.md": "context/agents/kubernetes-specialist.md",
  "agents/cloud-architect.md": "context/agents/cloud-architect.md"
}
```

#### mcp-server-dev
```json
{
  "agents/mcp-developer.md": "context/agents/mcp-developer.md"
}
```

#### rust-projects
```json
{
  "agents/rust-engineer.md": "context/agents/rust-engineer.md"
}
```

#### siem-ops
```json
{
  "agents/security-engineer.md": "context/agents/security-engineer.md",
  "agents/incident-responder.md": "context/agents/incident-responder.md",
  "agents/penetration-tester.md": "context/agents/penetration-tester.md"
}
```

#### terraform
```json
{
  "agents/terraform-engineer.md": "context/agents/terraform-engineer.md",
  "agents/cloud-architect.md": "context/agents/cloud-architect.md"
}
```

### Needs Custom Components

These plugins have no matching components in context/:

- **cad-dev**: Would need CAD-specific skills/agents
- **pcb-design**: Would need PCB/electronics skills/agents
- **job-hunting**: Would need career-focused components
- **android-dev**: Has mobile-app-developer but may need Android-specific
- **ios-dev**: Has swift-expert but may need iOS-specific

### Planning Format (Skip Migration)

- **blog-workflow**: Uses list format for planning, not buildable

## Migration Priority

1. **High value** (many matching components):
   - infrastructure, terraform, api-dev, frontend-dev, siem-ops

2. **Medium value** (some matching components):
   - go-projects, rust-projects, mcp-server-dev

3. **Low value** (few/no matching components):
   - cad-dev, pcb-design, job-hunting, android-dev, ios-dev, content-creation, model-dev

## Recommended Actions

1. Update high-value plugins with real component mappings
2. Keep placeholder sources for low-value plugins until domain-specific components exist
3. Remove placeholder files (foo.md, bar.md) and use empty sources for plugins without shared components
