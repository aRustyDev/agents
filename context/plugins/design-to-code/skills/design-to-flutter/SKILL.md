---
name: design-to-flutter
description: Convert design specifications from Figma, Sketch, or Penpot to Flutter widgets with proper theming
created: 2026-02-22
updated: 2026-02-22
tags: [design, flutter, dart, widgets, material]
requires: design-tokens-extraction
---

# Design to Flutter

Convert design component specifications to Flutter widgets.

## Overview

This skill transforms design specifications into idiomatic Flutter widgets with proper theming, composition patterns, and Material/Cupertino compliance.

**This skill covers:**

- Converting design frames to Flutter widget trees
- Mapping design properties to widget parameters
- Generating theme-aware widgets
- Creating widget tests

**This skill does NOT cover:**

- Design token extraction (see `design-tokens-extraction` skill)
- State management (Provider, Riverpod, Bloc)
- Navigation and routing

## Quick Reference

### Design to Flutter Mapping

| Design Element | Flutter Widget |
|----------------|----------------|
| Frame/Group | `Container`, `SizedBox` |
| Auto-layout horizontal | `Row` |
| Auto-layout vertical | `Column` |
| Overlapping layers | `Stack` |
| Text | `Text` |
| Rectangle | `Container` with `BoxDecoration` |
| Circle | `Container` with `BoxShape.circle` |
| Image | `Image.asset` / `Image.network` |
| Scroll | `SingleChildScrollView`, `ListView` |
| Grid | `GridView` |

### Layout Properties

| Design Property | Flutter Equivalent |
|-----------------|-------------------|
| Padding | `Padding` widget or `padding` parameter |
| Gap/Spacing | `SizedBox` or `MainAxisAlignment.spaceBetween` |
| Alignment | `MainAxisAlignment`, `CrossAxisAlignment` |
| Fill container | `Expanded`, `Flexible` |
| Fixed size | `SizedBox`, `Container` with constraints |

## Workflow: Convert Design Component

### Step 1: Analyze Design Structure

Read the design component and identify:

- Widget hierarchy and nesting
- Layout direction and spacing
- Theme token usage
- Interactive elements

### Step 2: Generate Widget Code

```dart
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class ComponentName extends StatelessWidget {
  final String title;
  final String? subtitle;
  final VoidCallback? onTap;

  const ComponentName({
    super.key,
    required this.title,
    this.subtitle,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.all(AppTheme.spacing.md),
        decoration: BoxDecoration(
          color: theme.colorScheme.surface,
          borderRadius: BorderRadius.circular(AppTheme.radius.md),
          boxShadow: [AppTheme.shadows.sm],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: theme.textTheme.bodyLarge,
            ),
            if (subtitle != null) ...[
              SizedBox(height: AppTheme.spacing.xs),
              Text(
                subtitle!,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

### Step 3: Generate Theme Extensions

```dart
import 'package:flutter/material.dart';

class AppTheme {
  // Spacing scale
  static const spacing = _Spacing();

  // Border radius
  static const radius = _Radius();

  // Shadows
  static const shadows = _Shadows();

  // Light theme
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFF2196F3),
      brightness: Brightness.light,
    ),
    textTheme: _textTheme,
  );

  // Dark theme
  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFF2196F3),
      brightness: Brightness.dark,
    ),
    textTheme: _textTheme,
  );

  static const _textTheme = TextTheme(
    displayLarge: TextStyle(fontSize: 57, fontWeight: FontWeight.w400),
    displayMedium: TextStyle(fontSize: 45, fontWeight: FontWeight.w400),
    headlineLarge: TextStyle(fontSize: 32, fontWeight: FontWeight.w600),
    headlineMedium: TextStyle(fontSize: 28, fontWeight: FontWeight.w600),
    bodyLarge: TextStyle(fontSize: 16, fontWeight: FontWeight.w400),
    bodyMedium: TextStyle(fontSize: 14, fontWeight: FontWeight.w400),
    labelLarge: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
  );
}

class _Spacing {
  const _Spacing();

  double get xs => 4;
  double get sm => 8;
  double get md => 16;
  double get lg => 24;
  double get xl => 32;
}

class _Radius {
  const _Radius();

  double get sm => 4;
  double get md => 8;
  double get lg => 16;
  double get full => 9999;
}

class _Shadows {
  const _Shadows();

  BoxShadow get sm => BoxShadow(
    color: Colors.black.withOpacity(0.05),
    blurRadius: 2,
    offset: const Offset(0, 1),
  );

  BoxShadow get md => BoxShadow(
    color: Colors.black.withOpacity(0.1),
    blurRadius: 6,
    offset: const Offset(0, 4),
  );

