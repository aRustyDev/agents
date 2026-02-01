## .NET (C#/F#) Formula Patterns

### Researching a .NET Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system confirmation | Repo root | Look for `*.csproj`, `*.fsproj`, or `*.sln` |
| Binary name(s) | `.csproj` `AssemblyName` or `PackageId` | Default is project directory name |
| Target framework | `.csproj` `TargetFramework` | e.g. `net8.0`, `net9.0` |
| Self-contained | Build requirements | Whether to bundle the .NET runtime |
| Dependencies | `.csproj` `PackageReference` | NuGet packages handled by `dotnet restore` |

**Quick check sequence:**

```bash
find . -name "*.csproj" -o -name "*.fsproj" | head -5
grep TargetFramework *.csproj 2>/dev/null
```

### Dependencies

```text
depends_on "dotnet"
```

### Install Block

```text
def install
  system "dotnet", "publish", "-c", "Release", "-o", "\#{libexec}"
  (bin/"mytool").write_env_script libexec/"mytool", DOTNET_ROOT: Formula["dotnet"].opt_libexec
end
```

### JSON Schema Fields (`install-dotnet`)

| Field | Default | Purpose |
|-------|---------|---------|
| `project` | — | Project or solution file to build |
| `configuration` | `"Release"` | Build configuration |
| `self_contained` | `false` | Publish as self-contained |
| `framework` | — | Target framework (e.g. `net8.0`) |

### Mustache Partial

The `langs/dotnet.mustache` partial renders `dotnet publish` and creates an env script wrapper.

### Common Issues

- **DOTNET_ROOT:** The wrapper script must set `DOTNET_ROOT` for the runtime to be found
- **Self-contained:** Self-contained builds are larger but don't need the .NET runtime formula
- **Runtime identifier:** May need `--runtime osx-arm64` or `--runtime linux-x64`

### Reference

See `reference/templates/formulas/dotnet.rb` for a pipeline-generated example.
