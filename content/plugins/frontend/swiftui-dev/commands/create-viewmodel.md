# Create ViewModel

Generate an @Observable ViewModel with dependency injection support.

## Arguments

- `<name>` - ViewModel name (e.g., `ItemList` creates `ItemListViewModel`)
- `--path <path>` - Target directory (default: current directory)
- `--repository <name>` - Include repository dependency
- `--async` - Include async loading methods

## Output

Creates `<Name>ViewModel.swift` with:

- @Observable class
- Dependency injection via init
- Error handling
- Loading state

## Template

```swift
import Foundation

@Observable
final class <Name>ViewModel {
    // MARK: - State

    var items: [Item] = []
    var isLoading = false
    var error: Error?

    // MARK: - Dependencies

    private let repository: ItemRepository

    // MARK: - Init

    init(repository: ItemRepository = .live) {
        self.repository = repository
    }

    // MARK: - Actions

    func load() async {
        isLoading = true
        defer { isLoading = false }

        do {
            items = try await repository.fetchAll()
            error = nil
        } catch {
            self.error = error
        }
    }
}
```

## Examples

```bash
# Basic ViewModel
/create-viewmodel ItemList

# With repository dependency
/create-viewmodel ItemDetail --repository ItemRepository

# With async methods
/create-viewmodel Dashboard --async

# In specific path
/create-viewmodel Settings --path Features/Settings/ViewModels
```

## Generated Patterns

### With Repository

```swift
@Observable
final class ItemListViewModel {
    var items: [Item] = []
    var isLoading = false
    var error: Error?

    private let repository: ItemRepository

    init(repository: ItemRepository = .live) {
        self.repository = repository
    }

    func loadItems() async {
        isLoading = true
        defer { isLoading = false }

        do {
            items = try await repository.fetchAll()
        } catch {
            self.error = error
        }
    }

    func deleteItem(_ item: Item) async {
        do {
            try await repository.delete(item)
            items.removeAll { $0.id == item.id }
        } catch {
            self.error = error
        }
    }
}
```

### For Testing

```swift
// In tests
let mockRepo = MockItemRepository(items: [.preview])
let viewModel = ItemListViewModel(repository: mockRepo)

await viewModel.loadItems()
XCTAssertEqual(viewModel.items.count, 1)
```
