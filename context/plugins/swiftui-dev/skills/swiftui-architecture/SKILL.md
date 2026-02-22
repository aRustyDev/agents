# SwiftUI Architecture Patterns

## Purpose

Architecture patterns for SwiftUI applications including MVVM, navigation, dependency injection, and the @Observable macro.

## Patterns

### MVVM with @Observable

```swift
import SwiftUI

// ViewModel using @Observable macro (iOS 17+/macOS 14+)
@Observable
final class ContentViewModel {
    var items: [Item] = []
    var isLoading = false
    var errorMessage: String?

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
            errorMessage = error.localizedDescription
        }
    }
}

// View
struct ContentView: View {
    @State private var viewModel = ContentViewModel()

    var body: some View {
        List(viewModel.items) { item in
            ItemRow(item: item)
        }
        .overlay {
            if viewModel.isLoading {
                ProgressView()
            }
        }
        .task {
            await viewModel.loadItems()
        }
    }
}
```

### Dependency Injection

```swift
// Protocol-based dependency
protocol ItemRepository: Sendable {
    func fetchAll() async throws -> [Item]
    func save(_ item: Item) async throws
}

// Live implementation
struct LiveItemRepository: ItemRepository {
    func fetchAll() async throws -> [Item] {
        // Real implementation
    }

    func save(_ item: Item) async throws {
        // Real implementation
    }
}

// Mock for testing
struct MockItemRepository: ItemRepository {
    var items: [Item] = []
    var shouldFail = false

    func fetchAll() async throws -> [Item] {
        if shouldFail { throw TestError.fetchFailed }
        return items
    }

    func save(_ item: Item) async throws {
        // Mock save
    }
}

// Static factory pattern
extension ItemRepository where Self == LiveItemRepository {
    static var live: LiveItemRepository { LiveItemRepository() }
}

extension ItemRepository where Self == MockItemRepository {
    static var mock: MockItemRepository { MockItemRepository() }
}
```

### Navigation with NavigationStack

```swift
// Type-safe navigation paths
enum NavigationDestination: Hashable {
    case detail(Item)
    case settings
    case profile(userId: String)
}

struct RootView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            ContentView(path: $path)
                .navigationDestination(for: NavigationDestination.self) { destination in
                    switch destination {
                    case .detail(let item):
                        ItemDetailView(item: item)
                    case .settings:
                        SettingsView()
                    case .profile(let userId):
                        ProfileView(userId: userId)
                    }
                }
        }
    }
}
```

### Environment-based Dependencies

```swift
// Environment key for repository
private struct ItemRepositoryKey: EnvironmentKey {
    static let defaultValue: any ItemRepository = LiveItemRepository()
}

extension EnvironmentValues {
    var itemRepository: any ItemRepository {
        get { self[ItemRepositoryKey.self] }
        set { self[ItemRepositoryKey.self] = newValue }
    }
}

// Usage in view
struct ItemListView: View {
    @Environment(\.itemRepository) private var repository
    @State private var items: [Item] = []

    var body: some View {
        List(items) { item in
            Text(item.name)
        }
        .task {
            items = try? await repository.fetchAll() ?? []
        }
    }
}

// Preview with mock
#Preview {
    ItemListView()
        .environment(\.itemRepository, MockItemRepository(items: .preview))
}
```

## File Organization

```text
MyApp/
├── App/
│   ├── MyApp.swift
│   └── AppDelegate.swift
├── Features/
│   ├── Items/
│   │   ├── Views/
│   │   │   ├── ItemListView.swift
│   │   │   └── ItemDetailView.swift
│   │   ├── ViewModels/
│   │   │   └── ItemViewModel.swift
│   │   └── Models/
│   │       └── Item.swift
│   └── Settings/
│       └── ...
├── Core/
│   ├── Repositories/
│   │   └── ItemRepository.swift
│   ├── Services/
│   │   └── NetworkService.swift
│   └── Extensions/
│       └── View+Extensions.swift
└── Resources/
    └── Assets.xcassets
```

## Best Practices

1. **Use @Observable for ViewModels** - Simpler than ObservableObject
2. **Inject dependencies via init** - Enables testing
3. **Use NavigationStack for navigation** - Type-safe, deep-linkable
4. **Keep views small** - Extract subviews early
5. **Use task modifier for async** - Proper lifecycle management

## Related Skills

- swiftui-data-flow: State management details
- swiftui-testing: Testing these patterns
- swift-concurrency: Async/await patterns
