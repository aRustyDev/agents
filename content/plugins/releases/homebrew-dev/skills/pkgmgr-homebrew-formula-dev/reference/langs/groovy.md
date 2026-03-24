## Groovy Formula Patterns

> **Mapping:** Use `language: "kotlin"` — Groovy projects use the same Gradle build system and JVM runtime.

### Researching a Groovy Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system | Repo root | `build.gradle` (Gradle) — same as Kotlin projects |
| JAR output | `build.gradle` | Check for `jar` or `application` plugin |
| Groovy version | `build.gradle` | Check `groovyVersion` or dependency |
| Test command | README | Check for `--help` or `--version` |

### Dependencies

```text
depends_on "gradle" => :build
depends_on "openjdk"
```

### Common Issues

- **Same as Kotlin:** Groovy uses the same Gradle + JVM pattern — follow Kotlin formula patterns
- **Groovy runtime:** May need `depends_on "groovy"` if not bundled in fat JAR
- **Script vs compiled:** Groovy can be scripted or compiled — prefer compiled JARs for formulas
