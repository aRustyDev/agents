## Swift Formula Patterns

### Researching a Swift Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system confirmation | Repo root | Look for `Package.swift` |
| Binary name(s) | `Package.swift` `.executableTarget` | The target name is the binary |
| Swift version | `Package.swift` `swift-tools-version` | Must be compatible with Homebrew's Swift |
| Platform support | `Package.swift` `platforms` | Check for macOS/Linux platform requirements |
| Dependencies | `Package.swift` `dependencies` | SPM handles these; check for system library deps |

**Quick check sequence:**

```bash
gh api repos/OWNER/REPO/contents/Package.swift --jq '.content' | base64 -d | head -5
```

### Dependencies

```text
depends_on xcode: ["14.0", :build]  # if needed
```

### Install Block

```text
def install
  system "swift", "build", "-c", "release", "--disable-sandbox"
  bin.install ".build/release/mytool"
end
```

### JSON Schema Fields (`install-swift`)

| Field | Default | Purpose |
|-------|---------|---------|
| `configuration` | `"release"` | Build configuration |
| `static_linking` | `true` | Use static linking |
| `build_args` | — | Additional swift build arguments |

### Mustache Partial

The `langs/swift.mustache` partial renders `swift build` with configuration and installs from `.build/`.

### Common Issues

- **macOS only:** Many Swift projects only support macOS — check `platforms` in `Package.swift`
- **Xcode dependency:** Some projects need Xcode CLI tools or specific SDK versions
- **Static linking:** Use `--static-swift-stdlib` for portable binaries on Linux

### Reference

See `reference/templates/formulas/swift.rb` for a pipeline-generated example.
