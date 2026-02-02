## Java Formula Patterns

### Researching a Java Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system | Repo root | `pom.xml` (Maven), `build.gradle` (Gradle), `build.xml` (Ant) |
| JAR output path | Build config | Maven: `target/*.jar`; Gradle: `build/libs/*.jar` |
| Java version | Build config, README | Check `sourceCompatibility` or `maven.compiler.source` |
| Main class | `MANIFEST.MF` or build config | Needed for `write_jar_script` |
| Runtime deps | Build config | Check for native library dependencies |

**Quick check sequence:**

```bash
gh api repos/OWNER/REPO/contents/pom.xml --jq '.name' 2>/dev/null && echo "Maven project"
gh api repos/OWNER/REPO/contents/build.gradle --jq '.name' 2>/dev/null && echo "Gradle project"
```

### Dependencies

```text
depends_on "openjdk" => :build  # or openjdk@17
depends_on "maven" => :build    # or gradle
```

### Install Block (Maven)

```text
def install
  system "mvn", "package", "-DskipTests"
  libexec.install "target/mytool.jar"
  bin.write_jar_script libexec/"mytool.jar", "mytool"
end
```

### JSON Schema Fields (`install-java`)

| Field | Default | Purpose |
|-------|---------|---------|
| `java_version` | `"openjdk"` | Java version dependency |
| `build_system` | `"maven"` | Build system (`maven`, `gradle`, `ant`, `manual`) |
| `jar_path` | — | Path to the output JAR file |
| `wrapper_name` | — | Name for the shell wrapper script |

### Mustache Partial

The `langs/java.mustache` partial renders build commands based on `build_system` and creates a wrapper script via `write_jar_script`.

### Common Issues

- **Fat JARs vs thin JARs:** Prefer fat/uber JARs (include all deps) for simpler formulas
- **Java version:** Ensure the JDK version matches the project's requirements
- **Wrapper scripts:** `write_jar_script` creates a shell wrapper that sets `JAVA_HOME`

### Reference

See `reference/templates/formulas/java.rb` for a pipeline-generated example.
