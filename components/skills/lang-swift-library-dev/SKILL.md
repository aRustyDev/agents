---
name: lang-swift-library-dev
description: Swift package development with SPM. Use for Package.swift, public APIs, DocC, XCTest, XCFrameworks, and library publishing. Extends meta-library-dev.
---

# Swift Library Development

Swift-specific patterns for library and package development. This skill extends `meta-library-dev` with Swift Package Manager tooling, platform support, and ecosystem practices.

## This Skill Extends

- `meta-library-dev` - Foundational library patterns (API design, versioning, testing strategies)

## This Skill Adds

- **Swift tooling**: Package.swift, SPM workflows, DocC documentation, XCTest
- **Swift idioms**: Protocol-oriented design, value types, availability annotations
- **Swift ecosystem**: Platform support, XCFrameworks, dependency management

---

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| New library package | `swift package init --type library` |
| Build | `swift build` |
| Test | `swift test` |
| Build docs | `swift package generate-documentation` |
| Resolve dependencies | `swift package resolve` |
| Archive XCFramework | `xcodebuild -create-xcframework` |

---

## Package.swift Structure

### Basic Library Package

```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MyLibrary",
    platforms: [
        .iOS(.v16),
        .macOS(.v13),
        .watchOS(.v9),
        .tvOS(.v16),
        .visionOS(.v1)
    ],
    products: [
        .library(name: "MyLibrary", targets: ["MyLibrary"]),
    ],
    dependencies: [
        .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),
    ],
    targets: [
        .target(
            name: "MyLibrary",
            dependencies: [.product(name: "Logging", package: "swift-log")]
        ),
        .testTarget(name: "MyLibraryTests", dependencies: ["MyLibrary"]),
    ]
)
```

### Multi-Target Package

```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MyPackage",
    platforms: [.iOS(.v16), .macOS(.v13)],
    products: [
        .library(name: "MyPackage", targets: ["MyPackage"]),
        .library(name: "MyPackageTestSupport", targets: ["MyPackageTestSupport"]),
        .executable(name: "my-tool", targets: ["MyPackageCLI"]),
    ],
    dependencies: [
        .package(url: "https://github.com/apple/swift-argument-parser.git", from: "1.3.0"),
    ],
    targets: [
        .target(name: "MyPackage", resources: [.process("Resources")]),
        .target(name: "MyPackageTestSupport", dependencies: ["MyPackage"]),
        .executableTarget(
            name: "MyPackageCLI",
            dependencies: ["MyPackage", .product(name: "ArgumentParser", package: "swift-argument-parser")]
        ),
        .testTarget(name: "MyPackageTests", dependencies: ["MyPackage", "MyPackageTestSupport"]),
    ]
)
```

---

## Public API Design (Swift-Specific)

### Access Control

```swift
public func publicFunction() {}      // Part of API
func internalFunction() {}           // Default, not exposed
private func privateFunction() {}    // Same declaration only
fileprivate func filePrivate() {}    // Same file only
open class OpenBaseClass {}          // Subclassable outside module
```

### Protocol-Oriented API

```swift
public protocol DataSource {
    associatedtype Item
    func fetch() async throws -> [Item]
}

public extension DataSource {
    func fetchFirst() async throws -> Item? {
        try await fetch().first
    }
}
```

### Value Type APIs

```swift
public struct Configuration {
    public var timeout: TimeInterval
    public var retryCount: Int

    public init(timeout: TimeInterval = 30, retryCount: Int = 3) {
        self.timeout = timeout
        self.retryCount = retryCount
    }

    public func withTimeout(_ timeout: TimeInterval) -> Configuration {
        var copy = self
        copy.timeout = timeout
        return copy
    }
}
```

### Availability Annotations

```swift
@available(iOS 16.0, macOS 13.0, *)
public func modernFeature() {}

@available(*, deprecated, renamed: "newFunction")
public func oldFunction() { newFunction() }

#if os(iOS)
@available(iOS 16.0, *)
public func iOSOnlyFeature() {}
#endif
```

---

## Error Handling

### Custom Error Types

```swift
public enum MyLibraryError: Error, LocalizedError {
    case invalidInput(String)
    case networkError(underlying: Error)
    case notFound(id: String)

    public var errorDescription: String? {
        switch self {
        case .invalidInput(let reason): return "Invalid input: \(reason)"
        case .networkError(let error): return "Network error: \(error.localizedDescription)"
        case .notFound(let id): return "Resource not found: \(id)"
        }
    }
}
```

### Throwing Functions

```swift
public func process(_ input: String) throws -> Result {
    guard !input.isEmpty else {
        throw MyLibraryError.invalidInput("Input cannot be empty")
    }
    return Result(value: input)
}
```

### Result Type for Callbacks

```swift
public func fetch(completion: @escaping (Swift.Result<Data, MyLibraryError>) -> Void) {
    // For legacy callback APIs
}
```

---

## Serialization (Codable)

### Basic Codable Conformance

```swift
public struct User: Codable, Sendable {
    public let id: String
    public let name: String
    public let createdAt: Date

    public init(id: String, name: String, createdAt: Date = .now) {
        self.id = id
        self.name = name
        self.createdAt = createdAt
    }
}
```

### Custom Coding Keys

```swift
public struct APIResponse: Codable {
    public let userId: String
    public let userName: String

    private enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case userName = "user_name"
    }
}
```

### Encoder/Decoder Configuration

```swift
public extension JSONDecoder {
    static var myLibrary: JSONDecoder {
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }
}

public extension JSONEncoder {
    static var myLibrary: JSONEncoder {
        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        return encoder
    }
}
```

---

## Zero/Default Values

### Default Parameter Values

