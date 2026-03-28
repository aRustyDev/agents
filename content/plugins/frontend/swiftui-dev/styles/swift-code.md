# Swift Code Output Style

Format Swift code output with proper conventions.

## Formatting Rules

1. **Indentation**: 4 spaces
2. **Line length**: 120 characters max
3. **Braces**: Same line for opening
4. **Imports**: Sorted alphabetically, Foundation/SwiftUI first

## Structure

```swift
import Foundation
import SwiftUI

// MARK: - Type Definition

struct/class/enum Name {
    // MARK: - Properties

    // MARK: - Init

    // MARK: - Methods
}

// MARK: - Extensions

extension Name {
    // ...
}

// MARK: - Preview

#Preview {
    // ...
}
```

## Naming Conventions

- Types: PascalCase (`ItemViewModel`)
- Properties/methods: camelCase (`loadItems()`)
- Constants: camelCase (`let maxItems = 100`)
- Protocols: PascalCase, often `-able` or `-ing` suffix
