---
name: lang-swift-library-dev
description: Swift-specific library and package development patterns. Use when creating Swift packages, designing public APIs with Swift Package Manager, configuring Package.swift, managing dependencies, building frameworks, publishing libraries, writing DocC documentation, or XCTest. Extends meta-library-dev with Swift tooling and idioms.
---

# Swift Library Development

Swift-specific patterns for library and package development. This skill extends `meta-library-dev` with Swift Package Manager tooling, platform support, and ecosystem practices.

## This Skill Extends

- `meta-library-dev` - Foundational library patterns (API design, versioning, testing strategies)

For general concepts like semantic versioning, module organization principles, and testing pyramids, see the meta-skill first.

## This Skill Adds

- **Swift tooling**: Package.swift, SPM workflows, DocC documentation, XCTest
- **Swift idioms**: Protocol-oriented design, value types in public APIs, availability annotations
- **Swift ecosystem**: Platform support, binary frameworks, XCFrameworks, dependency management

## This Skill Does NOT Cover

- General library patterns - see `meta-library-dev`
- iOS/macOS app development - see `lang-swift-dev`
- SwiftUI specifics - see `lang-swift-dev`
- UIKit development - see `lang-swift-dev`

---

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| New library package | `swift package init --type library` |
| Build | `swift build` |
| Test | `swift test` |
| Generate Xcode project | `swift package generate-xcodeproj` |
| Build docs | `swift package generate-documentation` |
| Resolve dependencies | `swift package resolve` |
| Update dependencies | `swift package update` |
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
        .library(
            name: "MyLibrary",
            targets: ["MyLibrary"]
        ),
    ],
    dependencies: [
        // External dependencies
        .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),
    ],
    targets: [
        .target(
            name: "MyLibrary",
            dependencies: [
                .product(name: "Logging", package: "swift-log"),
            ]
        ),
        .testTarget(
            name: "MyLibraryTests",
            dependencies: ["MyLibrary"]
        ),
    ]
)
```

### Multi-Target Package

```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MyPackage",
    platforms: [
        .iOS(.v16),
        .macOS(.v13)
    ],
    products: [
        // Core library
        .library(
            name: "MyPackage",
            targets: ["MyPackage"]
        ),
        // Optional testing utilities
        .library(
            name: "MyPackageTestSupport",
            targets: ["MyPackageTestSupport"]
        ),
        // CLI tool
        .executable(
            name: "my-tool",
            targets: ["MyPackageCLI"]
        ),
    ],
    dependencies: [
        .package(url: "https://github.com/apple/swift-argument-parser.git", from: "1.3.0"),
    ],
    targets: [
        // Main library target
        .target(
            name: "MyPackage",
            dependencies: [],
            resources: [
                .process("Resources")
            ]
        ),

        // Testing utilities (for package consumers)
        .target(
            name: "MyPackageTestSupport",
            dependencies: ["MyPackage"]
        ),

        // CLI tool target
        .executableTarget(
            name: "MyPackageCLI",
            dependencies: [
                "MyPackage",
                .product(name: "ArgumentParser", package: "swift-argument-parser"),
            ]
        ),

        // Tests
        .testTarget(
            name: "MyPackageTests",
            dependencies: [
                "MyPackage",
                "MyPackageTestSupport",
            ]
        ),
    ]
)
```

### Package with Plugins

```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MyPackage",
    products: [
        .library(name: "MyPackage", targets: ["MyPackage"]),
        .plugin(name: "MyPlugin", targets: ["MyPlugin"]),
    ],
    targets: [
        .target(name: "MyPackage"),
        .plugin(
            name: "MyPlugin",
            capability: .buildTool(),
            dependencies: []
        ),
    ]
)
```

---

## Public API Design (Swift-Specific)

### Access Control Best Practices

```swift
// Public - part of API
public func publicFunction() {}
public struct PublicType {}

// Internal - default, not exposed
func internalFunction() {}
struct InternalType {}

// Private - visible only in current file
private func privateFunction() {}

// Fileprivate - visible to all code in same file
fileprivate func filePrivateFunction() {}

// Open - can be subclassed/overridden outside module
open class OpenBaseClass {}
```

### Protocol-Oriented API Design

```swift
/// Core protocol for data sources
public protocol DataSource {
    associatedtype Item

    func fetch() async throws -> [Item]
}

/// Provide default implementation
public extension DataSource {
    func fetchFirst() async throws -> Item? {
        try await fetch().first
    }
}

/// Concrete implementation
public struct APIDataSource: DataSource {
    public typealias Item = User

    public init() {}

    public func fetch() async throws -> [User] {
        // Implementation
        []
    }
}
```

### Value Type APIs

```swift
/// Value type with copy-on-write semantics
public struct Configuration {
    public var timeout: TimeInterval
    public var retryCount: Int
    public var isVerbose: Bool

