# Apple Platform Family

> Languages designed for Apple platforms featuring reference counting and deep framework integration.

## Overview

The Apple family includes languages designed for macOS, iOS, watchOS, and tvOS development:

- **ARC (Automatic Reference Counting)** - Memory management via reference counting
- **Framework integration** - Deep ties to Cocoa/Cocoa Touch
- **Protocol-oriented** - Swift emphasizes protocols over inheritance
- **Interoperability** - Swift ↔ Objective-C seamless bridging
- **Platform-specific** - Designed for Apple ecosystem

## Subtypes

| Subtype | Description | Languages |
|---------|-------------|-----------|
| **legacy** | Original Apple development language | Objective-C |
| **modern** | Current primary language | Swift |

### Legacy vs Modern Differences

| Aspect | Objective-C | Swift |
|--------|-------------|-------|
| Typing | Dynamic (runtime) | Static |
| Null handling | nil messages return 0/nil | Optionals required |
| Memory | Manual → ARC | ARC from start |
| Syntax | C + Smalltalk | Modern, clean |
| Error handling | NSError pointers | throws/try/catch |
| Concurrency | GCD, blocks | async/await, actors |

## Key Characteristics

- **Reference counting** - ARC handles memory automatically
- **Protocol-oriented** - Protocols define behavior contracts
- **Value types** - Swift structs are value types
- **Optionals** - Explicit null handling in Swift
- **Closures** - First-class functions, blocks
- **Framework patterns** - Delegate, target-action, KVO

## Languages in Family

| Language | Subtype | Notes |
|----------|---------|-------|
| Swift | modern | Primary iOS/macOS language, protocol-oriented |
| Objective-C | legacy | C superset with Smalltalk messaging |

## Type System

### Objective-C (Dynamic)

- **Dynamic dispatch** - Message sending at runtime
- **id type** - Any object type
- **Lightweight generics** - NSArray<NSString *>
- **Protocols** - Informal and formal

```objc
// Dynamic typing
id object = @"Hello";
NSString *string = (NSString *)object;

// Protocols
@protocol DataSource <NSObject>
- (NSInteger)numberOfItems;
@end
```

### Swift (Static)

- **Strong static typing** - Compile-time checking
- **Type inference** - Local inference
- **Generics** - Full generic support
- **Optionals** - Explicit nullable types

```swift
// Optionals
var name: String? = nil
let unwrapped = name ?? "default"
if let name = name { print(name) }

// Generics
func swap<T>(_ a: inout T, _ b: inout T) {
    let temp = a; a = b; b = temp
}

// Protocols with associated types
protocol Container {
    associatedtype Item
    mutating func append(_ item: Item)
}
```

### Swift Type Patterns

```swift
// Enums with associated values
enum Result<Success, Failure: Error> {
    case success(Success)
    case failure(Failure)
}

// Structs (value types)
struct Point {
    var x: Double
    var y: Double
}

// Protocol extensions
extension Collection where Element: Numeric {
    var sum: Element {
        reduce(0, +)
    }
}
```

## Memory Model

### ARC (Automatic Reference Counting)

```swift
// Strong reference (default)
class Person {
    var name: String
    var apartment: Apartment?  // Strong
}

// Weak reference (breaks cycles)
class Apartment {
    weak var tenant: Person?  // Weak, optional
}

// Unowned reference (non-optional weak)
class Customer {
    var card: CreditCard!
}
class CreditCard {
    unowned let customer: Customer  // Unowned
}
```

### Memory Characteristics

| Feature | Description |
|---------|-------------|
| Reference counting | Compile-time inserted retain/release |
| Strong references | Default, increments count |
| Weak references | Doesn't increment, auto-zeroed |
| Unowned references | Doesn't increment, not zeroed |
| Copy-on-write | Value types optimize copies |

### Value vs Reference Types

```swift
// Value type (copied on assignment)
struct Point { var x, y: Int }
var p1 = Point(x: 1, y: 2)
var p2 = p1  // Copy
p2.x = 10    // p1.x still 1

// Reference type (shared on assignment)
class Box { var value: Int = 0 }
let b1 = Box()
let b2 = b1  // Same instance
b2.value = 10  // b1.value also 10
```

