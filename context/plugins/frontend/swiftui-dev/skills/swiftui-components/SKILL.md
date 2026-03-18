# SwiftUI Components & Layouts

## Purpose

Reference for SwiftUI's built-in components, layout tools, and visual styling for creating polished, iOS-native interfaces.

## Layout Containers

### Stack Views

```swift
// Vertical stack
VStack(alignment: .leading, spacing: 12) {
    Text("Title")
        .font(.headline)
    Text("Subtitle")
        .font(.subheadline)
        .foregroundStyle(.secondary)
}

// Horizontal stack
HStack(spacing: 16) {
    Image(systemName: "star.fill")
    Text("Featured")
    Spacer()
    Text("5.0")
}

// Layered stack (back to front)
ZStack(alignment: .bottomTrailing) {
    Image("photo")
        .resizable()
        .aspectRatio(contentMode: .fill)

    Text("New")
        .padding(8)
        .background(.red)
        .clipShape(Capsule())
        .padding(8)
}
```

### Lazy Grids

```swift
// Adaptive grid - columns adjust to fit
let adaptiveColumns = [
    GridItem(.adaptive(minimum: 150, maximum: 200))
]

LazyVGrid(columns: adaptiveColumns, spacing: 16) {
    ForEach(items) { item in
        ItemCard(item: item)
    }
}

// Fixed grid - explicit column count
let fixedColumns = [
    GridItem(.flexible()),
    GridItem(.flexible()),
    GridItem(.flexible())
]

LazyVGrid(columns: fixedColumns, spacing: 12) {
    ForEach(items) { item in
        ItemThumbnail(item: item)
    }
}

// Horizontal grid
let rows = [GridItem(.fixed(100)), GridItem(.fixed(100))]

LazyHGrid(rows: rows, spacing: 16) {
    ForEach(items) { item in
        ItemRow(item: item)
    }
}
```

### GeometryReader

```swift
struct ResponsiveCard: View {
    var body: some View {
        GeometryReader { geometry in
            HStack(spacing: 0) {
                // Left side takes 1/3
                Image("thumbnail")
                    .resizable()
                    .frame(width: geometry.size.width * 0.33)

                // Right side takes 2/3
                VStack(alignment: .leading) {
                    Text("Title")
                    Text("Description")
                }
                .frame(maxWidth: .infinity)
                .padding()
            }
        }
        .frame(height: 120)
    }
}

// Reading safe area
GeometryReader { geometry in
    VStack {
        Text("Top inset: \(geometry.safeAreaInsets.top)")
    }
}
```

### ViewThatFits

```swift
// Automatically chooses layout that fits
ViewThatFits {
    // Try horizontal first
    HStack {
        Image(systemName: "star")
        Text("Long descriptive label")
        Text("Details")
    }

    // Fall back to vertical if horizontal doesn't fit
    VStack {
        Image(systemName: "star")
        Text("Long descriptive label")
        Text("Details")
    }
}
```

## Built-in Components

### Lists

```swift
List {
    // Simple rows
    ForEach(items) { item in
        Text(item.name)
    }

    // Sections
    Section("Favorites") {
        ForEach(favorites) { item in
            ItemRow(item: item)
        }
    }

    Section("Recent") {
        ForEach(recent) { item in
            ItemRow(item: item)
        }
    }
}
.listStyle(.insetGrouped)  // iOS-style grouped list

// Swipe actions
List {
    ForEach(items) { item in
        ItemRow(item: item)
            .swipeActions(edge: .trailing) {
                Button(role: .destructive) {
                    delete(item)
                } label: {
                    Label("Delete", systemImage: "trash")
                }
            }
            .swipeActions(edge: .leading) {
                Button {
                    toggleFavorite(item)
                } label: {
                    Label("Favorite", systemImage: "star")
                }
                .tint(.yellow)
            }
    }
}
```

### Navigation

```swift
// Tab-based navigation
TabView {
    HomeView()
        .tabItem {
            Label("Home", systemImage: "house")
        }

    SearchView()
        .tabItem {
            Label("Search", systemImage: "magnifyingglass")
        }

    ProfileView()
        .tabItem {
            Label("Profile", systemImage: "person")
        }
}

// Stack-based navigation (iOS 16+)
NavigationStack {
    List(items) { item in
        NavigationLink(value: item) {
            ItemRow(item: item)
        }
    }
    .navigationTitle("Items")
    .navigationDestination(for: Item.self) { item in
        ItemDetailView(item: item)
    }
}

// Split view (iPad/Mac)
NavigationSplitView {
    List(categories, selection: $selectedCategory) { category in
        Text(category.name)
    }
} detail: {
    if let category = selectedCategory {
        CategoryDetailView(category: category)
    } else {
        Text("Select a category")
    }
}
```

### Forms & Controls

```swift
Form {
    Section("Account") {
        TextField("Username", text: $username)
        SecureField("Password", text: $password)
    }

    Section("Preferences") {
        Toggle("Notifications", isOn: $notificationsEnabled)

        Picker("Theme", selection: $theme) {
            Text("System").tag(Theme.system)
            Text("Light").tag(Theme.light)
            Text("Dark").tag(Theme.dark)
        }

        Stepper("Font Size: \(fontSize)", value: $fontSize, in: 12...24)

        Slider(value: $volume, in: 0...100) {
            Text("Volume")
        }
    }

    Section {
        DatePicker("Date", selection: $date, displayedComponents: .date)

        ColorPicker("Accent Color", selection: $accentColor)
    }
}
```

### SF Symbols