    public init(
        timeout: TimeInterval = 30,
        retryCount: Int = 3,
        isVerbose: Bool = false
    ) {
        self.timeout = timeout
        self.retryCount = retryCount
        self.isVerbose = isVerbose
    }
}

/// Builder pattern for complex configuration
public extension Configuration {
    func withTimeout(_ timeout: TimeInterval) -> Configuration {
        var copy = self
        copy.timeout = timeout
        return copy
    }

    func withRetryCount(_ count: Int) -> Configuration {
        var copy = self
        copy.retryCount = count
        return copy
    }
}
```

### Async/Await API Patterns

```swift
/// Async function with proper error handling
public func fetchUser(id: String) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

/// AsyncSequence for streaming data
public struct UserStream: AsyncSequence {
    public typealias Element = User

    public func makeAsyncIterator() -> AsyncIterator {
        AsyncIterator()
    }

    public struct AsyncIterator: AsyncIteratorProtocol {
        public mutating func next() async throws -> User? {
            // Implementation
            nil
        }
    }
}
```

### Availability Annotations

```swift
/// Mark API availability
@available(iOS 16.0, macOS 13.0, *)
public func modernFeature() {
    // Uses iOS 16+ APIs
}

/// Deprecate old APIs
@available(*, deprecated, renamed: "newFunction")
public func oldFunction() {
    newFunction()
}

/// Mark as obsoleted
@available(*, obsoleted: 2.0, message: "Use newAPI instead")
public func veryOldFunction() {}

/// Platform-specific API
#if os(iOS)
@available(iOS 16.0, *)
public func iOSOnlyFeature() {}
#endif
```

---

## Module Organization

### Standard Package Structure

```
MyPackage/
├── Package.swift
├── README.md
├── LICENSE
├── Sources/
│   ├── MyPackage/
│   │   ├── MyPackage.swift      # Main public API
│   │   ├── Models/
│   │   │   ├── User.swift
│   │   │   └── Configuration.swift
│   │   ├── Services/
│   │   │   └── NetworkService.swift
│   │   ├── Internal/            # Private implementation
│   │   │   └── Utilities.swift
│   │   └── Resources/
│   │       └── Assets.xcassets
│   └── MyPackageTestSupport/    # Testing utilities
│       └── Mocks.swift
├── Tests/
│   └── MyPackageTests/
│       ├── ModelTests.swift
│       └── ServiceTests.swift
└── Examples/                    # Example projects
    └── BasicExample/
        ├── Package.swift
        └── Sources/
```

### Main Module File

```swift
// Sources/MyPackage/MyPackage.swift

/// # MyPackage
///
/// A brief description of what this package does.
///
/// ## Overview
///
/// MyPackage provides a clean API for...
///
/// ## Usage
///
/// ```swift
/// let config = Configuration()
/// let service = MyService(configuration: config)
/// let result = try await service.fetch()
/// ```

// Re-export public types
@_exported import struct Foundation.URL
@_exported import struct Foundation.Data

// Make internal types public
public typealias CompletionHandler = (Result<Data, Error>) -> Void

/// Main entry point for the library
public struct MyPackage {
    public static let version = "1.0.0"

    public init() {}

    public func process(_ input: String) async throws -> Result {
        // Implementation
        Result(value: input)
    }
}

/// Result type
public struct Result {
    public let value: String

    public init(value: String) {
        self.value = value
    }
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
        try await super.setUp()
        service = MyService()
    }

    override func tearDown() async throws {
        service = nil
        try await super.tearDown()
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
        } catch MyError.invalidInput {
            // Expected
        } catch {
            XCTFail("Wrong error type: \(error)")
        }
    }
}
```

### Performance Testing

```swift
func testPerformance() {
    measure {
        for _ in 0..<1000 {
            _ = service.process("test")
        }
    }
}

func testAsyncPerformance() async throws {
    await measureAsync {
        for _ in 0..<100 {
            _ = try? await service.fetchData()
        }
    }
}

@available(iOS 16.0, macOS 13.0, *)
func measureAsync(_ block: @escaping () async -> Void) async {
    let start = Date()
    await block()
    let duration = Date().timeIntervalSince(start)
    print("Duration: \(duration)s")
}
```

### Test Support Package

```swift
// Sources/MyPackageTestSupport/Mocks.swift
import MyPackage

/// Mock implementation for testing
public final class MockDataSource: DataSource {
    public var mockItems: [Item] = []
    public var shouldThrowError = false

    public init() {}

    public func fetch() async throws -> [Item] {
        if shouldThrowError {
            throw MockError.forcedError
        }
        return mockItems
    }
}

