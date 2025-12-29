---
name: lang-java-library-dev
description: Java-specific library development patterns. Use when creating Java libraries, designing public APIs with interfaces and abstractions, configuring Maven/Gradle projects, managing dependencies, writing JUnit tests, documenting with Javadoc, or publishing to Maven Central. Extends meta-library-dev with Java tooling and ecosystem practices.
---

# Java Library Development

Java-specific patterns for library development. This skill extends `meta-library-dev` with Java tooling, API design patterns, and ecosystem practices.

## This Skill Extends

- `meta-library-dev` - Foundational library patterns (API design, versioning, testing strategies)

For general concepts like semantic versioning, module organization principles, and testing pyramids, see the meta-skill first.

## This Skill Adds

- **Java tooling**: Maven/Gradle configuration, dependency management, multi-module projects
- **Java API patterns**: Interface design, abstract classes, generics, builder patterns
- **Java ecosystem**: Maven Central publishing, Javadoc, JUnit testing, JAR packaging
- **Java conventions**: Package naming, access modifiers, annotation-driven configuration

## This Skill Does NOT Cover

- General library patterns - see `meta-library-dev`
- Java fundamentals - see `lang-java-dev`
- Spring framework libraries - see `lang-java-spring-dev`
- Build tool configuration details - see `lang-java-build-dev`
- Testing frameworks in depth - see `lang-java-test-dev`

---

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| New Maven library | `mvn archetype:generate -DarchetypeGroupId=org.apache.maven.archetypes -DarchetypeArtifactId=maven-archetype-quickstart` |
| New Gradle library | `gradle init --type java-library` |
| Build Maven | `mvn clean install` |
| Build Gradle | `./gradlew build` |
| Run tests | `mvn test` / `./gradlew test` |
| Generate Javadoc | `mvn javadoc:javadoc` / `./gradlew javadoc` |
| Deploy to Maven Central | `mvn clean deploy -P release` |
| Create JAR | `mvn package` / `./gradlew jar` |

---

## Maven Project Structure

### Standard Library Structure

```
my-library/
├── pom.xml
├── README.md
├── LICENSE
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── example/
│   │   │           └── mylib/
│   │   │               ├── MyLibrary.java
│   │   │               ├── api/
│   │   │               │   ├── Parser.java
│   │   │               │   └── Validator.java
│   │   │               ├── core/
│   │   │               │   └── ParserImpl.java
│   │   │               ├── model/
│   │   │               │   └── Config.java
│   │   │               └── exception/
│   │   │                   └── ParseException.java
│   │   └── resources/
│   │       └── META-INF/
│   └── test/
│       ├── java/
│       │   └── com/
│       │       └── example/
│       │           └── mylib/
│       │               ├── ParserTest.java
│       │               └── ValidatorTest.java
│       └── resources/
│           └── test-data.json
└── target/
```

### Essential pom.xml for Libraries

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- Coordinates -->
    <groupId>com.example</groupId>
    <artifactId>my-library</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <!-- Metadata -->
    <name>My Library</name>
    <description>A brief description of what this library does</description>
    <url>https://github.com/username/my-library</url>

    <licenses>
        <license>
            <name>Apache License 2.0</name>
            <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
        </license>
    </licenses>

    <developers>
        <developer>
            <id>username</id>
            <name>Your Name</name>
            <email>you@example.com</email>
        </developer>
    </developers>

    <scm>
        <connection>scm:git:git://github.com/username/my-library.git</connection>
        <developerConnection>scm:git:ssh://github.com:username/my-library.git</developerConnection>
        <url>https://github.com/username/my-library/tree/main</url>
    </scm>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <junit.version>5.10.1</junit.version>
    </properties>

    <dependencies>
        <!-- JUnit 5 for testing -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <!-- Compiler plugin -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
            </plugin>

            <!-- Javadoc plugin -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-javadoc-plugin</artifactId>
                <version>3.6.3</version>
                <executions>
                    <execution>
                        <id>attach-javadocs</id>
                        <goals>
                            <goal>jar</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>

            <!-- Source plugin -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-source-plugin</artifactId>
                <version>3.3.0</version>
                <executions>
                    <execution>
                        <id>attach-sources</id>
                        <goals>
                            <goal>jar-no-fork</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>

            <!-- Surefire for testing -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.2.3</version>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## Gradle Project Structure