## Concurrency Model

### Swift Concurrency (5.5+)

```swift
// Async/await
func fetchData() async throws -> Data {
    let (data, _) = try await URLSession.shared.data(from: url)
    return data
}

// Actors (isolated state)
actor Counter {
    private var value = 0

    func increment() {
        value += 1
    }

    func getValue() -> Int {
        value
    }
}

// Structured concurrency
async let image = fetchImage()
async let metadata = fetchMetadata()
let result = await (image, metadata)
```

### Legacy Concurrency

```swift
// Grand Central Dispatch
DispatchQueue.global().async {
    let result = heavyComputation()
    DispatchQueue.main.async {
        updateUI(result)
    }
}

// Operation queues
let queue = OperationQueue()
queue.addOperation {
    // Background work
}
```

## Common Patterns

### Delegate Pattern

```swift
protocol TableViewDelegate: AnyObject {
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath)
}

class ViewController: TableViewDelegate {
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        // Handle selection
    }
}
```

### Protocol-Oriented Design

```swift
protocol Drawable {
    func draw()
}

extension Drawable {
    func draw() {
        print("Default drawing")
    }
}

struct Circle: Drawable {
    func draw() {
        print("Drawing circle")
    }
}
```

### Property Wrappers

```swift
@propertyWrapper
struct Clamped<Value: Comparable> {
    var wrappedValue: Value {
        didSet { wrappedValue = min(max(wrappedValue, range.lowerBound), range.upperBound) }
    }
    let range: ClosedRange<Value>
}

struct Player {
    @Clamped(range: 0...100) var health: Int = 100
}
```

### Result Builders (SwiftUI)

```swift
var body: some View {
    VStack {
        Text("Hello")
        Button("Tap me") { action() }
    }
}
```

## Conversion Considerations

### Converting FROM Apple

**What's easy to preserve:**

- Protocol definitions → interfaces/traits
- Pure functions → direct mapping
- Value types → structs/records
- Closures → lambdas/closures

**What's hard to translate:**

- ARC semantics → GC or ownership
- Objective-C runtime features → static alternatives
- KVO/KVC → explicit observation patterns
- Framework-specific patterns → target equivalents
- Property wrappers → decorators or custom solutions

**Common pitfalls:**

- Ignoring ARC-specific patterns (weak/unowned)
- Assuming protocol extensions work the same
- Missing optional chaining semantics

**Semantic gaps:**

- Apple → other: 6 gaps identified in Obj-C ↔ Swift conversions

### Converting TO Apple

**What maps naturally:**

- Interfaces → protocols
- Classes → classes or structs
- Lambdas → closures
- Async → async/await

**What requires restructuring:**

- Inheritance hierarchies → protocol composition
- Exceptions → throws/Result types
- Shared mutable state → actors
- Null → optionals (explicit handling)

**Idiomatic patterns to target:**

- Prefer structs over classes
- Use protocols for abstraction
- Leverage property wrappers
- Use Swift's async/await for concurrency
- Follow Apple's API design guidelines

**Anti-patterns to avoid:**

- Force unwrapping (!!) everywhere
- Massive view controllers
- Ignoring value type semantics
- Overusing inheritance

## Cross-References

### Phase 0 Pattern Clusters

- **Universal patterns**: bool, String, int, float
- **Family-specific**: @property patterns, weak/strong patterns
- **Gap patterns**: 6 gaps in Apple ↔ Apple conversions

### Related convert-* Skills

- convert-objc-swift (223 patterns)

## Sources

- [Swift Documentation](https://docs.swift.org/swift-book/)
- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Objective-C Programming Guide](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ProgrammingWithObjectiveC/)
- [Swift Evolution](https://github.com/apple/swift-evolution)

## See Also

- [Managed OOP](managed-oop.md) - Similar class-based patterns
- [Systems](systems.md) - Memory management comparison
- [Overview](overview.md) - Cross-family comparison matrices