public enum MockError: Error {
    case forcedError
}
```

---

## DocC Documentation

### Catalog Structure

```
Sources/MyPackage/
└── MyPackage.docc/
    ├── MyPackage.md              # Root article
    ├── GettingStarted.md         # Tutorial
    ├── Resources/
    │   └── diagram.png
    └── Tutorials/
        └── BuildingYourFirstApp.tutorial
```

### Root Documentation Article

```markdown
# ``MyPackage``

A comprehensive library for data processing.

## Overview

MyPackage provides a modern, async-first API for processing data from various sources.

## Topics

### Essentials

- ``MyPackage/MyPackage``
- ``Configuration``
- ``DataSource``

### Data Models

- ``User``
- ``Result``

### Services

- ``NetworkService``
- ``CacheService``

### Error Handling

- ``MyError``
```

### Symbol Documentation

```swift
/// Fetches user data from the remote API.
///
/// This function performs an asynchronous network request to retrieve user information.
///
/// - Parameter id: The unique identifier for the user
/// - Returns: A `User` object containing the user's data
/// - Throws: `MyError.notFound` if the user doesn't exist
///          `MyError.networkError` if the network request fails
///
/// ## Example
///
/// ```swift
/// let user = try await fetchUser(id: "user123")
/// print(user.name)
/// ```
///
/// - Important: Requires an active network connection
/// - Note: Results are not cached by default
/// - Warning: Rate limiting may apply for frequent requests
///
/// ## See Also
///
/// - ``fetchUsers(ids:)``
/// - ``UserCache``
public func fetchUser(id: String) async throws -> User {
    // Implementation
    User(id: id, name: "Test")
}
```

### Tutorial Syntax

```markdown
@Tutorial(time: 20) {
    @Intro(title: "Building Your First App") {
        Learn how to integrate MyPackage into your application.

        @Image(source: "hero-image.png", alt: "App screenshot")
    }

    @Section(title: "Setup") {
        @ContentAndMedia {
            Install and configure MyPackage.
        }

        @Steps {
            @Step {
                Add the package dependency.

                @Code(name: "Package.swift", file: "01-add-dependency.swift")
            }

            @Step {
                Import the module.

                @Code(name: "ContentView.swift", file: "02-import.swift")
            }
        }
    }
}
```

---

## Platform Support

### Platform-Specific Code

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

### Feature Detection

```swift
#if swift(>=5.9)
public func modernFeature() {
    // Use Swift 5.9+ features
}
#else
public func modernFeature() {
    fatalError("Requires Swift 5.9 or later")
}
#endif

#if compiler(>=5.9)
// Compiler-specific features
#endif
```

---

## Binary Frameworks & XCFrameworks

### Creating XCFramework

```bash
# Build for iOS device
xcodebuild archive \
  -scheme MyPackage \
  -destination "generic/platform=iOS" \
  -archivePath ./build/ios \
  SKIP_INSTALL=NO \
  BUILD_LIBRARY_FOR_DISTRIBUTION=YES

# Build for iOS simulator
xcodebuild archive \
  -scheme MyPackage \
  -destination "generic/platform=iOS Simulator" \
  -archivePath ./build/ios-sim \
  SKIP_INSTALL=NO \
  BUILD_LIBRARY_FOR_DISTRIBUTION=YES

# Build for macOS
xcodebuild archive \
  -scheme MyPackage \
  -destination "generic/platform=macOS" \
  -archivePath ./build/macos \
  SKIP_INSTALL=NO \
  BUILD_LIBRARY_FOR_DISTRIBUTION=YES

# Create XCFramework
xcodebuild -create-xcframework \
  -framework ./build/ios.xcarchive/Products/Library/Frameworks/MyPackage.framework \
  -framework ./build/ios-sim.xcarchive/Products/Library/Frameworks/MyPackage.framework \
  -framework ./build/macos.xcarchive/Products/Library/Frameworks/MyPackage.framework \
  -output ./MyPackage.xcframework
```

### Distributing Binary Framework

```swift
// Package.swift with binary target
let package = Package(
    name: "MyPackage",
    products: [
        .library(name: "MyPackage", targets: ["MyPackage"]),
    ],
    targets: [
        .binaryTarget(
            name: "MyPackage",
            url: "https://github.com/user/repo/releases/download/1.0.0/MyPackage.xcframework.zip",
            checksum: "abc123..."
        ),
    ]
)
```

---

## Dependency Management

### Version Requirements

```swift
dependencies: [
    // Exact version
    .package(url: "https://github.com/user/repo.git", exact: "1.0.0"),

    // Version range
    .package(url: "https://github.com/user/repo.git", from: "1.0.0"),
    .package(url: "https://github.com/user/repo.git", "1.0.0"..<"2.0.0"),

    // Branch
    .package(url: "https://github.com/user/repo.git", branch: "main"),

    // Commit
    .package(url: "https://github.com/user/repo.git", revision: "abc123"),

    // Local path (for development)
    .package(path: "../LocalPackage"),
]
```

### Conditional Dependencies

```swift
var dependencies: [Package.Dependency] = [
    .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),
]

