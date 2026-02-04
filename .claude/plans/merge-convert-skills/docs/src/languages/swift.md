# Swift

> Modern, safe programming language for Apple platforms with protocol-oriented programming and value semantics.

## Overview

Swift is a general-purpose, compiled programming language developed by Apple, first released in 2014. It was designed as a replacement for Objective-C, emphasizing safety, performance, and modern language features while maintaining interoperability with existing Objective-C code and Apple frameworks.

Swift combines the performance of compiled languages with modern features like type inference, optionals for null safety, and protocol-oriented programming. The language has evolved rapidly, adding features like async/await, actors, and result builders.

While primarily used for Apple platform development (iOS, macOS, watchOS, tvOS), Swift is also available for Linux and Windows, with growing adoption for server-side development.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Apple | Apple ecosystem |
| Secondary Family | ML-FP | Protocols, generics, optionals |
| Subtype | protocol-oriented | Protocol-first design |

See: [Apple Family](../language-families/apple.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 3.0 | 2016-09 | API guidelines, SE-0001 to SE-0117 |
| 4.0 | 2017-09 | Codable, String as Collection |
| 5.0 | 2019-03 | ABI stability, Result type |
| 5.5 | 2021-09 | Async/await, actors |
| 5.7 | 2022-09 | Regex literals, if-let shorthand |
| 5.9 | 2023-09 | Macros, parameter packs |

## Feature Profile

### Type System

- **Strength:** strong (static, no implicit conversions)
- **Inference:** bidirectional (local and global)
- **Generics:** bounded (associated types, where clauses)
- **Nullability:** explicit (Optional<T> with ? syntax)

### Memory Model

- **Management:** ARC (Automatic Reference Counting)
- **Mutability:** default-immutable (let), explicit mutability (var)
- **Allocation:** value types (struct) on stack, reference types (class) on heap
- **Copy semantics:** copy-on-write for standard library types

### Control Flow

- **Structured:** if-else, for-in, while, switch (exhaustive), guard
- **Effects:** throws/try/catch, Result type
- **Async:** async/await, actors (Swift 5.5+)

### Data Types

- **Primitives:** Int, Double, Float, Bool, Character, String
- **Composites:** struct, class, enum (with associated values), tuple
- **Collections:** Array, Dictionary, Set (value types)
- **Abstraction:** protocols, extensions, modules

### Metaprogramming

- **Macros:** compile-time (Swift 5.9+)
- **Reflection:** limited (Mirror type)
- **Code generation:** macros, result builders (@resultBuilder)

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | Swift Package Manager | Built-in |
| Build System | Xcode, SwiftPM | SwiftPM cross-platform |
| LSP | SourceKit-LSP | Official |
| Formatter | swift-format | Apple official |
| Linter | SwiftLint | Community standard |
| REPL | swift (built-in) | Interactive |
| Test Framework | XCTest | Built-in |

## Syntax Patterns

```swift
// Function definition
func greet(name: String, times: Int = 1) -> String {
    String(repeating: "Hello, \(name)! ", count: times)
}

// Generic function
func identity<T>(_ value: T) -> T {
    value
}

// Generic with constraint
func compare<T: Comparable>(_ a: T, _ b: T) -> Bool {
    a < b
}

// Async function
func fetchData(from url: URL) async throws -> Data {
    let (data, response) = try await URLSession.shared.data(from: url)
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw HTTPError.badStatus
    }
    return data
}

// Struct (value type)
struct User {
    let id: String
    var name: String
    var email: String?

    init(id: String, name: String, email: String? = nil) {
        self.id = id
        self.name = name
        self.email = email
    }
}

// Enum with associated values (ADT)
enum Result<Success, Failure: Error> {
    case success(Success)
    case failure(Failure)
}

enum Shape {
    case circle(radius: Double)
    case rectangle(width: Double, height: Double)

    var area: Double {
        switch self {
        case .circle(let radius):
            return .pi * radius * radius
        case .rectangle(let width, let height):
            return width * height
        }
    }
}

// Protocol definition
protocol Displayable {
    func display() -> String
}

extension User: Displayable {
    func display() -> String {
        "User(\(name))"
    }
}

// Protocol with associated type
protocol Container {
    associatedtype Item
    var count: Int { get }
    mutating func append(_ item: Item)
    subscript(i: Int) -> Item { get }
}

// Error handling
enum DivisionError: Error {
    case divisionByZero
}

func divide(_ a: Int, by b: Int) throws -> Int {
    guard b != 0 else {
        throw DivisionError.divisionByZero
    }
    return a / b
}

// Using Result type
func divideResult(_ a: Int, by b: Int) -> Result<Int, DivisionError> {
    guard b != 0 else {
        return .failure(.divisionByZero)
    }
    return .success(a / b)
}

// Optional handling
let email = user.email ?? "no-email@example.com"

if let email = user.email {
    print("Email: \(email)")
}

guard let email = user.email else {
    print("No email")
    return
}

// Pattern matching
switch value {
case let x where x > 0:
    print("Positive: \(x)")
case 0:
    print("Zero")
case let x:
    print("Negative: \(x)")
}

// Higher-order functions
let numbers = [1, 2, 3, 4, 5]
let sum = numbers
    .filter { $0 % 2 == 0 }
    .map { $0 * 2 }
    .reduce(0, +)

// Closure syntax
let sorted = names.sorted { $0 < $1 }
let sorted2 = names.sorted(by: <)

// Property wrapper
@propertyWrapper
struct Clamped<Value: Comparable> {
    private var value: Value
    let range: ClosedRange<Value>

    var wrappedValue: Value {
        get { value }
        set { value = min(max(newValue, range.lowerBound), range.upperBound) }
    }
}

// Result builder
@resultBuilder
struct ArrayBuilder {
    static func buildBlock<T>(_ components: T...) -> [T] {
        components
    }
}

// Actor (Swift 5.5+)
actor Counter {
    private var count = 0

    func increment() {
        count += 1
    }

    func getCount() -> Int {
        count
    }
}
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| Apple platform bias | moderate | Use SwiftPM for cross-platform, Swift on Server |
| ARC retain cycles | moderate | Use weak/unowned references |
| No reflection (full) | minor | Use Mirror for limited reflection, Codable |
| Rapid evolution | minor | Pin Swift version, follow proposals |
| Linux/Windows support gaps | moderate | Check library availability |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 0 | — |
| As Target | 1 | objc-swift |

**Note:** Primary target for Objective-C migration. Protocol-oriented programming influences conversion patterns.

## Idiomatic Patterns

### Optionals → Maybe/Option

```swift
// Swift: optional
let name: String? = user.name
let display = name ?? "Anonymous"

// IR equivalent: Option type
// let display = name.unwrap_or("Anonymous")
```

### Protocols → Traits/Type Classes

```swift
// Swift: protocol
protocol Hashable {
    func hash(into hasher: inout Hasher)
}

// IR equivalent: trait
// trait Hashable { fn hash(&self) -> u64 }
```

### Enums with Associated Values → ADTs

```swift
// Swift: enum with associated values
enum Either<L, R> {
    case left(L)
    case right(R)
}

// IR equivalent: ADT
// enum Either<L, R> { Left(L), Right(R) }
```

### async/await → Effect System

```swift
// Swift: async/await
let data = try await fetchData(from: url)

// IR equivalent: async or IO monad
// let data = fetch_data(url).await?
```

## Related Languages

- **Influenced by:** Objective-C, Rust, Haskell, Ruby, Python, C#
- **Influenced:** Kotlin (some), Mojo
- **Compiles to:** LLVM IR, native machine code
- **FFI compatible:** C, Objective-C, C++ (limited)

## Sources

- [Swift Programming Language](https://docs.swift.org/swift-book/)
- [Swift API Design Guidelines](https://swift.org/documentation/api-design-guidelines/)
- [Swift Evolution](https://github.com/apple/swift-evolution)
- [Swift.org](https://swift.org/)

## See Also

- [Apple Family](../language-families/apple.md)
- [Objective-C](objc.md) - Predecessor
- [Rust](rust.md) - Ownership comparison
- [Kotlin](kotlin.md) - Similar modern features
