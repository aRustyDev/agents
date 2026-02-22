# Accessibility Audit

Audit design components and generated code for WCAG 2.1 compliance. Check color contrast, touch targets, screen reader compatibility, and keyboard navigation.

## WCAG Compliance Levels

| Level | Description | Target |
|-------|-------------|--------|
| A | Minimum accessibility | Required |
| AA | Standard compliance | Recommended |
| AAA | Enhanced accessibility | Aspirational |

## Color Contrast

### Requirements

| Element | WCAG Level | Ratio |
|---------|------------|-------|
| Normal text | AA | 4.5:1 |
| Large text (18px+) | AA | 3:1 |
| UI components | AA | 3:1 |
| Enhanced (AAA) | AAA | 7:1 |

### Checking Contrast

**Using design tokens:**

```javascript
function getContrastRatio(color1, color2) {
  const l1 = getLuminance(color1);
  const l2 = getLuminance(color2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

function getLuminance(hex) {
  const rgb = hexToRgb(hex);
  const [r, g, b] = rgb.map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
```

**Audit Report Format:**

```text
## Color Contrast Audit

### Passing
| Pair | Foreground | Background | Ratio | Level |
|------|------------|------------|-------|-------|
| Text on surface | #1A1A1A | #FFFFFF | 16.1:1 | AAA |
| Primary button | #FFFFFF | #2196F3 | 4.6:1 | AA |

### Failing
| Pair | Foreground | Background | Ratio | Required | Fix |
|------|------------|------------|-------|----------|-----|
| Muted text | #999999 | #F5F5F5 | 2.8:1 | 4.5:1 | Darken to #666666 |
| Disabled | #CCCCCC | #FFFFFF | 1.6:1 | 3:1 | Darken to #949494 |
```

### Automated Tools

```bash
# Install color contrast checker
npm install -g color-contrast-checker

# Check specific colors
contrast-check "#1A1A1A" "#FFFFFF"

# Audit CSS file
npx color-contrast-audit ./styles.css
```

## Touch Targets

### Requirements

| Platform | Minimum Size | Recommended |
|----------|--------------|-------------|
| iOS | 44×44 pt | 48×48 pt |
| Android | 48×48 dp | 56×56 dp |
| Web | 44×44 px | 48×48 px |

### Checking Touch Targets

**Component Audit:**

```text
## Touch Target Audit

### Compliant
| Component | Size | Platform | Status |
|-----------|------|----------|--------|
| Button | 48×48 | All | ✓ |
| ListItem | 56×48 | All | ✓ |
| Checkbox | 44×44 | All | ✓ |

### Non-Compliant
| Component | Current | Required | Fix |
|-----------|---------|----------|-----|
| IconButton | 32×32 | 44×44 | Add padding |
| CloseButton | 24×24 | 44×44 | Increase hit area |
| Link (inline) | 16×16 | 44×44 | Add touch padding |
```

### Implementation Fixes

**SwiftUI:**

```swift
// Bad: Small touch target
Image(systemName: "xmark")
    .frame(width: 24, height: 24)

// Good: Adequate touch target
Image(systemName: "xmark")
    .frame(width: 44, height: 44)
    .contentShape(Rectangle())
```

**React:**

```tsx
// Bad: Small touch target
<button className="w-6 h-6">×</button>

// Good: Visual + touch area separated
<button className="w-11 h-11 flex items-center justify-center">
  <span className="w-6 h-6">×</span>
</button>
```

## Screen Reader Compatibility

### Requirements

- All interactive elements must have accessible names
- Images must have alt text (or be decorative)
- Form inputs must have labels
- Dynamic content must be announced

### Audit Checklist

```text
## Screen Reader Audit

### Images
| Image | Alt Text | Status |
|-------|----------|--------|
| logo.png | "Company Logo" | ✓ |
| hero.jpg | "Team collaboration" | ✓ |
| icon-arrow.svg | "" (decorative) | ✓ |
| product.png | Missing | ✗ Fix: Add alt |

### Interactive Elements
| Element | Accessible Name | Source |
|---------|-----------------|--------|
| Submit button | "Submit form" | Content |
| Close button | "Close dialog" | aria-label |
| Search input | "Search products" | Label element |
| Nav menu | Missing | ✗ Fix: Add aria-label |

### Dynamic Content
| Update | Announcement | Status |
|--------|--------------|--------|
| Form error | role="alert" | ✓ |
| Toast | aria-live="polite" | ✓ |
| Loading | "Loading..." | ✗ Fix: Add aria-busy |
```

### ARIA Implementation

**Required Attributes:**

