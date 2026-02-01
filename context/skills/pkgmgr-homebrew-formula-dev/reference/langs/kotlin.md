## Kotlin Formula Patterns

### Researching a Kotlin Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system | Repo root | `build.gradle.kts` (Kotlin DSL) or `build.gradle` (Groovy DSL) |
| Binary name(s) | `build.gradle.kts` `application` block | Check `mainClass` and distribution scripts |
| Java version | `build.gradle.kts` `jvmTarget` | Map to Homebrew's `openjdk` version |
| Gradle wrapper | `gradlew` in repo | Prefer using the wrapper if present |
| Test command | README | Check for `--help` or `--version` support |

**Quick check sequence:**

```bash
gh api repos/OWNER/REPO/contents/build.gradle.kts --jq '.name' 2>/dev/null && echo "Kotlin/Gradle project"
```

### Dependencies

```text
depends_on "gradle" => :build
depends_on "openjdk"
```

### Install Block

```text
def install
  system "gradle", "installDist"
  libexec.install Dir["build/install/*/lib"]
  libexec.install Dir["build/install/*/bin"]
  (bin/"mytool").write_env_script libexec/"bin/mytool", JAVA_HOME: Formula["openjdk"].opt_prefix
end
```

### JSON Schema Fields (`install-kotlin`)

| Field | Default | Purpose |
|-------|---------|---------|
| `gradle_task` | `"installDist"` | Gradle task to run |
| `java_version` | `"openjdk"` | Java version dependency |
| `wrapper_name` | — | Name for the shell wrapper script |

### Mustache Partial

The `langs/kotlin.mustache` partial renders `gradle installDist` and creates an env script wrapper.

### Common Issues

- **Gradle wrapper:** If the project uses `gradlew`, you may need to use it instead of system Gradle
- **JAVA_HOME:** The wrapper script must set `JAVA_HOME` for the JVM to start
- **Fat JARs:** Some projects use `shadowJar` instead of `installDist`

### Reference

See `reference/templates/formulas/kotlin.rb` for a pipeline-generated example.
