# Component Spec

Output style for generating design specification documents from components. Use this style when documenting extracted design components for developer handoff.

## Component Specification Format

Generate markdown documentation for each component:

`````markdown
# Component: <ComponentName>

## Overview

<Brief description of the component's purpose and usage>

**Status**: <Draft | Review | Approved>
**Version**: <version>
**Last Updated**: <date>

## Visual Preview

![Component Preview](<path-to-preview-image>)

## Anatomy

```text
┌─────────────────────────────────────┐
│ ┌───┐                               │
│ │ A │  B ─────────────────────      │
│ └───┘  C ─────────────────────      │
│                              ┌───┐  │
│                              │ D │  │
│                              └───┘  │
└─────────────────────────────────────┘

A: Leading Icon (optional)
B: Title
C: Subtitle (optional)
D: Trailing Action
```
`````

## Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `title` | `string` | required | Primary text content |
| `subtitle` | `string?` | `null` | Secondary text content |
| `leadingIcon` | `Icon?` | `null` | Icon displayed before title |
| `trailingAction` | `Action?` | `null` | Action button or icon |
| `onTap` | `() => void` | `null` | Tap handler callback |

## Variants

### Size

| Variant | Height | Padding | Font Size |
|---------|--------|---------|-----------|
| `small` | 40px | 8px 12px | 14px |
| `medium` | 48px | 12px 16px | 16px |
| `large` | 56px | 16px 20px | 18px |

### State

| State | Background | Border | Text |
|-------|------------|--------|------|
| Default | `surface` | none | `text` |
| Hover | `surface-hover` | none | `text` |
| Pressed | `surface-pressed` | none | `text` |
| Disabled | `surface` | none | `text-disabled` |
| Selected | `primary-light` | `primary` | `primary` |

## Design Tokens

### Colors

| Token | Value | Usage |
|-------|-------|-------|
| `background` | `--color-surface` | Component background |
| `border` | `--color-border` | Border when selected |
| `title` | `--color-text` | Title text color |
| `subtitle` | `--color-text-secondary` | Subtitle text color |
| `icon` | `--color-text-secondary` | Icon color |

### Typography

| Element | Token | Spec |
|---------|-------|------|
| Title | `--font-body-medium` | 16px / 500 / 1.5 |
| Subtitle | `--font-body-small` | 14px / 400 / 1.4 |

### Spacing

| Element | Token | Value |
|---------|-------|-------|
| Container padding | `--spacing-md` | 16px |
| Icon-text gap | `--spacing-sm` | 8px |
| Title-subtitle gap | `--spacing-xs` | 4px |

### Other

| Property | Token | Value |
|----------|-------|-------|
| Border radius | `--radius-md` | 8px |
| Shadow | `--shadow-sm` | 0 1px 2px rgba(0,0,0,0.05) |
| Transition | `--duration-fast` | 150ms |

## Layout Specifications

### Container

- **Width**: Flexible (min: 200px, max: 100%)
- **Height**: Auto (based on content) or fixed by variant
- **Padding**: 12px horizontal, 16px vertical
- **Display**: Flex, horizontal, center-aligned

### Content Area

- **Layout**: Flex column
- **Gap**: 4px between title and subtitle
- **Flex**: 1 (fills available space)

### Icon

- **Size**: 24x24px
- **Alignment**: Center vertically
- **Margin**: 12px right of icon

## Interaction Behavior

### Touch/Click

1. On press: Apply pressed state immediately
2. On release within bounds: Trigger `onTap` callback
3. On release outside bounds: Cancel action

### Hover (Desktop)

1. On mouse enter: Apply hover state with 150ms transition
2. On mouse leave: Return to default state

### Focus

1. On keyboard focus: Show focus ring (2px primary outline, 2px offset)
2. On Enter/Space: Trigger `onTap` callback

### Disabled

1. Reduce opacity to 50%
2. Ignore all interactions
3. Change cursor to `not-allowed`

## Accessibility

### Requirements

- [ ] Minimum touch target: 44x44px
- [ ] Color contrast ratio: ≥4.5:1 (text), ≥3:1 (UI)
- [ ] Focus indicator visible
- [ ] Screen reader label provided

### ARIA Attributes

| Attribute | Value | Condition |
|-----------|-------|-----------|
| `role` | `button` | When `onTap` provided |
| `aria-label` | `{title}` | Always |
| `aria-disabled` | `true` | When disabled |
| `tabindex` | `0` | When interactive |

### Keyboard Navigation

| Key | Action |
|-----|--------|
| `Tab` | Move focus to/from component |
| `Enter` | Activate component |
| `Space` | Activate component |

## Responsive Behavior

| Breakpoint | Behavior |
|------------|----------|
| < 320px | Stack icon above text |
| 320px - 768px | Compact padding (8px 12px) |
| > 768px | Full layout as designed |

## Code Examples

### SwiftUI

```swift
ListItemView(
    title: "List Item",
    subtitle: "Supporting text",
    leadingIcon: Image(systemName: "star"),
    trailingAction: .chevron
) {
    // onTap action
}
```

### React

```tsx
<ListItem
  title="List Item"
  subtitle="Supporting text"
  leadingIcon={<StarIcon />}
  trailingAction="chevron"
  onClick={() => {}}
/>
```

### Flutter

```dart
ListItem(
  title: 'List Item',
  subtitle: 'Supporting text',
  leadingIcon: Icons.star,
  trailingAction: ListItemAction.chevron,
  onTap: () {},
)
```

## Related Components

| Component | Relationship |
|-----------|--------------|
| `List` | Parent container |
| `ListSection` | Groups related items |
| `Divider` | Separates items |
| `Icon` | Used for leading/trailing |

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-22 | Initial release |

## Design Source

- **Figma**: [Link to component](<figma-url>)
- **Sketch**: [Link to symbol](<sketch-url>)

## Specification Sections

### Required Sections

| Section | Purpose |
|---------|---------|
| Overview | Component purpose and status |
| Properties | API documentation |
| Design Tokens | Token references |
| Accessibility | WCAG compliance |

### Optional Sections

| Section | When to Include |
|---------|-----------------|
| Variants | Multiple size/state variations |
| Anatomy | Complex component structure |
| Interaction | Interactive components |
| Responsive | Layout changes by breakpoint |
| Code Examples | Developer handoff |

## Token Documentation

For each token reference, include:

1. **Token name**: CSS variable or design system reference
2. **Value**: Resolved value for reference
3. **Usage**: Where/how the token is applied

## Usage Notes

1. Include visual previews when available
2. Document all interactive states
3. Specify accessibility requirements
4. Provide code examples for each target framework
5. Link to source design files
6. Track version history for changes
