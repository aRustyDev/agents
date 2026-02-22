# Design Token CSS

Output style for generating CSS custom properties from design tokens. Use this style when converting extracted design tokens to CSS variables for web applications.

## CSS Custom Properties Format

Generate CSS custom properties using the extracted tokens:

```css
:root {
  /* ========================
   * Colors - Primary
   * ======================== */

  /** <description from design token> */
  --color-primary-50: #E3F2FD;
  --color-primary-100: #BBDEFB;
  --color-primary-500: #2196F3;
  --color-primary-900: #0D47A1;

  /* ========================
   * Colors - Semantic
   * ======================== */

  /** Background color */
  --color-background: var(--color-neutral-50);
  /** Surface/card background */
  --color-surface: var(--color-neutral-100);
  /** Primary text color */
  --color-text: var(--color-neutral-900);
  /** Secondary text color */
  --color-text-secondary: var(--color-neutral-600);
  /** Error state */
  --color-error: #DC2626;
  /** Success state */
  --color-success: #16A34A;
  /** Warning state */
  --color-warning: #D97706;

  /* ========================
   * Typography - Font Family
   * ======================== */

  --font-family-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-family-mono: 'JetBrains Mono', ui-monospace, monospace;

  /* ========================
   * Typography - Font Size
   * ======================== */

  --font-size-xs: 0.75rem;   /* 12px */
  --font-size-sm: 0.875rem;  /* 14px */
  --font-size-base: 1rem;    /* 16px */
  --font-size-lg: 1.125rem;  /* 18px */
  --font-size-xl: 1.25rem;   /* 20px */
  --font-size-2xl: 1.5rem;   /* 24px */
  --font-size-3xl: 1.875rem; /* 30px */
  --font-size-4xl: 2.25rem;  /* 36px */

  /* ========================
   * Typography - Font Weight
   * ======================== */

  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* ========================
   * Typography - Line Height
   * ======================== */

  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;

  /* ========================
   * Spacing
   * ======================== */

  --spacing-0: 0;
  --spacing-1: 0.25rem;  /* 4px */
  --spacing-2: 0.5rem;   /* 8px */
  --spacing-3: 0.75rem;  /* 12px */
  --spacing-4: 1rem;     /* 16px */
  --spacing-5: 1.25rem;  /* 20px */
  --spacing-6: 1.5rem;   /* 24px */
  --spacing-8: 2rem;     /* 32px */
  --spacing-10: 2.5rem;  /* 40px */
  --spacing-12: 3rem;    /* 48px */
  --spacing-16: 4rem;    /* 64px */

  /* ========================
   * Border Radius
   * ======================== */

  --radius-none: 0;
  --radius-sm: 0.125rem;  /* 2px */
  --radius-md: 0.375rem;  /* 6px */
  --radius-lg: 0.5rem;    /* 8px */
  --radius-xl: 0.75rem;   /* 12px */
  --radius-2xl: 1rem;     /* 16px */
  --radius-full: 9999px;

  /* ========================
   * Shadows
   * ======================== */

  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);

  /* ========================
   * Transitions
   * ======================== */

  --duration-instant: 0ms;
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;

  --easing-default: cubic-bezier(0.4, 0, 0.2, 1);
  --easing-in: cubic-bezier(0.4, 0, 1, 1);
  --easing-out: cubic-bezier(0, 0, 0.2, 1);
  --easing-in-out: cubic-bezier(0.4, 0, 0.2, 1);
}
```

## Dark Mode Support

Generate dark mode overrides:

```css
@media (prefers-color-scheme: dark) {
  :root {
    /* Invert semantic colors for dark mode */
    --color-background: var(--color-neutral-900);
    --color-surface: var(--color-neutral-800);
    --color-text: var(--color-neutral-50);
    --color-text-secondary: var(--color-neutral-400);
  }
}

/* Or use a class-based toggle */
.dark {
  --color-background: var(--color-neutral-900);
  --color-surface: var(--color-neutral-800);
  --color-text: var(--color-neutral-50);
  --color-text-secondary: var(--color-neutral-400);
}
```

## Naming Conventions

| Design Token Format | CSS Variable Format | Example |
|---------------------|---------------------|---------|
| `color.primary.500` | `--color-primary-500` | `var(--color-primary-500)` |
| `typography.fontSize.lg` | `--font-size-lg` | `var(--font-size-lg)` |
| `spacing.4` | `--spacing-4` | `var(--spacing-4)` |
| `borderRadius.md` | `--radius-md` | `var(--radius-md)` |
| `shadow.lg` | `--shadow-lg` | `var(--shadow-lg)` |

## Token References

Use `var()` for references between tokens:

```css
:root {
  /* Primitive token */
  --color-blue-500: #2196F3;

  /* Semantic token referencing primitive */
  --color-primary: var(--color-blue-500);

  /* Component token referencing semantic */
  --button-bg: var(--color-primary);
}
```

## Component Tokens

For component-specific tokens:

```css
:root {
  /* Button tokens */
  --button-padding-x: var(--spacing-4);
  --button-padding-y: var(--spacing-2);
  --button-radius: var(--radius-md);
  --button-font-size: var(--font-size-sm);
  --button-font-weight: var(--font-weight-medium);

  /* Card tokens */
  --card-padding: var(--spacing-4);
  --card-radius: var(--radius-lg);
  --card-shadow: var(--shadow-md);
  --card-bg: var(--color-surface);

  /* Input tokens */
  --input-padding-x: var(--spacing-3);
  --input-padding-y: var(--spacing-2);
  --input-radius: var(--radius-md);
  --input-border-color: var(--color-neutral-300);
  --input-focus-ring: var(--color-primary-500);
}
```

## Utility Classes (Optional)

Generate utility classes from tokens:

```css
/* Spacing utilities */
.p-1 { padding: var(--spacing-1); }
.p-2 { padding: var(--spacing-2); }
.p-4 { padding: var(--spacing-4); }

.m-1 { margin: var(--spacing-1); }
.m-2 { margin: var(--spacing-2); }
.m-4 { margin: var(--spacing-4); }

/* Color utilities */
.text-primary { color: var(--color-primary); }
.bg-surface { background-color: var(--color-surface); }

/* Typography utilities */
.text-sm { font-size: var(--font-size-sm); }
.text-base { font-size: var(--font-size-base); }
.font-medium { font-weight: var(--font-weight-medium); }
```

## File Organization

For large design systems:

```css
/* tokens/colors.css */
:root {
  --color-primary-500: #2196F3;
  /* ... */
}

/* tokens/typography.css */
:root {
  --font-size-base: 1rem;
  /* ... */
}

/* tokens/index.css */
@import './colors.css';
@import './typography.css';
@import './spacing.css';
@import './shadows.css';
```

## Usage Notes

1. Always include CSS comments with token descriptions
2. Group related tokens with section headers
3. Use `var()` for token references to enable theming
4. Include fallback values for browser compatibility: `var(--color-primary, #2196F3)`
5. Prefer `rem` units for spacing and font sizes
6. Use semantic token names for colors that change with theme
