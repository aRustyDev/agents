# SwiftUI View Output Style

Format SwiftUI view code with proper structure and previews.

## View Structure

```swift
import SwiftUI

struct <Name>View: View {
    // MARK: - Properties

    @State private var ...
    @Environment(\...) private var ...
    let ...

    // MARK: - Body

    var body: some View {
        // View content
    }
}

// MARK: - Subviews

private extension <Name>View {
    var headerView: some View {
        // ...
    }
}

// MARK: - Preview

#Preview {
    <Name>View()
}

#Preview("Dark Mode") {
    <Name>View()
        .preferredColorScheme(.dark)
}
```

## Best Practices

1. Extract complex subviews to computed properties
2. Use `private` for internal state
3. Include multiple preview variants (light/dark, sizes)
4. Add accessibility modifiers
5. Use MARK comments for organization