### Essential build.gradle for Libraries

```gradle
plugins {
    id 'java-library'
    id 'maven-publish'
    id 'signing'
}

group = 'com.example'
version = '1.0.0'

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
    withJavadocJar()
    withSourcesJar()
}

repositories {
    mavenCentral()
}

dependencies {
    // API dependencies (exposed to consumers)
    api 'com.google.guava:guava:32.1.3-jre'

    // Implementation dependencies (not exposed)
    implementation 'org.slf4j:slf4j-api:2.0.9'

    // Test dependencies
    testImplementation 'org.junit.jupiter:junit-jupiter:5.10.1'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}

test {
    useJUnitPlatform()
}

javadoc {
    options.encoding = 'UTF-8'
    if (JavaVersion.current().isJava9Compatible()) {
        options.addBooleanOption('html5', true)
    }
}

publishing {
    publications {
        maven(MavenPublication) {
            from components.java

            pom {
                name = 'My Library'
                description = 'A brief description of what this library does'
                url = 'https://github.com/username/my-library'

                licenses {
                    license {
                        name = 'The Apache License, Version 2.0'
                        url = 'http://www.apache.org/licenses/LICENSE-2.0.txt'
                    }
                }

                developers {
                    developer {
                        id = 'username'
                        name = 'Your Name'
                        email = 'you@example.com'
                    }
                }

                scm {
                    connection = 'scm:git:git://github.com/username/my-library.git'
                    developerConnection = 'scm:git:ssh://github.com:username/my-library.git'
                    url = 'https://github.com/username/my-library/tree/main'
                }
            }
        }
    }

    repositories {
        maven {
            url = layout.buildDirectory.dir('repo')
        }
    }
}

signing {
    sign publishing.publications.maven
}
```

---

## Public API Design (Java-Specific)

### Interface-Based APIs

**Prefer interfaces for public APIs:**

```java
// Public interface - exposed to users
public interface Parser {
    /**
     * Parses the input string into a structured result.
     *
     * @param input the input string to parse
     * @return parsed result
     * @throws ParseException if input is invalid
     */
    ParseResult parse(String input) throws ParseException;

    /**
     * Parses with custom options.
     *
     * @param input the input string to parse
     * @param options parsing options
     * @return parsed result
     * @throws ParseException if input is invalid
     */
    ParseResult parse(String input, ParseOptions options) throws ParseException;
}

// Package-private implementation
class DefaultParser implements Parser {
    @Override
    public ParseResult parse(String input) throws ParseException {
        return parse(input, ParseOptions.defaults());
    }

    @Override
    public ParseResult parse(String input, ParseOptions options) throws ParseException {
        // Implementation
    }
}

// Factory method in public API
public final class Parsers {
    private Parsers() {} // Prevent instantiation

    /**
     * Creates a new parser instance with default settings.
     *
     * @return a new parser
     */
    public static Parser newParser() {
        return new DefaultParser();
    }

    /**
     * Creates a parser with custom configuration.
     *
     * @param config parser configuration
     * @return a new configured parser
     */
    public static Parser newParser(ParserConfig config) {
        return new DefaultParser(config);
    }
}
```

### Abstract Classes for Extensibility

```java
/**
 * Base class for custom validators.
 * <p>
 * Subclasses must implement {@link #doValidate(Object)} to provide
 * validation logic.
 *
 * @param <T> the type being validated
 */
public abstract class Validator<T> {
    private final String name;

    protected Validator(String name) {
        this.name = Objects.requireNonNull(name, "name cannot be null");
    }

    /**
     * Validates the input value.
     *
     * @param value the value to validate
     * @return validation result
     */
    public final ValidationResult validate(T value) {
        if (value == null) {
            return ValidationResult.invalid("Value cannot be null");
        }
        return doValidate(value);
    }

    /**
     * Performs validation logic.
     * <p>
     * Guaranteed to be called with non-null value.
     *
     * @param value the value to validate (never null)
     * @return validation result
     */
    protected abstract ValidationResult doValidate(T value);

    public String getName() {
        return name;
    }
}
```

