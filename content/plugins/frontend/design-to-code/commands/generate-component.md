---
name: generate-component
description: Convert a design component to framework-specific code (SwiftUI, React, Flutter, Tailwind)
---

# Generate Component

Convert a design component (frame, component, or selection) to production-ready code for the specified framework.

## Arguments

- `<component>` - Component identifier:
  - Figma: Node ID or component name (e.g., `Button/Primary`, `12:345`)
  - Sketch: Layer name or path (e.g., `Symbols/Button/Primary`)
  - Penpot: Component ID or name
- `--file` - Design file identifier (if not in current context)
- `--framework` - Target framework: `swiftui` (default), `react`, `flutter`, `tailwind`
- `--output` - Output file path (default: stdout)
- `--with-tokens` - Include design token definitions in output (default: false)
- `--with-preview` - Include preview/storybook code (default: true)

## Workflow

### Step 1: Locate Component

Find the component in the design file:

**Figma:**

```text
Use figma MCP server
- Call get_file_nodes with node_ids
- Or search by component name in file structure
```

**Sketch:**

```text
Use sketch-context MCP server
- Call get_symbols to list components
- Or get_layer_by_path for specific path
```

**Penpot:**

```text
Use penpot MCP server
- Call get_components to list components
- Get component by ID or name match
```

### Step 2: Analyze Component Structure

Extract from the design component:

- Layout hierarchy (frames, groups, layers)
- Auto-layout properties (direction, gap, padding)
- Child elements (text, shapes, images, icons)
- Variants and states (if component set)
- Design token references (colors, typography, spacing)

### Step 3: Generate Code

Use the appropriate skill based on framework:

| Framework | Skill | Output Style |
|-----------|-------|--------------|
| `swiftui` | `design-to-swiftui` | Swift View struct |
| `react` | `design-to-react` | React component |
| `flutter` | `design-to-flutter` | Flutter widget |
| `tailwind` | `design-to-tailwind` | HTML + Tailwind classes |

### Step 4: Apply Tokens

If `--with-tokens`:

- Extract tokens used by the component
- Include token definitions in output
- Use extracted token values in code

If not `--with-tokens`:

- Reference Theme struct/tokens by name
- Assume tokens are already defined elsewhere

### Step 5: Add Preview

If `--with-preview` (default):

- SwiftUI: Add `#Preview` macro
- React: Add Storybook story
- Flutter: Add preview scaffold
- Tailwind: Add HTML example

### Step 6: Write Output

If `--output` specified:

- Write to file path
- Report file location

If no output:

- Display generated code
- Show component summary

## Examples

```bash
# Generate SwiftUI from Figma component
/generate-component "Button/Primary" --file abc123 --framework swiftui

# Generate React with tokens included
/generate-component "Card/Article" --framework react --with-tokens --output ./src/components/ArticleCard.tsx

# Generate Flutter widget
/generate-component 12:345 --file abc123 --framework flutter --output ./lib/widgets/button.dart

# Generate Tailwind HTML from Sketch
/generate-component "Symbols/Header/Main" --file ./design.sketch --framework tailwind
```

## Output Examples

### SwiftUI Output

```swift
import SwiftUI

struct PrimaryButtonView: View {
    let title: String
    let icon: String?
    var isLoading: Bool = false
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                if isLoading {
                    ProgressView()
                        .progressViewStyle(.circular)
                        .tint(.white)
                } else if let icon {
                    Image(systemName: icon)
                }
                Text(title)
            }
            .font(Theme.Typography.labelLarge)
            .foregroundStyle(Theme.Colors.onPrimary)
            .padding(.horizontal, 24)
            .padding(.vertical, 12)
            .background(Theme.Colors.primary)
            .clipShape(RoundedRectangle(cornerRadius: 8))
        }
        .disabled(isLoading)
    }
}

#Preview {
    VStack(spacing: 16) {
        PrimaryButtonView(title: "Continue", icon: "arrow.right") {}
        PrimaryButtonView(title: "Loading", icon: nil, isLoading: true) {}
    }
    .padding()
}
```

### React Output

```tsx
import React from 'react';
import styles from './PrimaryButton.module.css';

interface PrimaryButtonProps {
  title: string;
  icon?: React.ReactNode;
  isLoading?: boolean;
  onClick: () => void;
}

export const PrimaryButton: React.FC<PrimaryButtonProps> = ({
  title,
  icon,
  isLoading = false,
  onClick,
}) => {
  return (
    <button
      className={styles.button}
      onClick={onClick}
      disabled={isLoading}
    >
      {isLoading ? (
        <span className={styles.spinner} />
      ) : icon ? (
        <span className={styles.icon}>{icon}</span>
      ) : null}
      <span>{title}</span>
    </button>
  );
};
```

### Flutter Output

```dart
import 'package:flutter/material.dart';
import '../theme/theme.dart';

class PrimaryButton extends StatelessWidget {
  final String title;
  final IconData? icon;
  final bool isLoading;
  final VoidCallback onPressed;

  const PrimaryButton({
    super.key,
    required this.title,
    this.icon,
    this.isLoading = false,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: isLoading ? null : onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: AppTheme.colors.primary,
        foregroundColor: AppTheme.colors.onPrimary,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (isLoading)
            const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          else if (icon != null)
            Icon(icon, size: 20),
          if (icon != null || isLoading) const SizedBox(width: 8),
          Text(title, style: AppTheme.typography.labelLarge),
        ],
      ),
    );
  }
}
```

## Component Analysis

Display analysis before generating:

```text
## Component: Button/Primary

### Structure
- Frame: 120x44 px
- Auto-layout: Horizontal, gap=8, padding=12x24
- Background: color.primary (#2196F3)
- Corner radius: 8px

### Elements
- Icon (optional): 20x20, color.onPrimary
- Label: typography.labelLarge, color.onPrimary

### Variants
- Default
- Hover (background: color.primary.dark)
- Disabled (opacity: 0.5)
- Loading (show spinner)

### Tokens Referenced
- color.primary, color.onPrimary
- typography.labelLarge
- spacing.md (12), spacing.lg (24)
- radius.md (8)
```

## Error Handling

| Error | Resolution |
|-------|------------|
| Component not found | Check component name/ID, list available components |
| Framework not supported | Use swiftui, react, flutter, or tailwind |
| Missing tokens | Run `/extract-tokens` first or use `--with-tokens` |
| Unsupported element | Manual conversion guidance provided |

## Related Commands

- `/extract-tokens` - Extract design tokens first
- `/sync-design-system` - Sync tokens to codebase
- `/compare-design` - Compare generated code to design
