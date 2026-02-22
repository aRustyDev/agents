# Design Token Swift

Output style for generating Swift code from design tokens. Use this style when converting extracted design tokens to Swift Color, Font, and spacing extensions.

## Color Extension Format

Generate Color extensions using the extracted color tokens:

```swift
import SwiftUI

extension Color {
    // MARK: - Primary Colors

    /// <description from design token>
    static let <tokenName> = Color(hex: "<hexValue>")

    // MARK: - Secondary Colors

    /// <description>
    static let <tokenName> = Color(hex: "<hexValue>")

    // MARK: - Semantic Colors

    /// <description>
    static let <tokenName> = Color(hex: "<hexValue>")
}

// MARK: - Color Hex Initializer

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
```

## Font Extension Format

Generate Font extensions using the extracted typography tokens:

```swift
import SwiftUI

extension Font {
    // MARK: - Display

    /// <description from design token>
    static let <tokenName> = Font.system(size: <size>, weight: .<weight>, design: .<design>)

    // MARK: - Headings

    /// <description>
    static let <tokenName> = Font.system(size: <size>, weight: .<weight>)

    // MARK: - Body

    /// <description>
    static let <tokenName> = Font.system(size: <size>, weight: .<weight>)

    // MARK: - Custom Fonts (if applicable)

    /// <description>
    static let <tokenName> = Font.custom("<fontFamily>", size: <size>)
}
```

## Spacing Constants Format

Generate spacing values as a structured enum:

```swift
import SwiftUI

enum Spacing {
    // MARK: - Base Units

    /// <description> - <value>px
    static let <tokenName>: CGFloat = <value>

    // MARK: - Component Spacing

    /// <description>
    static let <tokenName>: CGFloat = <value>

    // MARK: - Layout Spacing

    /// <description>
    static let <tokenName>: CGFloat = <value>
}
```

## Border Radius Format

```swift
import SwiftUI

enum CornerRadius {
    /// <description>
    static let <tokenName>: CGFloat = <value>
}
```

## Shadow Format

```swift
import SwiftUI

struct DesignShadow {
    let color: Color
    let radius: CGFloat
    let x: CGFloat
    let y: CGFloat

    // MARK: - Predefined Shadows

    /// <description from design token>
    static let <tokenName> = DesignShadow(
        color: Color.black.opacity(<opacity>),
        radius: <radius>,
        x: <xOffset>,
        y: <yOffset>
    )
}

extension View {
    func designShadow(_ shadow: DesignShadow) -> some View {
        self.shadow(color: shadow.color, radius: shadow.radius, x: shadow.x, y: shadow.y)
    }
}
```

## Theme Struct Format

For comprehensive theming, generate a unified Theme struct:

```swift
import SwiftUI

struct Theme {
    // MARK: - Colors

    struct Colors {
        static let primary = Color.<primaryToken>
        static let secondary = Color.<secondaryToken>
        static let background = Color.<backgroundToken>
        static let surface = Color.<surfaceToken>
        static let text = Color.<textToken>
        static let textSecondary = Color.<textSecondaryToken>
        static let error = Color.<errorToken>
        static let success = Color.<successToken>
        static let warning = Color.<warningToken>
    }

    // MARK: - Typography

    struct Typography {
        static let displayLarge = Font.<displayLargeToken>
        static let headlineLarge = Font.<headlineLargeToken>
        static let headlineMedium = Font.<headlineMediumToken>
        static let bodyLarge = Font.<bodyLargeToken>
        static let bodyMedium = Font.<bodyMediumToken>
        static let labelLarge = Font.<labelLargeToken>
    }

    // MARK: - Spacing

    struct Spacing {
        static let xs = Spacing.<xsToken>
        static let sm = Spacing.<smToken>
        static let md = Spacing.<mdToken>
        static let lg = Spacing.<lgToken>
        static let xl = Spacing.<xlToken>
    }

    // MARK: - Corner Radius

    struct Radius {
        static let sm = CornerRadius.<smToken>
        static let md = CornerRadius.<mdToken>
        static let lg = CornerRadius.<lgToken>
        static let full: CGFloat = 9999
    }
}
```

## Naming Conventions

When converting design token names to Swift:

| Design Token Format | Swift Format | Example |
|---------------------|--------------|---------|
| `color.primary.500` | `primary500` | `Color.primary500` |
| `color-primary-500` | `primaryColor500` | `Color.primaryColor500` |
| `spacing/small` | `small` | `Spacing.small` |
| `typography.heading.h1` | `headingH1` | `Font.headingH1` |
| `shadow-elevation-2` | `elevation2` | `DesignShadow.elevation2` |

## Weight Mappings

| Design Token Weight | SwiftUI Weight |
|---------------------|----------------|
| 100, thin | `.ultraLight` |
| 200, extralight | `.thin` |
| 300, light | `.light` |
| 400, regular, normal | `.regular` |
| 500, medium | `.medium` |
| 600, semibold | `.semibold` |
| 700, bold | `.bold` |
| 800, extrabold | `.heavy` |
| 900, black | `.black` |

## Usage Notes

1. Always include documentation comments with the original token description
2. Group related tokens using `// MARK: -` comments
3. Include the hex initializer only once per file
4. Use `CGFloat` for spacing and sizing values
5. Prefer semantic naming over literal values
6. Generate a unified Theme struct when multiple token categories are present