### Immutable Value Objects

```java
/**
 * Configuration for parsing operations.
 * <p>
 * Instances are immutable and thread-safe.
 */
public final class ParseOptions {
    private final boolean strictMode;
    private final int maxDepth;
    private final Charset encoding;

    private ParseOptions(Builder builder) {
        this.strictMode = builder.strictMode;
        this.maxDepth = builder.maxDepth;
        this.encoding = builder.encoding;
    }

    public boolean isStrictMode() {
        return strictMode;
    }

    public int getMaxDepth() {
        return maxDepth;
    }

    public Charset getEncoding() {
        return encoding;
    }

    /**
     * Creates a builder for ParseOptions.
     *
     * @return a new builder
     */
    public static Builder builder() {
        return new Builder();
    }

    /**
     * Creates default parsing options.
     *
     * @return default options
     */
    public static ParseOptions defaults() {
        return builder().build();
    }

    public static final class Builder {
        private boolean strictMode = false;
        private int maxDepth = 100;
        private Charset encoding = StandardCharsets.UTF_8;

        private Builder() {}

        public Builder strictMode(boolean strictMode) {
            this.strictMode = strictMode;
            return this;
        }

        public Builder maxDepth(int maxDepth) {
            if (maxDepth < 1) {
                throw new IllegalArgumentException("maxDepth must be positive");
            }
            this.maxDepth = maxDepth;
            return this;
        }

        public Builder encoding(Charset encoding) {
            this.encoding = Objects.requireNonNull(encoding, "encoding cannot be null");
            return this;
        }

        public ParseOptions build() {
            return new ParseOptions(this);
        }
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof ParseOptions)) return false;
        ParseOptions that = (ParseOptions) o;
        return strictMode == that.strictMode &&
               maxDepth == that.maxDepth &&
               encoding.equals(that.encoding);
    }

    @Override
    public int hashCode() {
        return Objects.hash(strictMode, maxDepth, encoding);
    }

    @Override
    public String toString() {
        return "ParseOptions{" +
               "strictMode=" + strictMode +
               ", maxDepth=" + maxDepth +
               ", encoding=" + encoding +
               '}';
    }
}
```

### Generic API Design

```java
/**
 * A converter that transforms input of type S to output of type T.
 *
 * @param <S> source type
 * @param <T> target type
 */
@FunctionalInterface
public interface Converter<S, T> {
    /**
     * Converts the input value.
     *
     * @param source the input value
     * @return converted value
     * @throws ConversionException if conversion fails
     */
    T convert(S source) throws ConversionException;

    /**
     * Chains this converter with another.
     *
     * @param after the converter to apply after this one
     * @param <U> the output type of the chained converter
     * @return a composed converter
     */
    default <U> Converter<S, U> andThen(Converter<? super T, ? extends U> after) {
        Objects.requireNonNull(after);
        return (S s) -> after.convert(convert(s));
    }

    /**
     * Creates a converter that always returns a constant value.
     *
     * @param value the constant value
     * @param <S> source type
     * @param <T> target type
     * @return a constant converter
     */
    static <S, T> Converter<S, T> constant(T value) {
        return source -> value;
    }

    /**
     * Creates a converter from a function.
     *
     * @param function the conversion function
     * @param <S> source type
     * @param <T> target type
     * @return a converter
     */
    static <S, T> Converter<S, T> from(Function<S, T> function) {
        Objects.requireNonNull(function);
        return function::apply;
    }
}
```

---

## Package Organization

### Package Naming Conventions

```
com.example.mylib/
├── MyLib.java              # Main entry point
├── Parsers.java            # Factory for parsers
├── Validators.java         # Factory for validators
│
├── api/                    # Public interfaces
│   ├── Parser.java
│   ├── Validator.java
│   └── Converter.java
│
├── model/                  # Public data models
│   ├── ParseResult.java
│   ├── ParseOptions.java
│   └── ValidationResult.java
│
├── exception/              # Public exceptions
│   ├── ParseException.java
│   ├── ValidationException.java
│   └── ConversionException.java
│
├── spi/                    # Service Provider Interface
│   └── ParserProvider.java
│
└── internal/               # Package-private implementation
    ├── DefaultParser.java
    ├── DefaultValidator.java
    └── util/
        └── StringUtils.java
```

