---
name: design-to-swiftui
description: Convert design specifications from Figma, Sketch, or Penpot to SwiftUI view code with proper modifiers and theme integration
created: 2026-02-22
updated: 2026-02-22
tags: [design, swiftui, ios, code-generation, figma, sketch]
requires: design-tokens-extraction
---

# Design to SwiftUI

Convert design component specifications to SwiftUI view code.

## Overview

This skill transforms design specifications (from Figma, Sketch, or Penpot) into idiomatic SwiftUI views with proper modifiers, layout containers, and theme token integration.

**This skill covers:**

- Converting design frames to SwiftUI layouts (VStack, HStack, ZStack)
- Mapping design properties to SwiftUI modifiers
- Generating reusable SwiftUI components
- Integrating with extracted design tokens

**This skill does NOT cover:**

- Design token extraction (see `design-tokens-extraction` skill)
- State management and data binding
- Navigation and routing

## Quick Reference

### Design to SwiftUI Mapping

| Design Element | SwiftUI Component |
|----------------|-------------------|
| Horizontal layout | `HStack` |
| Vertical layout | `VStack` |
| Overlapping layers | `ZStack` |
| Auto-layout | `Stack` with `spacing` |
| Grid | `LazyVGrid` / `LazyHGrid` |
| Scroll container | `ScrollView` |
| Text | `Text` with modifiers |
| Rectangle | `RoundedRectangle` or `Rectangle` |
| Circle | `Circle` |
| Image | `Image` / `AsyncImage` |
| Button | `Button` with custom label |

### Property Mapping

| Design Property | SwiftUI Modifier |
|-----------------|------------------|
| Fill color | `.fill()` / `.foregroundStyle()` |
| Stroke | `.stroke()` / `.overlay()` |
| Corner radius | `.clipShape(RoundedRectangle())` |
| Shadow | `.shadow()` |
| Opacity | `.opacity()` |
| Padding | `.padding()` |
| Size | `.frame()` |
| Position | `.offset()` / `.position()` |

## Workflow: Convert Design Component

### Step 1: Analyze Design Structure

Read the design component from MCP and identify:

- Layout type (horizontal, vertical, grid, free-form)
- Child elements and their order
- Spacing and padding values
- Constraints and sizing behavior

### Step 2: Map to SwiftUI Layout

**Auto-layout (horizontal):**

```swift
HStack(alignment: .<alignment>, spacing: <gap>) {
    // children
}
```

**Auto-layout (vertical):**

```swift
VStack(alignment: .<alignment>, spacing: <gap>) {
    // children
}
```

**Grid layout:**

```swift
let columns = [
    GridItem(.flexible()),
    GridItem(.flexible())
]
LazyVGrid(columns: columns, spacing: <gap>) {
    // children
}
```

**Absolute positioning (rare in SwiftUI):**

```swift
ZStack {
    // position children with .offset() or .position()
}
```

### Step 3: Generate View Code

For each design element, generate SwiftUI code:

**Text elements:**

```swift
Text("<content>")
    .font(<Theme.Typography.style>)
    .foregroundStyle(<Theme.Colors.color>)
    .lineLimit(<lines>)
    .multilineTextAlignment(.<alignment>)
```

**Shapes with fill:**

```swift
RoundedRectangle(cornerRadius: Theme.Radius.<size>)
    .fill(Theme.Colors.<color>)
    .frame(width: <width>, height: <height>)
    .shadow(color: .black.opacity(0.1), radius: 4, y: 2)
```

**Images:**

```swift
// Local image
Image("<assetName>")
    .resizable()
    .aspectRatio(contentMode: .fill)
    .frame(width: <width>, height: <height>)
    .clipShape(RoundedRectangle(cornerRadius: Theme.Radius.<size>))

// Remote image
AsyncImage(url: URL(string: "<url>")) { image in
    image
        .resizable()
        .aspectRatio(contentMode: .fill)
} placeholder: {
    ProgressView()
}
.frame(width: <width>, height: <height>)
```

**Buttons:**

```swift
Button {
    // action
} label: {
    HStack(spacing: 8) {
        Image(systemName: "<icon>")
        Text("<label>")
    }
    .font(Theme.Typography.<style>)
    .foregroundStyle(Theme.Colors.<textColor>)
    .padding(.horizontal, Theme.Spacing.<h>)
    .padding(.vertical, Theme.Spacing.<v>)
    .background(Theme.Colors.<bgColor>)
    .clipShape(RoundedRectangle(cornerRadius: Theme.Radius.<size>))
}
```

### Step 4: Create Component View

Wrap the generated code in a reusable SwiftUI View:

