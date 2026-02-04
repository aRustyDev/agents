# Managed OOP Family

> Class-based object-oriented languages with managed memory (garbage collection).

## Overview

The Managed OOP family represents mainstream enterprise programming:

- **Class-based OOP** - Inheritance, encapsulation, polymorphism
- **Garbage collection** - Automatic memory management
- **Static typing** - Compile-time type checking
- **Platform runtimes** - JVM, CLR provide services
- **Rich ecosystems** - Extensive libraries and frameworks

These languages dominate enterprise software development.

## Subtypes

| Subtype | Description | Languages |
|---------|-------------|-----------|
| **classic** | Traditional class-based OOP | Java, C# |
| **modern** | OOP with functional features | Kotlin |

### Classic vs Modern Differences

| Aspect | Classic | Modern |
|--------|---------|--------|
| Null handling | Nullable by default | Non-null by default (Kotlin) |
| Functional features | Added later (streams, lambdas) | Native |
| Boilerplate | Verbose | Concise (data classes, etc.) |
| Syntax | Traditional | Expressive |

## Key Characteristics

- **Classes and interfaces** - Primary abstraction mechanisms
- **Inheritance** - Single class inheritance, multiple interface
- **Encapsulation** - Access modifiers (public, private, protected)
- **Generics** - Parametric polymorphism with bounds
- **Exceptions** - Try-catch error handling
- **Garbage collection** - JVM GC or CLR GC
- **Reflection** - Runtime type introspection

## Languages in Family

| Language | Subtype | Platform | Notes |
|----------|---------|----------|-------|
| Java | classic | JVM | Ubiquitous, verbose, stable |
| C# | classic | .NET/CLR | Microsoft ecosystem, LINQ |
| Kotlin | modern | JVM/Native/JS | Concise, null-safe, coroutines |

## Type System

### Static Typing