### Access Modifiers Strategy

| Modifier | When to Use |
|----------|-------------|
| `public` | Part of public API, fully documented |
| `protected` | For subclassing (use sparingly) |
| `package-private` | Implementation details, internal |
| `private` | Internal to class |

```java
// Public API class
public final class Parsers {
    // Private constructor - utility class
    private Parsers() {}

    // Public factory method
    public static Parser newParser() {
        return new DefaultParser();
    }
}

// Package-private implementation
class DefaultParser implements Parser {
    // Package-private for testing
    final ParserConfig config;

    // Package-private constructor
    DefaultParser() {
        this(ParserConfig.defaults());
    }

    DefaultParser(ParserConfig config) {
        this.config = config;
    }

    @Override
    public ParseResult parse(String input) {
        return parseInternal(input);
    }

    // Private helper method
    private ParseResult parseInternal(String input) {
        // Implementation
    }
}
```

---

## Exception Design

### Custom Exception Hierarchy

```java
/**
 * Base exception for all library exceptions.
 */
public class MyLibException extends Exception {
    public MyLibException(String message) {
        super(message);
    }

    public MyLibException(String message, Throwable cause) {
        super(message, cause);
    }

    public MyLibException(Throwable cause) {
        super(cause);
    }
}

/**
 * Thrown when parsing fails.
 */
public class ParseException extends MyLibException {
    private final int line;
    private final int column;

    public ParseException(String message, int line, int column) {
        super(String.format("%s at line %d, column %d", message, line, column));
        this.line = line;
        this.column = column;
    }

    public ParseException(String message, int line, int column, Throwable cause) {
        super(String.format("%s at line %d, column %d", message, line, column), cause);
        this.line = line;
        this.column = column;
    }

    public int getLine() {
        return line;
    }

    public int getColumn() {
        return column;
    }
}

/**
 * Thrown when validation fails.
 */
public class ValidationException extends MyLibException {
    private final List<String> errors;

    public ValidationException(String message) {
        this(List.of(message));
    }

    public ValidationException(List<String> errors) {
        super("Validation failed: " + String.join(", ", errors));
        this.errors = List.copyOf(errors);
    }

    public List<String> getErrors() {
        return errors;
    }
}
```

### Unchecked Exceptions for Programming Errors

```java
/**
 * Thrown when the library is used incorrectly.
 * <p>
 * This is an unchecked exception indicating a programming error.
 */
public class InvalidUsageException extends RuntimeException {
    public InvalidUsageException(String message) {
        super(message);
    }

    public InvalidUsageException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

---

## Testing Patterns

### JUnit 5 Test Structure

```java
package com.example.mylib;

import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.junit.jupiter.params.provider.CsvSource;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests for {@link Parser}.
 */
class ParserTest {

    private Parser parser;

    @BeforeEach
    void setUp() {
        parser = Parsers.newParser();
    }

    @AfterEach
    void tearDown() {
        // Cleanup if needed
    }

    @Test
    @DisplayName("Should parse valid input successfully")
    void shouldParseValidInput() throws ParseException {
        // Given
        String input = "valid input";

        // When
        ParseResult result = parser.parse(input);

        // Then
        assertNotNull(result);
        assertTrue(result.isValid());
        assertEquals("expected value", result.getValue());
    }

    @Test
    @DisplayName("Should throw ParseException for invalid input")
    void shouldThrowExceptionForInvalidInput() {
        // Given
        String input = "invalid input";

        // When/Then
        ParseException exception = assertThrows(
            ParseException.class,
            () -> parser.parse(input)
        );

        assertTrue(exception.getMessage().contains("invalid"));
    }

    @ParameterizedTest
    @ValueSource(strings = {"input1", "input2", "input3"})
    @DisplayName("Should parse multiple valid inputs")
    void shouldParseMultipleInputs(String input) throws ParseException {
        // When
        ParseResult result = parser.parse(input);

        // Then
        assertNotNull(result);
        assertTrue(result.isValid());
    }

