# SwiftUI Gestures & Interactions

## Purpose

Implementing touch interactions, gestures, and haptic feedback in SwiftUI for engaging, responsive user experiences.

## Basic Gestures

### Tap Gesture

```swift
// Single tap
Text("Tap me")
    .onTapGesture {
        print("Tapped!")
    }

// Double tap
Image("photo")
    .onTapGesture(count: 2) {
        toggleZoom()
    }

// Tap with location
Color.blue
    .frame(width: 200, height: 200)
    .onTapGesture { location in
        print("Tapped at: \(location)")
    }
```

### Long Press

```swift
struct LongPressButton: View {
    @State private var isPressed = false

    var body: some View {
        Circle()
            .fill(isPressed ? .red : .blue)
            .frame(width: 100, height: 100)
            .onLongPressGesture(minimumDuration: 0.5) {
                // Completed long press
                performAction()
            } onPressingChanged: { pressing in
                withAnimation(.easeInOut(duration: 0.2)) {
                    isPressed = pressing
                }
            }
    }
}
```

### Drag Gesture

```swift
struct DraggableCard: View {
    @State private var offset = CGSize.zero
    @State private var isDragging = false

    var body: some View {
        RoundedRectangle(cornerRadius: 16)
            .fill(.blue)
            .frame(width: 150, height: 100)
            .offset(offset)
            .scaleEffect(isDragging ? 1.05 : 1.0)
            .gesture(
                DragGesture()
                    .onChanged { value in
                        offset = value.translation
                        isDragging = true
                    }
                    .onEnded { value in
                        withAnimation(.spring) {
                            offset = .zero
                            isDragging = false
                        }
                    }
            )
    }
}

// Drag with velocity (swipe to dismiss)
struct SwipeToDismiss: View {
    @State private var offset = CGSize.zero
    @Binding var isPresented: Bool

    var body: some View {
        ContentView()
            .offset(y: offset.height)
            .gesture(
                DragGesture()
                    .onChanged { value in
                        if value.translation.height > 0 {
                            offset = value.translation
                        }
                    }
                    .onEnded { value in
                        if value.translation.height > 100 ||
                           value.predictedEndTranslation.height > 300 {
                            withAnimation {
                                isPresented = false
                            }
                        } else {
                            withAnimation(.spring) {
                                offset = .zero
                            }
                        }
                    }
            )
    }
}
```

### Magnification (Pinch)

```swift
struct ZoomableImage: View {
    @State private var scale: CGFloat = 1.0
    @State private var lastScale: CGFloat = 1.0

    var body: some View {
        Image("photo")
            .resizable()
            .scaledToFit()
            .scaleEffect(scale)
            .gesture(
                MagnificationGesture()
                    .onChanged { value in
                        scale = lastScale * value
                    }
                    .onEnded { value in
                        lastScale = scale
                        // Clamp scale
                        if scale < 1 {
                            withAnimation(.spring) {
                                scale = 1
                                lastScale = 1
                            }
                        } else if scale > 4 {
                            withAnimation(.spring) {
                                scale = 4
                                lastScale = 4
                            }
                        }
                    }
            )
    }
}
```

### Rotation

```swift
struct RotatableView: View {
    @State private var angle: Angle = .zero
    @State private var lastAngle: Angle = .zero

    var body: some View {
        Image(systemName: "arrow.up")
            .font(.system(size: 60))
            .rotationEffect(angle)
            .gesture(
                RotationGesture()
                    .onChanged { value in
                        angle = lastAngle + value
                    }
                    .onEnded { value in
                        lastAngle = angle
                    }
            )
    }
}
```

## Gesture Composition

### Simultaneous Gestures

```swift
// Pinch and rotate at the same time
struct TransformableView: View {
    @State private var scale: CGFloat = 1.0
    @State private var angle: Angle = .zero

    var body: some View {
        Image("photo")
            .scaleEffect(scale)
            .rotationEffect(angle)
            .gesture(
                MagnificationGesture()
                    .onChanged { scale = $0 }
                    .simultaneously(with:
                        RotationGesture()
                            .onChanged { angle = $0 }
                    )
            )
    }
}
```

