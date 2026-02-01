## Dart Formula Patterns

### Researching a Dart Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system confirmation | Repo root | Look for `pubspec.yaml` |
| Binary name(s) | `pubspec.yaml` or `bin/` directory | Dart CLI entry points in `bin/` |
| Dart SDK version | `pubspec.yaml` `environment.sdk` | Check version constraint |
| Dependencies | `pubspec.yaml` `dependencies` | Pub handles Dart deps |
| Test command | README | Check for `--help` or `--version` support |

**Quick check sequence:**

```bash
gh api repos/OWNER/REPO/contents/pubspec.yaml --jq '.content' | base64 -d | head -10
```

### Dependencies

```text
depends_on "dart-sdk" => :build
```

### Install Block

```text
def install
  system "dart", "pub", "get"
  system "dart", "compile", "exe", "bin/main.dart", "-o", "mytool"
  bin.install "mytool"
end
```

### JSON Schema Fields (`install-dart`)

| Field | Default | Purpose |
|-------|---------|---------|
| `compile_target` | `"exe"` | Dart compile target (`exe`, `aot-snapshot`, `kernel`) |
| `source_file` | `"bin/main.dart"` | Main Dart file to compile |

### Mustache Partial

The `langs/dart.mustache` partial renders `dart compile exe` with configurable source file.

### Common Issues

- **AOT compilation:** `dart compile exe` produces a native executable — no Dart runtime needed
- **Pub cache:** `dart pub get` downloads packages — ensure network access during build
- **Platform support:** Compiled binaries are platform-specific

### Reference

See `reference/templates/formulas/dart.rb` for a pipeline-generated example.