    @ParameterizedTest
    @CsvSource({
        "input1, expected1",
        "input2, expected2",
        "input3, expected3"
    })
    @DisplayName("Should parse and produce expected output")
    void shouldProduceExpectedOutput(String input, String expected) throws ParseException {
        // When
        ParseResult result = parser.parse(input);

        // Then
        assertEquals(expected, result.getValue());
    }

    @Nested
    @DisplayName("Parser with strict mode")
    class StrictModeTests {

        private Parser strictParser;

        @BeforeEach
        void setUp() {
            ParseOptions options = ParseOptions.builder()
                .strictMode(true)
                .build();
            strictParser = Parsers.newParser(ParserConfig.fromOptions(options));
        }

        @Test
        @DisplayName("Should reject lenient input in strict mode")
        void shouldRejectLenientInput() {
            String input = "lenient input";

            assertThrows(
                ParseException.class,
                () -> strictParser.parse(input)
            );
        }
    }

    @Test
    @Disabled("TODO: Implement edge case handling")
    void shouldHandleEdgeCase() {
        // Test to be implemented
    }
}
```

### Test Utilities and Fixtures

```java
/**
 * Test utilities for parser tests.
 */
final class ParserTestUtils {
    private ParserTestUtils() {}

    static String loadTestResource(String name) throws IOException {
        try (InputStream is = ParserTest.class.getResourceAsStream("/" + name)) {
            if (is == null) {
                throw new IOException("Resource not found: " + name);
            }
            return new String(is.readAllBytes(), StandardCharsets.UTF_8);
        }
    }

    static ParseResult parseResource(Parser parser, String resourceName)
            throws IOException, ParseException {
        String input = loadTestResource(resourceName);
        return parser.parse(input);
    }
}
```

---

## Javadoc Documentation

### Class-Level Documentation

```java
/**
 * A parser for structured text input.
 * <p>
 * This parser supports multiple formats and provides extensive
 * configuration options through {@link ParseOptions}.
 *
 * <h2>Usage Example:</h2>
 * <pre>{@code
 * Parser parser = Parsers.newParser();
 * ParseResult result = parser.parse("input string");
 * if (result.isValid()) {
 *     System.out.println(result.getValue());
 * }
 * }</pre>
 *
 * <h2>Thread Safety:</h2>
 * <p>
 * Instances of this class are thread-safe and can be shared across
 * multiple threads.
 *
 * @since 1.0.0
 * @see ParseOptions
 * @see ParseResult
 */
public interface Parser {
    // ...
}
```

### Method-Level Documentation

```java
/**
 * Parses the input string with the specified options.
 * <p>
 * The parsing behavior is controlled by the options provided. In
 * strict mode, the parser will reject any input that doesn't conform
 * strictly to the format.
 *
 * @param input the input string to parse, must not be {@code null}
 * @param options parsing options, must not be {@code null}
 * @return the parsed result, never {@code null}
 * @throws ParseException if the input cannot be parsed
 * @throws NullPointerException if either argument is {@code null}
 * @since 1.0.0
 * @see ParseOptions
 */
ParseResult parse(String input, ParseOptions options) throws ParseException;
```

### Package Documentation (package-info.java)

```java
/**
 * Provides APIs for parsing and validating structured text.
 * <p>
 * The main entry points are:
 * <ul>
 *   <li>{@link com.example.mylib.Parsers} - Factory for parser instances</li>
 *   <li>{@link com.example.mylib.Validators} - Factory for validators</li>
 * </ul>
 *
 * <h2>Quick Start:</h2>
 * <pre>{@code
 * Parser parser = Parsers.newParser();
 * ParseResult result = parser.parse("input");
 * }</pre>
 *
 * @since 1.0.0
 */
