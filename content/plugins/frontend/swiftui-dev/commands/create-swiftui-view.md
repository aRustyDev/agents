# Create SwiftUI View

Generate a new SwiftUI view with proper structure, accessibility, and preview providers.

## Arguments

- `<name>` - View name in PascalCase (e.g., `ItemDetailView`)
- `--path <path>` - Target directory (default: current directory)
- `--observable` - Include @Observable ViewModel
- `--list` - Generate a List-based view
- `--form` - Generate a Form-based view

## Output

Creates `<Name>.swift` with:

- View struct with body
- Preview provider with sample data
- ViewModel if `--observable` specified

## Template

```swift
import SwiftUI

struct <Name>View: View {
    // MARK: - Properties

    // MARK: - Body

    var body: some View {
        <content>
    }
}

// MARK: - Subviews

private extension <Name>View {
    // Extract complex subviews here
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

## Examples

```bash
# Basic view
/create-swiftui-view ItemRow

# View with ViewModel
/create-swiftui-view ItemDetail --observable

# List view
/create-swiftui-view ItemList --list --observable

# Form view in specific path
/create-swiftui-view SettingsForm --form --path Features/Settings/Views
```

## Generated Code Patterns

### Basic View

```swift
struct ItemRowView: View {
    let item: Item

    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text(item.name)
                    .font(.headline)
                Text(item.description)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
            Spacer()
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(item.name), \(item.description)")
    }
}
```

### With ViewModel

```swift
@Observable
final class ItemDetailViewModel {
    var item: Item
    var isLoading = false
    var error: Error?

    init(item: Item) {
        self.item = item
    }

    func refresh() async {
        // Implement refresh logic
    }
}

struct ItemDetailView: View {
    @State private var viewModel: ItemDetailViewModel

    init(item: Item) {
        _viewModel = State(initialValue: ItemDetailViewModel(item: item))
    }

    var body: some View {
        // View content
    }
}
```
