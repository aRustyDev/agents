## Clojure Formula Patterns

> **Recommended:** Use `language: "java"` with `build_system: "maven"` — Clojure projects produce JVM JARs.

### Overview

Clojure compiles to JVM bytecode. Most Clojure CLI tools are distributed as uberjars. Use `language: "java"` and `write_jar_script` for the wrapper.

### Dependencies

```text
depends_on "clojure" => :build  # or leiningen
depends_on "openjdk"
```

### Example Pattern (Leiningen)

```text
def install
  system "lein", "uberjar"
  libexec.install Dir["target/*-standalone.jar"].first => "mytool.jar"
  bin.write_jar_script libexec/"mytool.jar", "mytool"
end
```

### Common Issues

- **Leiningen vs deps.edn:** Check which build tool the project uses
- **Uberjar:** Prefer uberjar (fat JAR) for simpler formula
- **JVM startup:** Clojure tools have slow JVM startup — consider GraalVM native-image