package com.example.mylib;
```

### Javadoc Tags Reference

| Tag | Purpose | Example |
|-----|---------|---------|
| `@param` | Parameter description | `@param input the input string` |
| `@return` | Return value description | `@return parsed result` |
| `@throws` | Exception documentation | `@throws ParseException if invalid` |
| `@since` | Version introduced | `@since 1.0.0` |
| `@deprecated` | Deprecation notice | `@deprecated Use {@link #newMethod()} instead` |
| `@see` | Related reference | `@see ParseOptions` |
| `{@link}` | Inline link | `{@link Parser#parse(String)}` |
| `{@code}` | Inline code | `{@code parser.parse("input")}` |
| `<pre>{@code}` | Code block | See examples above |

---

## Publishing to Maven Central

### Requirements Checklist

- [ ] Valid `groupId` (matching domain you control)
- [ ] Unique `artifactId`
- [ ] Proper version (SemVer)
- [ ] Project metadata (name, description, URL)
- [ ] License information
- [ ] Developer information
- [ ] SCM information
- [ ] Javadoc JAR
- [ ] Sources JAR
- [ ] GPG-signed artifacts

### Maven Central Deployment (pom.xml)

```xml
<distributionManagement>
    <snapshotRepository>
        <id>ossrh</id>
        <url>https://oss.sonatype.org/content/repositories/snapshots</url>
    </snapshotRepository>
    <repository>
        <id>ossrh</id>
        <url>https://oss.sonatype.org/service/local/staging/deploy/maven2/</url>
    </repository>
</distributionManagement>

<build>
    <plugins>
        <!-- GPG signing -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-gpg-plugin</artifactId>
            <version>3.1.0</version>
            <executions>
                <execution>
                    <id>sign-artifacts</id>
                    <phase>verify</phase>
                    <goals>
                        <goal>sign</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>

        <!-- Nexus staging -->
        <plugin>
            <groupId>org.sonatype.plugins</groupId>
            <artifactId>nexus-staging-maven-plugin</artifactId>
            <version>1.6.13</version>
            <extensions>true</extensions>
            <configuration>
                <serverId>ossrh</serverId>
                <nexusUrl>https://oss.sonatype.org/</nexusUrl>
                <autoReleaseAfterClose>true</autoReleaseAfterClose>
            </configuration>
        </plugin>
    </plugins>
</build>
```

### settings.xml for Credentials

```xml
<settings>
    <servers>
        <server>
            <id>ossrh</id>
            <username>your-username</username>
            <password>your-password</password>
        </server>
    </servers>
</settings>
```

### Deployment Commands

```bash
# Deploy snapshot
mvn clean deploy

# Release version
mvn versions:set -DnewVersion=1.0.0
mvn clean deploy -P release

# Close and release on Nexus
mvn nexus-staging:close
mvn nexus-staging:release
```

---

## Multi-Module Projects

### Parent POM Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>mylib-parent</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>

    <modules>
        <module>mylib-core</module>
        <module>mylib-api</module>
        <module>mylib-impl</module>
        <module>mylib-extras</module>
    </modules>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <junit.version>5.10.1</junit.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <!-- Internal modules -->
            <dependency>
                <groupId>com.example</groupId>
                <artifactId>mylib-api</artifactId>
                <version>${project.version}</version>
            </dependency>

            <dependency>
                <groupId>com.example</groupId>
                <artifactId>mylib-core</artifactId>
                <version>${project.version}</version>
            </dependency>

            <!-- External dependencies -->
            <dependency>
                <groupId>org.junit.jupiter</groupId>
                <artifactId>junit-jupiter</artifactId>
                <version>${junit.version}</version>
                <scope>test</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <pluginManagement>
            <plugins>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-compiler-plugin</artifactId>
                    <version>3.11.0</version>
                </plugin>
            </plugins>
        </pluginManagement>
    </build>
</project>
```

### Module POM (Child)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>com.example</groupId>
        <artifactId>mylib-parent</artifactId>
        <version>1.0.0</version>
    </parent>

    <artifactId>mylib-core</artifactId>
    <name>MyLib Core</name>

    <dependencies>
        <!-- Versions inherited from parent -->
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>mylib-api</artifactId>
        </dependency>

        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

---

## Service Provider Interface (SPI)

### Defining an SPI

```java
/**
 * Service provider interface for custom parsers.
 * <p>
 * Implementations should be registered via {@code META-INF/services}.
 */
public interface ParserProvider {
    /**
     * Returns the name of this parser provider.
     *
     * @return provider name
     */
    String getName();

    /**
     * Creates a new parser instance.
     *
     * @param config parser configuration
     * @return a new parser
     */
    Parser createParser(ParserConfig config);

    /**
     * Indicates whether this provider supports the given format.
     *
     * @param format the format to check
     * @return {@code true} if supported
     */
    boolean supports(String format);
}
```

### Loading SPI Implementations

```java
public final class ParserProviders {
    private static final List<ParserProvider> PROVIDERS;

    static {
        PROVIDERS = loadProviders();
    }

    private ParserProviders() {}

    /**
     * Finds a provider that supports the given format.
     *
     * @param format the format
     * @return a suitable provider
     * @throws IllegalArgumentException if no provider found
     */
    public static ParserProvider findProvider(String format) {
        return PROVIDERS.stream()
            .filter(p -> p.supports(format))
            .findFirst()
            .orElseThrow(() -> new IllegalArgumentException(
                "No provider found for format: " + format));
    }

    private static List<ParserProvider> loadProviders() {
        List<ParserProvider> providers = new ArrayList<>();
        ServiceLoader<ParserProvider> loader =
            ServiceLoader.load(ParserProvider.class);
        loader.forEach(providers::add);
        return List.copyOf(providers);
    }
}
```

### Registering SPI Implementation

Create `src/main/resources/META-INF/services/com.example.mylib.spi.ParserProvider`:

```
com.example.mylib.internal.JsonParserProvider
com.example.mylib.internal.XmlParserProvider
```

---

## Anti-Patterns

### 1. Exposing Mutable Internal State

```java
// Bad: Exposes internal list that can be modified
public class Config {
    private List<String> values = new ArrayList<>();

    public List<String> getValues() {
        return values;  // Caller can modify!
    }
}

// Good: Return unmodifiable view
public class Config {
    private final List<String> values;

    public Config(List<String> values) {
        this.values = List.copyOf(values);
    }

    public List<String> getValues() {
        return values;  // Immutable
    }
}
```

### 2. Not Validating Constructor Parameters

```java
// Bad: No validation
public class Parser {
    private final ParserConfig config;

    public Parser(ParserConfig config) {
        this.config = config;  // What if null?
    }
}

// Good: Validate inputs
public class Parser {
    private final ParserConfig config;

    public Parser(ParserConfig config) {
        this.config = Objects.requireNonNull(config, "config cannot be null");
    }
}
```

### 3. Breaking Semantic Versioning

```java
// v1.0.0
public interface Parser {
    ParseResult parse(String input);
}

// v1.1.0 - WRONG! This breaks compatibility
public interface Parser {
    ParseResult parse(String input, ParseOptions options);
}

// v1.1.0 - Correct: Add new method with default implementation
public interface Parser {
    ParseResult parse(String input);

    default ParseResult parse(String input, ParseOptions options) {
        return parse(input);
    }
}
```

### 4. Not Documenting Thread Safety

```java
// Bad: No documentation about thread safety
public class Cache {
    private Map<String, Object> data = new HashMap<>();

    public void put(String key, Object value) {
        data.put(key, value);
    }
}

// Good: Clear documentation
/**
 * A cache for storing values.
 * <p>
 * <b>Thread Safety:</b> This class is NOT thread-safe. Callers must
 * provide external synchronization if used across multiple threads.
 */
public class Cache {
    private final Map<String, Object> data = new HashMap<>();

    public void put(String key, Object value) {
        data.put(key, value);
    }
}
```

---

## References

- `meta-library-dev` - Foundational library patterns
- `lang-java-dev` - Java fundamentals
- `lang-java-build-dev` - Maven/Gradle configuration
- `lang-java-test-dev` - JUnit testing strategies
- [Maven Central Guide](https://central.sonatype.org/publish/publish-guide/)
- [Javadoc Guidelines](https://www.oracle.com/technical-resources/articles/java/javadoc-tool.html)
- [JUnit 5 User Guide](https://junit.org/junit5/docs/current/user-guide/)
