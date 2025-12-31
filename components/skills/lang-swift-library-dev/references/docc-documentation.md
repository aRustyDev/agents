# DocC Documentation

Comprehensive guide for documenting Swift packages with DocC.

## Catalog Structure

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

## Root Documentation Article

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

## Symbol Documentation

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

## Tutorial Syntax

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

## Building Documentation

```bash
# Generate documentation
swift package generate-documentation

# Preview in browser
swift package preview-documentation

# Export static site
swift package generate-documentation --output-path ./docs
```

## Callout Syntax

| Callout | Usage |
|---------|-------|
| `- Note:` | Additional information |
| `- Important:` | Critical information |
| `- Warning:` | Potential problems |
| `- Tip:` | Helpful suggestions |
| `- Experiment:` | Encourage exploration |

## Article Linking

```markdown
# Internal links
See ``MyPackage/Configuration`` for settings.

# External links
Visit [Swift.org](https://swift.org)

# Tutorial links
Start with <doc:GettingStarted>
```
