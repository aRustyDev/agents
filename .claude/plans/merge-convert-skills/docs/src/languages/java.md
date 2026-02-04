# Java

> Statically typed, class-based object-oriented language designed for portability and enterprise applications.

## Overview

Java is a class-based, object-oriented programming language developed by James Gosling at Sun Microsystems, first released in 1995. It was designed with the principle of "write once, run anywhere" (WORA), compiling to bytecode that runs on the Java Virtual Machine (JVM).

Modern Java has evolved significantly from its verbose origins. Java 8 introduced lambdas and streams, Java 14+ brought records, sealed classes, and pattern matching. The language maintains backward compatibility while adding modern features, making it suitable for both legacy systems and new development.

Java dominates enterprise computing, Android development (historically), and large-scale distributed systems. Its ecosystem includes Spring Framework, Jakarta EE, and a vast library ecosystem.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Managed-OOP | Class-based, GC-managed |
| Secondary Family | — | Increasingly functional (Java 8+) |
| Subtype | enterprise | Enterprise patterns dominant |

See: [Managed-OOP Family](../language-families/managed-oop.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| Java 8 | 2014-03 | Lambdas, streams, Optional, default methods |
| Java 11 | 2018-09 | LTS, var, HTTP client, collection factories |
| Java 17 | 2021-09 | LTS, sealed classes, pattern matching preview |
| Java 21 | 2023-09 | LTS, virtual threads, record patterns, sequenced collections |

## Feature Profile

### Type System

- **Strength:** strong (static, nominal)
- **Inference:** limited (var since Java 10, diamond operator)
- **Generics:** type-erasure (reified at compile time only)
- **Nullability:** nullable (Optional<T> for explicit)

### Memory Model

- **Management:** gc (JVM garbage collection, multiple collectors)
- **Mutability:** default-mutable (final for immutability)
- **Allocation:** heap (objects), stack (primitives)
- **Value types:** primitive types + records (quasi-value)

### Control Flow

- **Structured:** if-else, for, while, switch (expression in Java 14+), try-catch
- **Effects:** exceptions (checked and unchecked)
- **Async:** CompletableFuture, virtual threads (Java 21+)

### Data Types

- **Primitives:** byte, short, int, long, float, double, boolean, char
- **Composites:** classes, records, arrays, enums
- **Collections:** List, Set, Map, Queue (java.util)
- **Abstraction:** classes, interfaces, packages, modules (Java 9+)

### Metaprogramming

- **Macros:** none
- **Reflection:** runtime (java.lang.reflect)
- **Code generation:** annotation processors, bytecode manipulation

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | Maven, Gradle | Maven for dependencies |
| Build System | Maven, Gradle, Bazel | Gradle is modern |
| LSP | Eclipse JDT LS | Good IDE support |
| Formatter | google-java-format | Opinionated |
| Linter | SpotBugs, Error Prone | Static analysis |
| REPL | JShell (Java 9+) | Built-in |
| Test Framework | JUnit, TestNG | JUnit 5 is standard |

## Syntax Patterns

```java
// Function (method) definition
public String greet(String name, int times) {
    return "Hello, " + name + "! ".repeat(times);
}

// Generic method
public <T> T identity(T value) {
    return value;
}

// Async method (CompletableFuture)
public CompletableFuture<Response> fetchData(String url) {
    return httpClient.sendAsync(
        HttpRequest.newBuilder(URI.create(url)).build(),
        HttpResponse.BodyHandlers.ofString()
    ).thenApply(response -> {
        if (response.statusCode() != 200) {
            throw new HttpException(response.statusCode());
        }
        return response;
    });
}

// Record (Java 14+)
public record User(String id, String name, Optional<String> email) {
    public User {
        Objects.requireNonNull(id);
        Objects.requireNonNull(name);
    }
}

// Enum with behavior
public enum Shape {
    CIRCLE {
        @Override
        public double area(double... params) {
            double radius = params[0];
            return Math.PI * radius * radius;
        }
    },
    RECTANGLE {
        @Override
        public double area(double... params) {
            return params[0] * params[1];
        }
    };

    public abstract double area(double... params);
}

// Sealed interface (Java 17+)
public sealed interface Result<T> permits Ok, Err {
}

public record Ok<T>(T value) implements Result<T> {}
public record Err<T>(String error) implements Result<T> {}

// Pattern matching (Java 21+)
public String describe(Object obj) {
    return switch (obj) {
        case Integer i -> "Integer: " + i;
        case String s when s.length() > 10 -> "Long string";
        case String s -> "String: " + s;
        case null -> "null";
        default -> "Unknown";
    };
}

// Record patterns (Java 21+)
public double area(Shape shape) {
    return switch (shape) {
        case Circle(var radius) -> Math.PI * radius * radius;
        case Rectangle(var w, var h) -> w * h;
    };
}

// Interface definition
public interface Repository<T, ID> {
    Optional<T> findById(ID id);
    T save(T entity);
    void delete(T entity);
}

// Lambda and streams
List<Integer> numbers = List.of(1, 2, 3, 4, 5);
int sum = numbers.stream()
    .filter(n -> n % 2 == 0)
    .map(n -> n * 2)
    .reduce(0, Integer::sum);

// Optional handling
String email = user.email()
    .orElse("no-email@example.com");

String displayName = Optional.ofNullable(user.name())
    .map(String::toUpperCase)
    .orElseThrow(() -> new IllegalStateException("Name required"));

// Error handling
public Result<Integer> divide(int a, int b) {
    try {
        return new Ok<>(a / b);
    } catch (ArithmeticException e) {
        return new Err<>("Division by zero");
    }
}

// Traditional try-with-resources
try (var reader = new BufferedReader(new FileReader(path))) {
    return reader.lines().collect(Collectors.joining("\n"));
} catch (IOException e) {
    throw new RuntimeException("Failed to read file", e);
}

// Virtual threads (Java 21+)
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i -> {
        executor.submit(() -> {
            Thread.sleep(Duration.ofSeconds(1));
            return i;
        });
    });
}

// Annotation
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Logged {
    String level() default "INFO";
}
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| Null pointer exceptions | high | Use Optional, @Nullable annotations |
| Checked exceptions verbosity | moderate | Use unchecked exceptions, wrap in RuntimeException |
| Type erasure limits | moderate | Use class tokens, reified types in Kotlin |
| Verbosity (pre-records) | minor | Use records (Java 14+), Lombok |
| No true value types (yet) | minor | Use records, await Valhalla project |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 3 | java-c, java-cpp, java-rust |
| As Target | 0 | — |

**Note:** Java version significantly affects conversion patterns. Modern Java (17+) is much more concise.

## Idiomatic Patterns

### Records → Data Classes/Structs

```java
// Java: record
public record Point(int x, int y) {}

// IR equivalent: data class
// data class Point(x: int, y: int)
// OR struct Point { x: i32, y: i32 }
```

### Optional → Maybe/Option

```java
// Java: Optional
Optional.ofNullable(value).map(String::toUpperCase).orElse("default");

// IR equivalent: Option combinators
// value.map(|s| s.to_uppercase()).unwrap_or("default")
```

### Streams → Iterators/Lazy Sequences

```java
// Java: stream
list.stream().filter(predicate).map(transform).collect(toList());

// IR equivalent: iterator chain
// list.iter().filter(predicate).map(transform).collect()
```

### Sealed Types → ADTs

```java
// Java: sealed interface with records
sealed interface Shape permits Circle, Rectangle {}
record Circle(double radius) implements Shape {}
record Rectangle(double w, double h) implements Shape {}

// IR equivalent: enum ADT
// enum Shape { Circle(f64), Rectangle(f64, f64) }
```

## Related Languages

- **Influenced by:** C++, Smalltalk, Objective-C
- **Influenced:** C#, Kotlin, Scala, Groovy, Ceylon
- **Compiles to:** JVM bytecode, native (GraalVM)
- **FFI compatible:** JNI (C/C++), JNA, Panama API (Java 22+)

## Sources

- [Java Language Specification](https://docs.oracle.com/javase/specs/)
- [Java SE Documentation](https://docs.oracle.com/en/java/javase/)
- [OpenJDK JEPs](https://openjdk.org/jeps/)
- [Effective Java (Bloch)](https://www.oreilly.com/library/view/effective-java/9780134686097/)

## See Also

- [Managed-OOP Family](../language-families/managed-oop.md)
- [Kotlin](kotlin.md) - Modern JVM alternative
- [Scala](scala.md) - FP on JVM
- [C#](csharp.md) - Similar managed OOP
