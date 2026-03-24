---
name: swiftui-data-flow
description: SwiftUI data flow mechanisms including @Observable, @State, @Binding, and environment values
tags: [swift, swiftui, data-flow, state-management, observable]
---

# SwiftUI Data Flow

## Purpose

Understanding SwiftUI's data flow mechanisms including @Observable, @State, @Binding, and environment values.

## Property Wrappers

### @State - Local View State

```swift
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        VStack {
            Text("Count: \(count)")
            Button("Increment") {
                count += 1
            }
        }
    }
}
```

### @Binding - Two-Way Connection

```swift
struct ToggleRow: View {
    let title: String
    @Binding var isOn: Bool

    var body: some View {
        Toggle(title, isOn: $isOn)
    }
}

struct SettingsView: View {
    @State private var notificationsEnabled = false

    var body: some View {
        Form {
            ToggleRow(title: "Notifications", isOn: $notificationsEnabled)
        }
    }
}
```

### @Observable (iOS 17+/macOS 14+)

```swift
@Observable
final class UserSettings {
    var username = ""
    var notificationsEnabled = true
    var theme: Theme = .system

    // Computed properties work automatically
    var isValid: Bool {
        !username.isEmpty
    }
}

struct SettingsView: View {
    @State private var settings = UserSettings()

    var body: some View {
        Form {
            TextField("Username", text: $settings.username)
            Toggle("Notifications", isOn: $settings.notificationsEnabled)
            Picker("Theme", selection: $settings.theme) {
                ForEach(Theme.allCases) { theme in
                    Text(theme.rawValue).tag(theme)
                }
            }
        }
        .disabled(!settings.isValid)
    }
}
```

### @Bindable - Bindings from @Observable

```swift
struct EditUserView: View {
    @Bindable var user: User  // User is @Observable

    var body: some View {
        Form {
            TextField("Name", text: $user.name)
            TextField("Email", text: $user.email)
        }
    }
}
```

### @Environment - System Values

```swift
struct AdaptiveView: View {
    @Environment(\.colorScheme) private var colorScheme
    @Environment(\.horizontalSizeClass) private var sizeClass
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack {
            Text("Theme: \(colorScheme == .dark ? "Dark" : "Light")")

            Button("Close") {
                dismiss()
            }
        }
    }
}
```

### Custom Environment Values

```swift
// Define the key
private struct APIClientKey: EnvironmentKey {
    static let defaultValue: APIClient = .live
}

// Extend EnvironmentValues
extension EnvironmentValues {
    var apiClient: APIClient {
        get { self[APIClientKey.self] }
        set { self[APIClientKey.self] = newValue }
    }
}

// Usage
struct DataView: View {
    @Environment(\.apiClient) private var api

    var body: some View {
        // Use api
    }
}

// Injection
MyApp()
    .environment(\.apiClient, .mock)
```

### @Environment with @Observable

```swift
@Observable
final class AppState {
    var currentUser: User?
    var isAuthenticated: Bool { currentUser != nil }
}

// In App
@main
struct MyApp: App {
    @State private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(appState)
        }
    }
}

// In View
struct ProfileView: View {
    @Environment(AppState.self) private var appState

    var body: some View {
        if let user = appState.currentUser {
            Text("Hello, \(user.name)")
        }
    }
}
```

## Data Flow Patterns

### Parent to Child

```swift
struct ParentView: View {
    @State private var data = [Item]()

    var body: some View {
        List(data) { item in
            ChildRow(item: item)  // Pass as value
        }
    }
}
```

### Child to Parent (Binding)

```swift
struct FilterView: View {
    @Binding var selectedFilter: Filter

    var body: some View {
        Picker("Filter", selection: $selectedFilter) {
            ForEach(Filter.allCases) { filter in
                Text(filter.title).tag(filter)
            }
        }
    }
}
```

### Child to Parent (Closure)

```swift
struct ItemRow: View {
    let item: Item
    let onDelete: () -> Void

    var body: some View {
        HStack {
            Text(item.name)
            Spacer()
            Button("Delete", action: onDelete)
        }
    }
}
```

### Shared State via @Observable

```swift
@Observable
final class ShoppingCart {
    var items: [CartItem] = []

    var total: Decimal {
        items.reduce(0) { $0 + $1.price * Decimal($1.quantity) }
    }

    func add(_ product: Product) {
        if let index = items.firstIndex(where: { $0.productId == product.id }) {
            items[index].quantity += 1
        } else {
            items.append(CartItem(product: product))
        }
    }
}

// Shared across views via environment
struct ProductView: View {
    @Environment(ShoppingCart.self) private var cart
    let product: Product

    var body: some View {
        Button("Add to Cart") {
            cart.add(product)
        }
    }
}
```

## Best Practices

1. **Use @State for simple local state**
2. **Use @Observable for shared/complex state** (iOS 17+)
3. **Pass data down, actions up**
4. **Prefer @Environment for dependency injection**
5. **Use @Binding sparingly** - prefer closures for actions

## Migration from ObservableObject

```swift
// OLD (pre-iOS 17)
class ViewModel: ObservableObject {
    @Published var items: [Item] = []
}

struct MyView: View {
    @StateObject private var viewModel = ViewModel()
}

// NEW (iOS 17+)
@Observable
final class ViewModel {
    var items: [Item] = []
}

struct MyView: View {
    @State private var viewModel = ViewModel()
}
```

## Related Skills

- swiftui-architecture: Overall patterns
- swift-concurrency: Async data flow
