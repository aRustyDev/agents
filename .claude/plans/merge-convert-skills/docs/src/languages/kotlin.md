# Kotlin

> Modern, concise JVM language with null safety, coroutines, and excellent Java interoperability.

## Overview

Kotlin is a statically typed programming language developed by JetBrains, first released in 2011 and reaching 1.0 in 2016. It was designed to be a more concise and safer alternative to Java while maintaining full interoperability with existing Java code and libraries.

Kotlin addresses many pain points of Java: null safety through nullable types, concise syntax with data classes and extension functions, and modern features like coroutines for asynchronous programming. Google announced Kotlin as a first-class language for Android development in 2017 and made it the preferred language in 2019.

The language runs on the JVM, compiles to JavaScript, and has native compilation via Kotlin/Native, making it suitable for multiplatform development.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Managed-OOP | JVM-based, null-safe |
| Secondary Family | ML-FP | Data classes, sealed classes |
| Subtype | modern-jvm | Java interop focus |

See: [Managed-OOP Family](../language-families/managed-oop.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 1.0 | 2016-02 | Initial stable release |
| 1.3 | 2018-10 | Coroutines stable, contracts |
| 1.4 | 2020-08 | SAM conversions, trailing comma |
| 1.5 | 2021-05 | Value classes, sealed interfaces |
| 1.7 | 2022-06 | K2 compiler preview, builders |
| 1.9 | 2023-07 | K2 beta, enum entries |
| 2.0 | 2024-05 | K2 compiler stable |

## Feature Profile

### Type System

- **Strength:** strong (static, null-safe)
- **Inference:** bidirectional (excellent local inference)
- **Generics:** bounded (reified for inline functions)
- **Nullability:** explicit (T vs T?, smart casts)

### Memory Model

- **Management:** gc (JVM garbage collection)
- **Mutability:** choice (val immutable, var mutable)
- **Allocation:** heap (JVM), value classes for optimization

### Control Flow

- **Structured:** if-else (expression), when, for, while, try-catch
- **Effects:** exceptions, Result type
- **Async:** coroutines (suspending functions, Flow)

### Data Types

- **Primitives:** Int, Long, Float, Double, Boolean, Char, Byte, Short
- **Composites:** data class, class, sealed class, enum class, object
- **Collections:** List, Set, Map (immutable views), MutableList, etc.
- **Abstraction:** interfaces, abstract classes, packages

### Metaprogramming

- **Macros:** none (compiler plugins)
- **Reflection:** runtime (kotlin-reflect)
- **Code generation:** annotation processors, KSP

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | Gradle, Maven | Gradle preferred |
| Build System | Gradle | Kotlin DSL support |
| LSP | Kotlin Language Server | JetBrains |
| Formatter | ktlint, detekt | ktlint standard |
| Linter | detekt | Comprehensive |
| REPL | kotlin (built-in), ki | Interactive |
| Test Framework | JUnit, Kotest | Kotest is Kotlin-native |

## Syntax Patterns

```kotlin
// Function definition
fun greet(name: String, times: Int = 1): String =
    "Hello, $name! ".repeat(times)

// Extension function
fun String.greet(times: Int = 1): String =
    "Hello, $this! ".repeat(times)

// Generic function
fun <T> identity(value: T): T = value

// Async function (coroutine)
suspend fun fetchData(url: String): Response {
    val response = httpClient.get(url)
    if (response.status != HttpStatusCode.OK) {
        throw HttpException(response.status)
    }
    return response
}

// Data class
data class User(
    val id: String,
    val name: String,
    val email: String? = null
)

// Sealed class (ADT)
sealed class Result<out T, out E> {
    data class Ok<T>(val value: T) : Result<T, Nothing>()
    data class Err<E>(val error: E) : Result<Nothing, E>()
}

sealed interface Shape {
    data class Circle(val radius: Double) : Shape
    data class Rectangle(val width: Double, val height: Double) : Shape
}

// When expression (pattern matching)
fun area(shape: Shape): Double = when (shape) {
    is Shape.Circle -> Math.PI * shape.radius * shape.radius
    is Shape.Rectangle -> shape.width * shape.height
}

// Null safety
val email: String? = user.email
val display = email ?: "no-email@example.com"
val length = email?.length ?: 0

// Safe call chain
val city = user?.address?.city ?: "Unknown"

// Elvis with throw
val nonNullEmail = email ?: throw IllegalStateException("Email required")

// Smart casts
fun process(obj: Any) {
    if (obj is String) {
        println(obj.length)  // Smart cast to String
    }
}

// Scoping functions
val user = User("1", "Alice").apply {
    println("Created user: $name")
}

val result = user.let { it.name.uppercase() }

val config = buildString {
    append("host=")
    append(host)
    appendLine()
}

// Collection operations
val numbers = listOf(1, 2, 3, 4, 5)
val sum = numbers
    .filter { it % 2 == 0 }
    .map { it * 2 }
    .sum()

// Coroutines
suspend fun loadData(): List<Item> = coroutineScope {
    val items = async { fetchItems() }
    val metadata = async { fetchMetadata() }
    combine(items.await(), metadata.await())
}

// Flow (reactive streams)
fun observeUsers(): Flow<User> = flow {
    while (true) {
        emit(fetchLatestUser())
        delay(1000)
    }
}

// DSL builder
fun html(init: HTML.() -> Unit): HTML = HTML().apply(init)

val page = html {
    head { title("Page") }
    body {
        div { +"Hello, World!" }
    }
}

// Delegation
class Derived(base: Base) : Base by base {
    override fun method() {
        // Override specific methods
    }
}

// Lazy initialization
val expensiveValue: String by lazy {
    computeExpensiveValue()
}
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| JVM-only features (full Kotlin) | moderate | Use Kotlin Multiplatform for cross-platform |
| No union types | minor | Use sealed classes |
| Coroutine debugging complexity | minor | Use coroutine debugger, structured concurrency |
| Gradle complexity | moderate | Use Kotlin DSL, convention plugins |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 0 | — |
| As Target | 0 | — |

**Note:** Not in current convert-* skills. Natural migration target from Java.

## Idiomatic Patterns

### Data Classes → Records/Structs

```kotlin
// Kotlin: data class
data class Point(val x: Int, val y: Int)
val p2 = p1.copy(x = 10)

// IR equivalent: record with copy
// Point { x: 10, ..p1 }
```

### Sealed Classes → ADTs

```kotlin
// Kotlin: sealed class hierarchy
sealed class Option<out T>
data class Some<T>(val value: T) : Option<T>()
object None : Option<Nothing>()

// IR equivalent: enum ADT
// enum Option<T> { Some(T), None }
```

### Coroutines → Async/Effect

```kotlin
// Kotlin: suspend function
suspend fun fetch(): Data = withContext(Dispatchers.IO) {
    api.getData()
}

// IR equivalent: async function
// async fn fetch() -> Data { api.get_data().await }
```

### Extension Functions → Methods/Traits

```kotlin
// Kotlin: extension function
fun String.wordCount(): Int = split(" ").size

// IR equivalent: trait implementation or method
// impl StringExt for String { fn word_count(&self) -> usize }
```

## Related Languages

- **Influenced by:** Java, Scala, Groovy, C#, ML
- **Influenced:** Swift (some features)
- **Compiles to:** JVM bytecode, JavaScript, Native (LLVM)
- **FFI compatible:** Java (seamless), C (Kotlin/Native)

## Sources

- [Kotlin Documentation](https://kotlinlang.org/docs/)
- [Kotlin Language Specification](https://kotlinlang.org/spec/)
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Kotlin Standard Library](https://kotlinlang.org/api/latest/jvm/stdlib/)

## See Also

- [Managed-OOP Family](../language-families/managed-oop.md)
- [Java](java.md) - Interop target
- [Scala](scala.md) - JVM alternative
- [Swift](swift.md) - Similar modern features
