## Custom Formula Patterns

### Overview

Use `language: "custom"` for formulas with non-standard build systems that don't fit any other language category. The install block is specified as an array of Ruby DSL commands.

### Researching a Custom Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build process | README, INSTALL, CI config | Understand the exact build steps |
| Binary name(s) | Build output, docs | Determine what files to install |
| Dependencies | Build docs, CI | Identify all build and runtime dependencies |
| Install locations | Build system | Determine if files go to `bin/`, `lib/`, `libexec/`, etc. |

### Dependencies

Varies by project — analyze build requirements carefully.

### Install Block

```text
def install
  system "make"
  bin.install "mybinary"
end
```

### JSON Schema Fields (`install-custom`)

| Field | Default | Purpose |
|-------|---------|---------|
| `commands` | (required) | Array of Ruby DSL commands for the install block |

### Mustache Partial

The `langs/custom.mustache` partial renders each command from the `commands` array verbatim.

### Common Issues

- **Install paths:** Use `bin.install`, `lib.install`, `libexec.install` as appropriate
- **Environment variables:** Set via `ENV["VAR"] = "value"` before system calls
- **Write scripts:** Use `(bin/"name").write` for wrapper scripts

### Reference

See `reference/templates/formulas/custom.rb` for a pipeline-generated example.