### Sequential Gestures

```swift
// Long press then drag
struct LongPressDraggable: View {
    @State private var offset = CGSize.zero
    @State private var isActive = false

    var body: some View {
        Circle()
            .fill(isActive ? .green : .blue)
            .frame(width: 100, height: 100)
            .offset(offset)
            .gesture(
                LongPressGesture(minimumDuration: 0.3)
                    .onEnded { _ in
                        isActive = true
                    }
                    .sequenced(before:
                        DragGesture()
                            .onChanged { offset = $0.translation }
                            .onEnded { _ in
                                withAnimation {
                                    offset = .zero
                                    isActive = false
                                }
                            }
                    )
            )
    }
}
```

### Exclusive Gestures

```swift
// Only one gesture recognized
struct ExclusiveGestureView: View {
    var body: some View {
        Rectangle()
            .gesture(
                TapGesture(count: 2)
                    .onEnded { handleDoubleTap() }
                    .exclusively(before:
                        TapGesture()
                            .onEnded { handleSingleTap() }
                    )
            )
    }
}
```

### High Priority Gestures

```swift
// Parent gesture takes priority
struct ParentGestureView: View {
    var body: some View {
        VStack {
            Button("Child Button") {
                print("Button tapped")
            }
        }
        .frame(width: 200, height: 200)
        .background(.gray.opacity(0.2))
        .highPriorityGesture(
            TapGesture()
                .onEnded { print("Parent tapped") }
        )
    }
}
```

## Haptic Feedback

### UIKit Haptics

```swift
struct HapticButton: View {
    var body: some View {
        Button("Tap for Haptic") {
            // Impact feedback
            let impact = UIImpactFeedbackGenerator(style: .medium)
            impact.impactOccurred()
        }
    }
}

// Different feedback types
func triggerHaptics() {
    // Impact - for collisions
    let impact = UIImpactFeedbackGenerator(style: .light)  // .light, .medium, .heavy, .soft, .rigid
    impact.impactOccurred()

    // Selection - for selection changes
    let selection = UISelectionFeedbackGenerator()
    selection.selectionChanged()

    // Notification - for success/warning/error
    let notification = UINotificationFeedbackGenerator()
    notification.notificationOccurred(.success)  // .success, .warning, .error
}
```

### Sensory Feedback (iOS 17+)

```swift
struct ModernHapticView: View {
    @State private var value = 0

    var body: some View {
        Button("Increment") {
            value += 1
        }
        .sensoryFeedback(.increase, trigger: value)
    }
}

// Available feedback types:
// .success, .warning, .error
// .selection
// .increase, .decrease
// .start, .stop
// .alignment, .levelChange
// .impact(weight:intensity:), .impact(flexibility:intensity:)
```

### Haptic Patterns

```swift
// Prepare haptics for responsive feedback
class HapticManager {
    static let shared = HapticManager()

    private var impactLight: UIImpactFeedbackGenerator?
    private var impactMedium: UIImpactFeedbackGenerator?

    func prepare() {
        impactLight = UIImpactFeedbackGenerator(style: .light)
        impactLight?.prepare()

        impactMedium = UIImpactFeedbackGenerator(style: .medium)
        impactMedium?.prepare()
    }

    func lightTap() {
        impactLight?.impactOccurred()
        impactLight?.prepare()
    }

    func mediumTap() {
        impactMedium?.impactOccurred()
        impactMedium?.prepare()
    }
}
```

## Interactive Components

### Custom Slider