```swift
import SwiftUI

struct <ComponentName>View: View {
    // Properties extracted from design variants
    let title: String
    let subtitle: String?
    var onTap: (() -> Void)?

    var body: some View {
        VStack(alignment: .leading, spacing: Theme.Spacing.sm) {
            Text(title)
                .font(Theme.Typography.headlineMedium)
                .foregroundStyle(Theme.Colors.text)

            if let subtitle {
                Text(subtitle)
                    .font(Theme.Typography.bodyMedium)
                    .foregroundStyle(Theme.Colors.textSecondary)
            }
        }
        .padding(Theme.Spacing.md)
        .background(Theme.Colors.surface)
        .clipShape(RoundedRectangle(cornerRadius: Theme.Radius.md))
        .onTapGesture {
            onTap?()
        }
    }
}

#Preview {
    <ComponentName>View(
        title: "Preview Title",
        subtitle: "Preview subtitle text"
    )
    .padding()
}
```

## Common Patterns

### Card Component

Design spec:

- Background fill with rounded corners
- Shadow elevation
- Padding around content
- Optional image header

```swift
struct CardView<Content: View>: View {
    let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            content
        }
        .background(Theme.Colors.surface)
        .clipShape(RoundedRectangle(cornerRadius: Theme.Radius.lg))
        .shadow(
            color: .black.opacity(0.08),
            radius: 8,
            y: 4
        )
    }
}
```

### Button Variants

Design spec defines Primary, Secondary, Ghost variants:

```swift
enum ButtonVariant {
    case primary, secondary, ghost

    var backgroundColor: Color {
        switch self {
        case .primary: Theme.Colors.primary
        case .secondary: Theme.Colors.surface
        case .ghost: .clear
        }
    }

    var foregroundColor: Color {
        switch self {
        case .primary: Theme.Colors.onPrimary
        case .secondary: Theme.Colors.primary
        case .ghost: Theme.Colors.primary
        }
    }
}

struct ThemedButton: View {
    let title: String
    let variant: ButtonVariant
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(Theme.Typography.labelLarge)
                .foregroundStyle(variant.foregroundColor)
                .padding(.horizontal, Theme.Spacing.lg)
                .padding(.vertical, Theme.Spacing.md)
                .background(variant.backgroundColor)
                .clipShape(RoundedRectangle(cornerRadius: Theme.Radius.md))
        }
    }
}
```

### List Item

Design spec with leading icon, title/subtitle, trailing accessory:

```swift
struct ListItemView: View {
    let icon: String
    let title: String
    let subtitle: String?
    let accessory: Accessory

    enum Accessory {
        case chevron
        case toggle(Binding<Bool>)
        case badge(String)
        case none
    }

    var body: some View {
        HStack(spacing: Theme.Spacing.md) {
            Image(systemName: icon)
                .font(.system(size: 20))
                .foregroundStyle(Theme.Colors.primary)
                .frame(width: 24)

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(Theme.Typography.bodyLarge)
                    .foregroundStyle(Theme.Colors.text)

                if let subtitle {
                    Text(subtitle)
                        .font(Theme.Typography.bodySmall)
                        .foregroundStyle(Theme.Colors.textSecondary)
                }
            }

            Spacer()

            accessoryView
        }
        .padding(.vertical, Theme.Spacing.sm)
        .padding(.horizontal, Theme.Spacing.md)
    }

    @ViewBuilder
    private var accessoryView: some View {
        switch accessory {
        case .chevron:
            Image(systemName: "chevron.right")
                .foregroundStyle(Theme.Colors.textSecondary)
        case .toggle(let isOn):
            Toggle("", isOn: isOn)
                .labelsHidden()
        case .badge(let text):
            Text(text)
                .font(Theme.Typography.labelSmall)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Theme.Colors.primary)
                .foregroundStyle(Theme.Colors.onPrimary)
                .clipShape(Capsule())
        case .none:
            EmptyView()
        }
    }
}
```

## Token Integration

Reference design tokens through the Theme struct:

```swift
// Colors
Theme.Colors.primary
Theme.Colors.surface
Theme.Colors.text
Theme.Colors.textSecondary

// Typography
Theme.Typography.displayLarge
Theme.Typography.headlineMedium
Theme.Typography.bodyLarge
Theme.Typography.labelSmall

// Spacing
Theme.Spacing.xs  // 4
Theme.Spacing.sm  // 8
Theme.Spacing.md  // 16
Theme.Spacing.lg  // 24
Theme.Spacing.xl  // 32

// Corner Radius
Theme.Radius.sm   // 4
Theme.Radius.md   // 8
Theme.Radius.lg   // 16
Theme.Radius.full // 9999
```

## Naming Conventions

| Design Name | SwiftUI Name |
|-------------|--------------|
| `Button/Primary` | `PrimaryButton` |
| `Card - Article` | `ArticleCardView` |
| `List Item/Default` | `ListItemView` |
| `Header/Large` | `LargeHeaderView` |
| `Input/Text Field` | `TextFieldView` |

## See Also

- `design-tokens-extraction` skill - Extract tokens first
- `design-token-swift` style - Swift code output format
- `swiftui-components` skill - SwiftUI component patterns