#if os(Linux)
dependencies.append(
    .package(url: "https://github.com/swift-server/async-http-client.git", from: "1.0.0")
)
#endif

let package = Package(
    name: "MyPackage",
    dependencies: dependencies,
    // ...
)
```

---

## Publishing Best Practices

### Pre-publish Checklist

- [ ] All tests pass (`swift test`)
- [ ] Documentation builds (`swift package generate-documentation`)
- [ ] No compiler warnings
- [ ] README.md is comprehensive
- [ ] LICENSE file included
- [ ] Version tagged in git
- [ ] CHANGELOG.md updated
- [ ] All platforms tested
- [ ] Example projects work
- [ ] API is stable and well-designed

### Versioning Strategy

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Breaking API change | Major | 1.0.0 → 2.0.0 |
| New feature (backward compatible) | Minor | 1.0.0 → 1.1.0 |
| Bug fix | Patch | 1.0.0 → 1.0.1 |

### README Template

```markdown
# MyPackage

Brief description of the package.

## Features

- Feature 1
- Feature 2
- Feature 3

## Requirements

- iOS 16.0+ / macOS 13.0+
- Swift 5.9+

## Installation

### Swift Package Manager

```swift
dependencies: [
    .package(url: "https://github.com/user/MyPackage.git", from: "1.0.0")
]
```

## Usage

```swift
import MyPackage

let config = Configuration()
let result = try await MyPackage().process("input")
```

## Documentation

Full documentation available at [https://user.github.io/MyPackage](https://user.github.io/MyPackage)

## License

MIT License
```

---

## Common Dependencies

### Logging

```swift
dependencies: [
    .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),
]

// Usage
import Logging

let logger = Logger(label: "com.example.mypackage")
logger.info("Processing started")
```

### Async/Concurrency

```swift
dependencies: [
    .package(url: "https://github.com/apple/swift-async-algorithms.git", from: "1.0.0"),
]

// Provides AsyncSequence utilities
```

### Argument Parsing (for CLIs)

```swift
dependencies: [
    .package(url: "https://github.com/apple/swift-argument-parser.git", from: "1.3.0"),
]
```

### Testing

```swift
dependencies: [
    .package(url: "https://github.com/pointfreeco/swift-snapshot-testing.git", from: "1.15.0"),
]
```

---

## Anti-Patterns

### 1. Exposing Implementation Details

```swift
// Bad: Exposes Foundation types unnecessarily
public func getData() -> [String: Any]

// Good: Return domain type
public func getData() -> Configuration
```

### 2. Using Classes When Structs Suffice

```swift
// Bad: Unnecessary reference type
public class Configuration {
    public var timeout: Int
}

// Good: Value type with value semantics
public struct Configuration {
    public var timeout: Int
}
```

### 3. Force Unwrapping in Public APIs

```swift
// Bad: Can crash consumer's app
public func process(_ input: String) -> User {
    return try! JSONDecoder().decode(User.self, from: data)
}

// Good: Proper error handling
public func process(_ input: String) throws -> User {
    return try JSONDecoder().decode(User.self, from: data)
}
```

### 4. Missing @available Annotations

```swift
// Bad: Breaks on older platforms
public func modernAPI() {
    // Uses iOS 17 APIs
}

// Good: Properly marked
@available(iOS 17.0, macOS 14.0, *)
public func modernAPI() {
    // Uses iOS 17 APIs
}
```

---

## Troubleshooting

### Package Resolution Issues

**Problem:** `error: package at '...' is using Swift tools version but package is at '...'`

**Solution:** Update `swift-tools-version` in Package.swift header

```swift
// swift-tools-version: 5.9
```

### Missing Module Errors

**Problem:** `error: no such module 'MyPackage'`

**Solution:** Ensure target dependencies are correctly specified

```swift
.testTarget(
    name: "MyPackageTests",
    dependencies: ["MyPackage"]  // Add module dependency
)
```

### Xcode Build Issues

**Problem:** Xcode can't find package

**Solution:**
1. Delete derived data
2. `File > Packages > Reset Package Caches`
3. `swift package resolve`

---

## References

- `meta-library-dev` - Foundational library patterns
- `lang-swift-dev` - Swift language fundamentals
- [Swift Package Manager Documentation](https://www.swift.org/package-manager/)
- [DocC Documentation](https://www.swift.org/documentation/docc/)
- [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)