```swift
public struct NetworkClient {
    public let baseURL: URL
    public let timeout: TimeInterval
    public let retryPolicy: RetryPolicy

    public init(
        baseURL: URL,
        timeout: TimeInterval = 30.0,
        retryPolicy: RetryPolicy = .default
    ) {
        self.baseURL = baseURL
        self.timeout = timeout
        self.retryPolicy = retryPolicy
    }
}

public struct RetryPolicy {
    public let maxRetries: Int
    public let delay: TimeInterval

    public static let `default` = RetryPolicy(maxRetries: 3, delay: 1.0)
    public static let aggressive = RetryPolicy(maxRetries: 5, delay: 0.5)
    public static let none = RetryPolicy(maxRetries: 0, delay: 0)
}
```

### ExpressibleBy Protocols

```swift
public struct Timeout: ExpressibleByIntegerLiteral, ExpressibleByFloatLiteral {
    public let seconds: TimeInterval

    public init(integerLiteral value: Int) {
        self.seconds = TimeInterval(value)
    }

    public init(floatLiteral value: Double) {
        self.seconds = value
    }
}

// Usage: let timeout: Timeout = 30
```

---

## Metaprogramming

### Property Wrappers

```swift
@propertyWrapper
public struct Clamped<Value: Comparable> {
    private var value: Value
    private let range: ClosedRange<Value>

    public var wrappedValue: Value {
        get { value }
        set { value = min(max(newValue, range.lowerBound), range.upperBound) }
    }

    public init(wrappedValue: Value, _ range: ClosedRange<Value>) {
        self.range = range
        self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
    }
}

// Usage
public struct Volume {
    @Clamped(0...100) public var level: Int = 50
}
```

### Result Builders

```swift
@resultBuilder
public struct ArrayBuilder<Element> {
    public static func buildBlock(_ components: Element...) -> [Element] {
        components
    }

    public static func buildOptional(_ component: [Element]?) -> [Element] {
        component ?? []
    }

    public static func buildEither(first: [Element]) -> [Element] { first }
    public static func buildEither(second: [Element]) -> [Element] { second }
}
```

### Swift Macros (5.9+)

```swift
// Using macros from dependencies
import Observation

@Observable
public final class ViewModel {
    public var title: String = ""
    public var items: [Item] = []
}
```

---

## Testing Patterns

### XCTest Basics

```swift
import XCTest
@testable import MyPackage

final class MyPackageTests: XCTestCase {
    var service: MyService!

    override func setUp() async throws {
        service = MyService()
    }

    func testBasicFunctionality() throws {
        let result = try service.process("test")
        XCTAssertEqual(result.value, "test")
    }

    func testAsyncFunction() async throws {
        let result = try await service.fetchData()
        XCTAssertNotNil(result)
    }

    func testErrorHandling() async {
        do {
            _ = try await service.fetchWithInvalidInput("")
            XCTFail("Should throw error")
        } catch MyLibraryError.invalidInput {
            // Expected
        } catch {
            XCTFail("Wrong error type: \(error)")
        }
    }
}
```

### Test Support Package

```swift
// Sources/MyPackageTestSupport/Mocks.swift
public final class MockDataSource: DataSource {
    public var mockItems: [Item] = []
    public var shouldThrowError = false

    public init() {}

    public func fetch() async throws -> [Item] {
        if shouldThrowError { throw MockError.forced }
        return mockItems
    }
}
```

---

## Module Organization

```
MyPackage/
├── Package.swift
├── README.md
├── Sources/
│   ├── MyPackage/
│   │   ├── MyPackage.swift      # Main public API
│   │   ├── Models/
│   │   ├── Services/
│   │   └── Internal/            # Private implementation
│   └── MyPackageTestSupport/
└── Tests/
    └── MyPackageTests/
```

---

## Platform Support

```swift
#if os(iOS) || os(tvOS) || os(watchOS)
import UIKit
public typealias PlatformColor = UIColor
#elseif os(macOS)
import AppKit
public typealias PlatformColor = NSColor
#endif

#if canImport(SwiftUI)
import SwiftUI

@available(iOS 16.0, macOS 13.0, *)
public extension Configuration {
    func toView() -> some View {
        ConfigurationView(config: self)
    }
}
#endif
```

---

## Dependency Management

```swift
dependencies: [
    .package(url: "https://github.com/user/repo.git", from: "1.0.0"),  // Semantic version
    .package(url: "https://github.com/user/repo.git", exact: "1.0.0"), // Exact
    .package(url: "https://github.com/user/repo.git", branch: "main"), // Branch
    .package(path: "../LocalPackage"),                                  // Local dev
]
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Exposing `[String: Any]` | Loses type safety | Return domain types |
| Classes for value types | Unexpected sharing | Use structs |
| Force unwrapping in API | Crashes consumer apps | Use `throws` or optionals |
| Missing `@available` | Breaks older platforms | Annotate new APIs |

---

## Publishing Checklist

- [ ] All tests pass (`swift test`)
- [ ] Documentation builds (`swift package generate-documentation`)
- [ ] No compiler warnings
- [ ] README.md is comprehensive
- [ ] LICENSE file included
- [ ] Version tagged in git
- [ ] CHANGELOG.md updated

---

## References

### In This Skill

- [DocC Documentation Guide](references/docc-documentation.md)
- [Binary Frameworks & XCFrameworks](references/binary-frameworks.md)
- [Dependencies & Troubleshooting](references/dependencies-troubleshooting.md)

### Related Skills

- `meta-library-dev` - Foundational library patterns
- `lang-swift-dev` - Swift language fundamentals

### External

- [Swift Package Manager Documentation](https://www.swift.org/package-manager/)
- [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)