```swift
struct CustomSlider: View {
    @Binding var value: Double
    let range: ClosedRange<Double>

    @State private var isDragging = false

    var body: some View {
        GeometryReader { geometry in
            ZStack(alignment: .leading) {
                // Track
                RoundedRectangle(cornerRadius: 4)
                    .fill(.gray.opacity(0.3))
                    .frame(height: 8)

                // Fill
                RoundedRectangle(cornerRadius: 4)
                    .fill(.blue)
                    .frame(width: thumbPosition(in: geometry), height: 8)

                // Thumb
                Circle()
                    .fill(.white)
                    .shadow(radius: 2)
                    .frame(width: 24, height: 24)
                    .offset(x: thumbPosition(in: geometry) - 12)
                    .scaleEffect(isDragging ? 1.2 : 1.0)
            }
            .gesture(
                DragGesture(minimumDistance: 0)
                    .onChanged { gesture in
                        isDragging = true
                        updateValue(gesture.location.x, in: geometry)

                        // Haptic on drag start
                        if !isDragging {
                            UIImpactFeedbackGenerator(style: .light).impactOccurred()
                        }
                    }
                    .onEnded { _ in
                        isDragging = false
                    }
            )
        }
        .frame(height: 24)
    }

    private func thumbPosition(in geometry: GeometryProxy) -> CGFloat {
        let percent = (value - range.lowerBound) / (range.upperBound - range.lowerBound)
        return geometry.size.width * CGFloat(percent)
    }

    private func updateValue(_ x: CGFloat, in geometry: GeometryProxy) {
        let percent = Double(x / geometry.size.width)
        let clamped = min(max(percent, 0), 1)
        value = range.lowerBound + (range.upperBound - range.lowerBound) * clamped
    }
}
```

### Pull to Refresh

```swift
struct RefreshableList: View {
    @State private var items: [Item] = []

    var body: some View {
        List(items) { item in
            ItemRow(item: item)
        }
        .refreshable {
            // Async refresh
            await loadItems()
        }
    }

    func loadItems() async {
        // Fetch data
        items = try? await api.fetchItems() ?? []
    }
}
```

### Scroll Position Detection

```swift
struct ScrollPositionView: View {
    @State private var scrollOffset: CGFloat = 0

    var body: some View {
        ScrollView {
            VStack {
                ForEach(0..<50) { index in
                    Text("Row \(index)")
                        .frame(maxWidth: .infinity)
                        .padding()
                }
            }
            .background(
                GeometryReader { geometry in
                    Color.clear.preference(
                        key: ScrollOffsetPreferenceKey.self,
                        value: geometry.frame(in: .named("scroll")).minY
                    )
                }
            )
        }
        .coordinateSpace(name: "scroll")
        .onPreferenceChange(ScrollOffsetPreferenceKey.self) { value in
            scrollOffset = value
        }
        .overlay(alignment: .top) {
            // Shrinking header based on scroll
            Header()
                .scaleEffect(max(0.8, min(1, 1 + scrollOffset / 200)))
        }
    }
}

struct ScrollOffsetPreferenceKey: PreferenceKey {
    static var defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = nextValue()
    }
}
```

## Accessibility

### Accessible Gestures

```swift
struct AccessibleCard: View {
    var body: some View {
        CardContent()
            .onTapGesture {
                selectCard()
            }
            .accessibilityAction {
                selectCard()  // Triggered by VoiceOver activation
            }
            .accessibilityHint("Double tap to select")
    }
}

// Custom accessibility actions
struct MultiActionView: View {
    var body: some View {
        ItemRow()
            .accessibilityAction(named: "Delete") {
                deleteItem()
            }
            .accessibilityAction(named: "Favorite") {
                toggleFavorite()
            }
    }
}
```

## Best Practices

1. **Provide visual feedback** - Show state changes during gestures
2. **Use haptics sparingly** - Reinforce key interactions only
3. **Support accessibility** - Add `.accessibilityAction` for custom gestures
4. **Test on device** - Simulator doesn't capture gesture nuances
5. **Consider gesture conflicts** - Use `.highPriorityGesture` or `.simultaneousGesture`
6. **Prepare haptic generators** - Call `.prepare()` before time-sensitive feedback

## Related Skills

- swiftui-components: UI elements
- swiftui-architecture: State management for gestures
- swiftui-testing: Testing gesture interactions