```swift
// Basic usage
Image(systemName: "star.fill")

// With configuration
Image(systemName: "heart.fill")
    .symbolRenderingMode(.multicolor)
    .font(.title)

// Variable value (iOS 16+)
Image(systemName: "speaker.wave.3.fill", variableValue: volume)

// Symbol effects (iOS 17+)
Image(systemName: "wifi")
    .symbolEffect(.variableColor.iterative)

Image(systemName: "arrow.down.circle")
    .symbolEffect(.bounce, value: downloadStarted)

// In labels
Label("Downloads", systemImage: "arrow.down.circle")
    .labelStyle(.titleAndIcon)
```

## Visual Styling

### Shadows & Depth

```swift
// Drop shadow
Text("Elevated")
    .padding()
    .background(.white)
    .clipShape(RoundedRectangle(cornerRadius: 12))
    .shadow(color: .black.opacity(0.1), radius: 8, x: 0, y: 4)

// Inner shadow effect
RoundedRectangle(cornerRadius: 12)
    .fill(.white)
    .overlay(
        RoundedRectangle(cornerRadius: 12)
            .stroke(.gray.opacity(0.2), lineWidth: 1)
    )
```

### Gradients

```swift
// Linear gradient
Rectangle()
    .fill(
        LinearGradient(
            colors: [.blue, .purple],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
    )

// Radial gradient
Circle()
    .fill(
        RadialGradient(
            colors: [.yellow, .orange],
            center: .center,
            startRadius: 0,
            endRadius: 100
        )
    )

// Angular gradient
Circle()
    .fill(
        AngularGradient(
            colors: [.red, .yellow, .green, .blue, .purple, .red],
            center: .center
        )
    )

// Mesh gradient (iOS 18+)
MeshGradient(
    width: 3, height: 3,
    points: [
        [0, 0], [0.5, 0], [1, 0],
        [0, 0.5], [0.5, 0.5], [1, 0.5],
        [0, 1], [0.5, 1], [1, 1]
    ],
    colors: [
        .red, .orange, .yellow,
        .green, .blue, .purple,
        .pink, .cyan, .mint
    ]
)
```

### Blur & Materials

```swift
// Background blur
ZStack {
    Image("background")
        .resizable()

    VStack {
        Text("Content")
    }
    .padding()
    .background(.ultraThinMaterial)
    .clipShape(RoundedRectangle(cornerRadius: 16))
}

// Material options: .regularMaterial, .thinMaterial, .ultraThinMaterial,
//                   .thickMaterial, .ultraThickMaterial, .bar

// Custom blur
Image("photo")
    .blur(radius: 10)
```

### Custom Shapes

```swift
// Built-in shapes
Circle()
Ellipse()
Rectangle()
RoundedRectangle(cornerRadius: 12)
Capsule()
UnevenRoundedRectangle(
    topLeadingRadius: 20,
    bottomLeadingRadius: 0,
    bottomTrailingRadius: 0,
    topTrailingRadius: 20
)

// Custom shape
struct Triangle: Shape {
    func path(in rect: CGRect) -> Path {
        Path { path in
            path.move(to: CGPoint(x: rect.midX, y: rect.minY))
            path.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY))
            path.addLine(to: CGPoint(x: rect.minX, y: rect.maxY))
            path.closeSubpath()
        }
    }
}

// Usage
Triangle()
    .fill(.blue)
    .frame(width: 100, height: 100)
```

## Animations

### Basic Animations

```swift
struct AnimatedButton: View {
    @State private var isPressed = false

    var body: some View {
        Button("Tap Me") {
            // Action
        }
        .scaleEffect(isPressed ? 0.95 : 1.0)
        .animation(.spring(response: 0.3, dampingFraction: 0.6), value: isPressed)
        .onLongPressGesture(minimumDuration: .infinity, pressing: { pressing in
            isPressed = pressing
        }, perform: {})
    }
}
```

### Transitions

```swift
struct ContentView: View {
    @State private var showDetails = false

    var body: some View {
        VStack {
            Button("Toggle") {
                withAnimation(.spring) {
                    showDetails.toggle()
                }
            }

            if showDetails {
                DetailView()
                    .transition(.asymmetric(
                        insertion: .scale.combined(with: .opacity),
                        removal: .slide
                    ))
            }
        }
    }
}
```

### Matched Geometry Effect

```swift
struct HeroAnimation: View {
    @Namespace private var animation
    @State private var isExpanded = false

    var body: some View {
        VStack {
            if isExpanded {
                ExpandedCard(namespace: animation)
            } else {
                CompactCard(namespace: animation)
            }
        }
        .onTapGesture {
            withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) {
                isExpanded.toggle()
            }
        }
    }
}

struct CompactCard: View {
    var namespace: Namespace.ID

    var body: some View {
        RoundedRectangle(cornerRadius: 12)
            .fill(.blue)
            .matchedGeometryEffect(id: "card", in: namespace)
            .frame(width: 100, height: 100)
    }
}
```

### Phase Animator (iOS 17+)

```swift
struct PulsingDot: View {
    var body: some View {
        Circle()
            .fill(.blue)
            .frame(width: 20, height: 20)
            .phaseAnimator([false, true]) { content, phase in
                content
                    .scaleEffect(phase ? 1.2 : 1.0)
                    .opacity(phase ? 0.7 : 1.0)
            } animation: { _ in
                .easeInOut(duration: 0.8)
            }
    }
}
```

## Best Practices

1. **Use semantic colors** - `.primary`, `.secondary`, `.background`
2. **Prefer built-in components** - Match platform conventions
3. **Use SF Symbols** - Consistent, scalable iconography
4. **Test on multiple sizes** - iPhone SE to iPad Pro
5. **Support Dark Mode** - Use adaptive colors and materials
6. **Animate state changes** - Smooth transitions improve UX

## Related Skills

- swiftui-architecture: Overall app structure
- swiftui-gestures: User interactions
- swiftui-data-flow: State management