- **Nominal typing** - Types identified by name, not structure
- **Generic types** - With type erasure (Java) or reified (C#, Kotlin)
- **Bounded generics** - `<T extends Comparable<T>>`

### Type Features

| Feature | Java | C# | Kotlin |
|---------|------|-----|--------|
| Generics | ◕ Erased | ● Reified | ● Reified |
| Null safety | ◔ Optional | ◔ Nullable refs | ● Native |
| Pattern matching | ◔ Java 21+ | ◕ Switch expressions | ◕ When |
| Type inference | ◔ var (10+) | ◕ var | ● Native |
| Records/Data classes | ◕ Java 16+ | ● Records (C# 9) | ● Data classes |

### Common Type Patterns

```java
// Java generics
public interface Repository<T, ID> {
    T findById(ID id);
    List<T> findAll();
}

// Bounded generics
public <T extends Comparable<T>> T max(T a, T b) {
    return a.compareTo(b) > 0 ? a : b;
}
```

```kotlin
// Kotlin with null safety
fun process(name: String?): String {
    return name?.uppercase() ?: "default"
}

// Data classes
data class Person(val name: String, val age: Int)
```

## Memory Model

- **Garbage collected** - JVM or CLR manages memory
- **Heap allocation** - Objects on heap, primitives on stack (Java)
- **Value types** - C# structs, Java primitives
- **Reference semantics** - Objects accessed by reference

### GC Characteristics

| Platform | GC Types | Notes |
|----------|----------|-------|
| JVM | G1, ZGC, Shenandoah | Highly tunable |
| CLR | Workstation, Server | Generational |

### Memory Patterns

```java
// Java: all objects on heap
String s = new String("hello");  // heap
int x = 42;  // stack (primitive)

// C#: value types on stack
struct Point { public int X, Y; }
Point p = new Point();  // stack (value type)
```

## Concurrency Model

### Java

- **Threads** - `java.lang.Thread`
- **Executors** - Thread pool management
- **CompletableFuture** - Async composition
- **Virtual threads** - Project Loom (Java 21+)

```java
// Virtual threads (Java 21+)
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> processTask());
}

// CompletableFuture
CompletableFuture.supplyAsync(() -> fetchData())
    .thenApply(this::process)
    .thenAccept(this::save);
```

### C

- **async/await** - Native async support
- **Task Parallel Library** - High-level parallelism
- **Channels** - Producer-consumer patterns

```csharp
// C# async/await
public async Task<string> FetchDataAsync(string url) {
    using var client = new HttpClient();
    return await client.GetStringAsync(url);
}
```

### Kotlin

- **Coroutines** - Lightweight concurrency
- **Structured concurrency** - Scoped lifetime
- **Flow** - Reactive streams

```kotlin
// Kotlin coroutines
suspend fun fetchData(): Data {
    return withContext(Dispatchers.IO) {
        api.getData()
    }
}

// Flow
fun dataFlow(): Flow<Data> = flow {
    while (true) {
        emit(fetchLatest())
        delay(1000)
    }
}
```

## Common Patterns

### Dependency Injection

```java
// Constructor injection
public class UserService {
    private final UserRepository repository;

    public UserService(UserRepository repository) {
        this.repository = repository;
    }
}
```

### Builder Pattern

```java
User user = User.builder()
    .name("Alice")
    .email("alice@example.com")
    .build();
```

### Streams/LINQ

```java
// Java streams
List<String> names = users.stream()
    .filter(u -> u.getAge() > 18)
    .map(User::getName)
    .collect(Collectors.toList());
```

```csharp
// C# LINQ
var names = users
    .Where(u => u.Age > 18)
    .Select(u => u.Name)
    .ToList();
```

### Extension Functions (Kotlin/C#)

```kotlin
fun String.addExclamation() = "$this!"
"Hello".addExclamation()  // "Hello!"
```

## Conversion Considerations

### Converting FROM Managed-OOP

**What's easy to preserve:**

- Class structures → classes, records, modules
- Interfaces → traits, protocols, interfaces
- Generics → generics (where available)
- Control flow → direct mapping

**What's hard to translate:**

- Inheritance hierarchies → composition (FP targets)
- Null handling → Option types (null-safe targets)
- Checked exceptions (Java) → Result types or unchecked
- Reflection-based code → static alternatives
- Framework-specific patterns → target equivalents

**Common pitfalls:**

- Keeping inheritance when composition is better
- Ignoring null safety improvements
- Over-using OOP patterns in FP targets

**Semantic gaps:**

- Managed-OOP → Systems: 13 gaps (GC → ownership)
- Managed-OOP → ML-FP: Class hierarchies → ADTs

### Converting TO Managed-OOP

**What maps naturally:**

- Functions → static methods or classes
- Modules → classes or packages
- Interfaces/traits → interfaces
- Records/structs → classes or records

**What requires restructuring:**

- ADTs → sealed classes/interfaces + subclasses
- Pattern matching → visitor pattern or switch
- Immutable data → final fields + builders
- Pure functions → stateless service classes
- Higher-order functions → interfaces (pre-Java 8) or lambdas

**Idiomatic patterns to target:**

- Use interfaces for abstraction
- Leverage streams/LINQ for collection operations
- Use dependency injection
- Prefer composition over inheritance
- Use records/data classes for DTOs

**Anti-patterns to avoid:**

- Anemic domain models
- God classes
- Excessive inheritance depth
- Null returns instead of Optional
- Checked exceptions for flow control

## Cross-References

### Phase 0 Pattern Clusters

- **Universal patterns**: bool, String, int, float, List
- **Family-specific**: Class patterns, interface patterns
- **Gap patterns**: 13 gaps Managed-OOP → Systems

### Related convert-* Skills

- convert-java-rust (235 patterns)
- convert-java-c (170 patterns)
- convert-java-cpp (99 patterns)

## Sources

- [Java Documentation](https://docs.oracle.com/en/java/)
- [C# Documentation](https://learn.microsoft.com/en-us/dotnet/csharp/)
- [Kotlin Documentation](https://kotlinlang.org/docs/)
- [Effective Java](https://www.oreilly.com/library/view/effective-java/9780134686097/)

## See Also

- [Dynamic](dynamic.md) - Similar patterns, different typing
- [Systems](systems.md) - Common conversion target
- [Overview](overview.md) - Cross-family comparison matrices