```html
<!-- Buttons with icons only -->
<button aria-label="Close dialog">
  <svg>...</svg>
</button>

<!-- Form inputs -->
<label for="email">Email</label>
<input id="email" type="email" aria-describedby="email-hint">
<span id="email-hint">We'll never share your email</span>

<!-- Dynamic regions -->
<div role="status" aria-live="polite">
  {statusMessage}
</div>
```

## Keyboard Navigation

### Requirements

- All interactive elements reachable via Tab
- Visible focus indicators
- Logical tab order
- Escape closes modals/dialogs
- Arrow keys for menus/lists

### Focus Indicators

**Requirements:**

| Property | Minimum | Recommended |
|----------|---------|-------------|
| Contrast | 3:1 | 4.5:1 |
| Width | 2px | 3px |
| Offset | 0px | 2px |
| Style | Solid | Any visible |

**Implementation:**

```css
/* Bad: Removed focus */
:focus {
  outline: none;
}

/* Good: Custom focus */
:focus-visible {
  outline: 3px solid var(--color-primary);
  outline-offset: 2px;
}

/* Good: Focus ring component */
.focus-ring:focus-visible {
  box-shadow: 0 0 0 3px var(--color-focus);
}
```

### Tab Order Audit

```text
## Keyboard Navigation Audit

### Tab Order
1. Skip to content link ✓
2. Logo (link to home) ✓
3. Navigation items (1-5) ✓
4. Search input ✓
5. Main content starts ✓

### Focus Visibility
| Element | Has Focus Style | Contrast | Status |
|---------|-----------------|----------|--------|
| Button | Yes | 4.8:1 | ✓ |
| Link | Yes | 4.5:1 | ✓ |
| Input | Yes | 3.2:1 | ✓ |
| Checkbox | No | - | ✗ Fix |

### Keyboard Shortcuts
| Action | Key | Working |
|--------|-----|---------|
| Submit form | Enter | ✓ |
| Close modal | Escape | ✓ |
| Menu navigation | Arrow keys | ✓ |
| Skip link | Tab (first) | ✓ |
```

## Motion and Animation

### Requirements

- Respect `prefers-reduced-motion`
- No auto-playing videos with sound
- No flashing content (3 flashes/second)
- Provide pause controls for animation

### Implementation

**CSS:**

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**SwiftUI:**

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

var animation: Animation? {
    reduceMotion ? nil : .spring()
}
```

**React:**

```tsx
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

const variants = {
  enter: prefersReducedMotion
    ? { opacity: 1 }
    : { opacity: 1, y: 0, transition: { duration: 0.3 } },
};
```

## Audit Report Template

```markdown
# Accessibility Audit Report

**Component**: ButtonComponent
**Date**: 2026-02-22
**WCAG Target**: AA

## Summary

| Category | Pass | Fail | Warnings |
|----------|------|------|----------|
| Color Contrast | 4 | 1 | 0 |
| Touch Targets | 3 | 0 | 1 |
| Screen Reader | 5 | 2 | 0 |
| Keyboard | 4 | 0 | 0 |
| Motion | 2 | 0 | 0 |
| **Total** | **18** | **3** | **1** |

## Critical Issues

### 1. Insufficient Color Contrast
- **Element**: Disabled state text
- **Current**: 2.8:1
- **Required**: 4.5:1
- **Fix**: Change `#999999` to `#767676`

### 2. Missing Accessible Name
- **Element**: Icon-only button
- **Issue**: No accessible name for screen readers
- **Fix**: Add `aria-label="Close"`

## Recommendations

1. Add focus indicators to all interactive elements
2. Increase disabled state contrast
3. Add aria-labels to icon buttons
4. Test with VoiceOver/TalkBack

## Compliance Status

| Level | Status |
|-------|--------|
| WCAG 2.1 A | ⚠️ 2 issues |
| WCAG 2.1 AA | ⚠️ 3 issues |
| WCAG 2.1 AAA | ❌ Not targeted |
```

## Testing Tools

### Automated

```bash
# axe-core CLI
npm install -g @axe-core/cli
axe https://example.com

# Lighthouse accessibility
npx lighthouse https://example.com --only-categories=accessibility

# pa11y
npx pa11y https://example.com
```

### Manual Testing

| Tool | Platform | Purpose |
|------|----------|---------|
| VoiceOver | macOS/iOS | Screen reader |
| TalkBack | Android | Screen reader |
| NVDA | Windows | Screen reader |
| Accessibility Inspector | Xcode | iOS audit |
| Chrome DevTools | Web | Accessibility tree |

## Integration

The accessibility-audit skill is used by:

- **design-translator**: Validate generated components
- **component-spec style**: Include accessibility section
- **design-system-architect**: Ensure system-wide compliance
