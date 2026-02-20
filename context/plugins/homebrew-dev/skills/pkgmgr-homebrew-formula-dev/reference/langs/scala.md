## Scala Formula Patterns

### Researching a Scala Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system | Repo root | `build.sbt` (sbt) or `build.gradle` |
| Binary name(s) | `build.sbt` | Check for assembly plugin or native-packager |
| Scala version | `build.sbt` `scalaVersion` | Usually handled by sbt |
| Java version | `build.sbt` or README | Map to Homebrew's `openjdk` version |
| Test command | README | Check for `--help` or `--version` support |

**Quick check sequence:**

```bash
gh api repos/OWNER/REPO/contents/build.sbt --jq '.name' 2>/dev/null && echo "Scala/sbt project"
```

### Dependencies

```text
depends_on "sbt" => :build
depends_on "openjdk"
```

### Install Block

```text
def install
  system "sbt", "assembly"
  libexec.install Dir["target/**/*.jar"]
  bin.write_jar_script Dir[libexec/"*.jar"].first, "mytool"
end
```

### JSON Schema Fields (`install-scala`)

| Field | Default | Purpose |
|-------|---------|---------|
| `sbt_task` | `"assembly"` | sbt task to run |
| `java_version` | `"openjdk"` | Java version dependency |
| `wrapper_name` | — | Name for the shell wrapper script |

### Mustache Partial

The `langs/scala.mustache` partial renders `sbt assembly` and creates a JAR wrapper script.

### Common Issues

- **sbt-assembly plugin:** Required for fat JARs — check `project/plugins.sbt`
- **Scala version:** sbt downloads the Scala compiler — ensure network access during build
- **Memory:** sbt builds can be memory-intensive — may need `ENV["SBT_OPTS"]`

### Reference

See `reference/templates/formulas/scala.rb` for a pipeline-generated example.