  BoxShadow get lg => BoxShadow(
    color: Colors.black.withOpacity(0.1),
    blurRadius: 15,
    offset: const Offset(0, 10),
  );
}
```

## Common Patterns

### Card Widget

```dart
class AppCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final VoidCallback? onTap;

  const AppCard({
    super.key,
    required this.child,
    this.padding,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    Widget card = Container(
      padding: padding ?? EdgeInsets.all(AppTheme.spacing.md),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(AppTheme.radius.lg),
        boxShadow: [AppTheme.shadows.md],
      ),
      child: child,
    );

    if (onTap != null) {
      return InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppTheme.radius.lg),
        child: card,
      );
    }

    return card;
  }
}
```

### Button Widget

```dart
enum ButtonVariant { primary, secondary, ghost }
enum ButtonSize { small, medium, large }

class AppButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final ButtonVariant variant;
  final ButtonSize size;
  final IconData? leftIcon;
  final IconData? rightIcon;
  final bool isLoading;

  const AppButton({
    super.key,
    required this.label,
    this.onPressed,
    this.variant = ButtonVariant.primary,
    this.size = ButtonSize.medium,
    this.leftIcon,
    this.rightIcon,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    final padding = switch (size) {
      ButtonSize.small => EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      ButtonSize.medium => EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      ButtonSize.large => EdgeInsets.symmetric(horizontal: 24, vertical: 16),
    };

    final textStyle = switch (size) {
      ButtonSize.small => theme.textTheme.labelSmall,
      ButtonSize.medium => theme.textTheme.labelLarge,
      ButtonSize.large => theme.textTheme.labelLarge?.copyWith(fontSize: 16),
    };

    final (backgroundColor, foregroundColor) = switch (variant) {
      ButtonVariant.primary => (
        theme.colorScheme.primary,
        theme.colorScheme.onPrimary,
      ),
      ButtonVariant.secondary => (
        theme.colorScheme.secondaryContainer,
        theme.colorScheme.onSecondaryContainer,
      ),
      ButtonVariant.ghost => (
        Colors.transparent,
        theme.colorScheme.primary,
      ),
    };

    return Material(
      color: backgroundColor,
      borderRadius: BorderRadius.circular(AppTheme.radius.md),
      child: InkWell(
        onTap: isLoading ? null : onPressed,
        borderRadius: BorderRadius.circular(AppTheme.radius.md),
        child: Padding(
          padding: padding,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (isLoading)
                SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: foregroundColor,
                  ),
                )
              else if (leftIcon != null)
                Icon(leftIcon, size: 20, color: foregroundColor),
              if (leftIcon != null || isLoading) SizedBox(width: 8),
              Text(label, style: textStyle?.copyWith(color: foregroundColor)),
              if (rightIcon != null) ...[
                SizedBox(width: 8),
                Icon(rightIcon, size: 20, color: foregroundColor),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
```

### List Item Widget

```dart
class ListItem extends StatelessWidget {
  final String title;
  final String? subtitle;
  final Widget? leading;
  final Widget? trailing;
  final VoidCallback? onTap;

  const ListItem({
    super.key,
    required this.title,
    this.subtitle,
    this.leading,
    this.trailing,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: EdgeInsets.symmetric(
          horizontal: AppTheme.spacing.md,
          vertical: AppTheme.spacing.sm,
        ),
        child: Row(
          children: [
            if (leading != null) ...[
              leading!,
              SizedBox(width: AppTheme.spacing.md),
            ],
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: theme.textTheme.bodyLarge),
                  if (subtitle != null)
                    Text(
                      subtitle!,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                ],
              ),
            ),
            if (trailing != null) ...[
              SizedBox(width: AppTheme.spacing.md),
              trailing!,
            ],
          ],
        ),
      ),
    );
  }
}
```

## Widget Test Template

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:your_app/widgets/component_name.dart';

void main() {
  group('ComponentName', () {
    testWidgets('renders title', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ComponentName(title: 'Test Title'),
          ),
        ),
      );

      expect(find.text('Test Title'), findsOneWidget);
    });

    testWidgets('renders subtitle when provided', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: ComponentName(
              title: 'Title',
              subtitle: 'Subtitle',
            ),
          ),
        ),
      );

      expect(find.text('Subtitle'), findsOneWidget);
    });

    testWidgets('calls onTap when tapped', (tester) async {
      var tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ComponentName(
              title: 'Title',
              onTap: () => tapped = true,
            ),
          ),
        ),
      );

      await tester.tap(find.byType(ComponentName));
      expect(tapped, isTrue);
    });
  });
}
```

## File Structure

```text
lib/
├── theme/
│   ├── app_theme.dart
│   ├── colors.dart
│   └── typography.dart
├── widgets/
│   ├── app_button.dart
│   ├── app_card.dart
│   ├── list_item.dart
│   └── widgets.dart  // barrel export
└── main.dart
```

## See Also

- `design-tokens-extraction` skill - Extract tokens first
- `design-token-json` style - Token format reference
- `component-spec` style - Documentation format
