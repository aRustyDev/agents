---
name: design-to-tailwind
description: Convert design specifications from Figma, Sketch, or Penpot to HTML with Tailwind CSS utility classes
created: 2026-02-22
updated: 2026-02-22
tags: [design, tailwind, css, html, utility-first]
requires: design-tokens-extraction
---

# Design to Tailwind

Convert design component specifications to HTML with Tailwind CSS.

## Overview

This skill transforms design specifications into semantic HTML with Tailwind utility classes, following utility-first best practices.

**This skill covers:**

- Converting design frames to HTML structure
- Mapping design properties to Tailwind utilities
- Generating responsive variants
- Creating reusable component patterns

**This skill does NOT cover:**

- Design token extraction (see `design-tokens-extraction` skill)
- JavaScript interactivity
- Framework-specific components (React, Vue, etc.)

## Quick Reference

### Design to Tailwind Mapping

| Design Property | Tailwind Utilities |
|-----------------|-------------------|
| Horizontal layout | `flex flex-row` |
| Vertical layout | `flex flex-col` |
| Gap/Spacing | `gap-{size}` |
| Padding | `p-{size}`, `px-{size}`, `py-{size}` |
| Margin | `m-{size}`, `mx-{size}`, `my-{size}` |
| Width | `w-{size}`, `w-full`, `w-auto` |
| Height | `h-{size}`, `h-full`, `h-auto` |
| Background color | `bg-{color}` |
| Text color | `text-{color}` |
| Font size | `text-{size}` |
| Font weight | `font-{weight}` |
| Border radius | `rounded-{size}` |
| Shadow | `shadow-{size}` |
| Opacity | `opacity-{value}` |

### Spacing Scale

| Design Value | Tailwind Class |
|--------------|----------------|
| 4px | `{p\|m\|gap}-1` |
| 8px | `{p\|m\|gap}-2` |
| 12px | `{p\|m\|gap}-3` |
| 16px | `{p\|m\|gap}-4` |
| 24px | `{p\|m\|gap}-6` |
| 32px | `{p\|m\|gap}-8` |

## Workflow: Convert Design Component

### Step 1: Analyze Design Structure

Read the design component and identify:

- Container structure and nesting
- Layout direction and alignment
- Spacing values (map to Tailwind scale)
- Color and typography tokens

### Step 2: Generate HTML with Tailwind

**Basic Card:**

```html
<div class="bg-white rounded-lg shadow-md p-4">
  <h3 class="text-lg font-semibold text-gray-900">Card Title</h3>
  <p class="text-sm text-gray-600 mt-1">Supporting text content</p>
</div>
```

**With Custom Theme Tokens:**

```html
<div class="bg-surface rounded-lg shadow-md p-4">
  <h3 class="text-heading-md text-foreground">Card Title</h3>
  <p class="text-body-sm text-foreground-muted mt-1">Supporting text</p>
</div>
```

### Step 3: Add Interactive States

```html
<button class="
  bg-primary-500 text-white
  px-4 py-2 rounded-md
  font-medium text-sm
  hover:bg-primary-600
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
  active:bg-primary-700
  disabled:opacity-50 disabled:cursor-not-allowed
  transition-colors duration-150
">
  Button Label
</button>
```

### Step 4: Add Responsive Variants

```html
<div class="
  flex flex-col gap-4
  md:flex-row md:gap-6
  lg:gap-8
">
  <div class="w-full md:w-1/2 lg:w-1/3">Column 1</div>
  <div class="w-full md:w-1/2 lg:w-2/3">Column 2</div>
</div>
```

## Common Patterns

### Card Component

```html
<!-- Elevated Card -->
<article class="bg-white rounded-xl shadow-lg overflow-hidden">
  <img
    src="image.jpg"
    alt="Card image"
    class="w-full h-48 object-cover"
  />
  <div class="p-4 space-y-2">
    <h3 class="text-lg font-semibold text-gray-900">Card Title</h3>
    <p class="text-sm text-gray-600 line-clamp-2">
      Description text that may be truncated...
    </p>
    <div class="flex items-center justify-between pt-2">
      <span class="text-sm font-medium text-primary-600">$29.99</span>
      <button class="text-sm text-gray-500 hover:text-gray-700">
        View details →
      </button>
    </div>
  </div>
</article>

<!-- Outlined Card -->
<article class="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
  <h3 class="font-medium text-gray-900">Card Title</h3>
  <p class="text-sm text-gray-600 mt-1">Description text</p>
</article>
```

### Button Variants

```html
<!-- Primary Button -->
<button class="
  inline-flex items-center justify-center gap-2
  bg-primary-500 text-white
  px-4 py-2 rounded-md
  font-medium text-sm
  hover:bg-primary-600 active:bg-primary-700
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
  transition-colors
">
  <svg class="w-4 h-4"><!-- icon --></svg>
  Primary Button
</button>

<!-- Secondary Button -->
<button class="
  inline-flex items-center justify-center gap-2
  bg-gray-100 text-gray-900
  px-4 py-2 rounded-md
  font-medium text-sm
  hover:bg-gray-200 active:bg-gray-300
  focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2
  transition-colors
">
  Secondary
</button>

<!-- Ghost Button -->
<button class="
  inline-flex items-center justify-center gap-2
  text-primary-600
  px-4 py-2 rounded-md
  font-medium text-sm
  hover:bg-primary-50 active:bg-primary-100
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
  transition-colors
">
  Ghost Button
</button>

<!-- Icon Button -->
<button class="
  p-2 rounded-full
  text-gray-500 hover:text-gray-700
  hover:bg-gray-100 active:bg-gray-200
  focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2
  transition-colors
">
  <svg class="w-5 h-5"><!-- icon --></svg>
  <span class="sr-only">Action label</span>
</button>
```

### List Items

```html
<ul class="divide-y divide-gray-200">
  <li class="flex items-center gap-4 p-4 hover:bg-gray-50 transition-colors">
    <div class="flex-shrink-0">
      <img src="avatar.jpg" alt="" class="w-10 h-10 rounded-full" />
    </div>
    <div class="flex-1 min-w-0">
      <p class="text-sm font-medium text-gray-900 truncate">List Item Title</p>
      <p class="text-sm text-gray-500 truncate">Supporting text</p>
    </div>
    <div class="flex-shrink-0">
      <svg class="w-5 h-5 text-gray-400"><!-- chevron --></svg>
    </div>
  </li>
</ul>
```

### Form Input

```html
<div class="space-y-1">
  <label for="email" class="block text-sm font-medium text-gray-700">
    Email address
  </label>
  <input
    type="email"
    id="email"
    class="
      block w-full px-3 py-2
      border border-gray-300 rounded-md
      text-gray-900 placeholder-gray-400
      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
      disabled:bg-gray-50 disabled:text-gray-500
      sm:text-sm
    "
    placeholder="you@example.com"
  />
  <p class="text-sm text-gray-500">We'll never share your email.</p>
</div>
```

### Navigation

```html
<nav class="flex items-center gap-1">
  <a href="#" class="
    px-3 py-2 rounded-md text-sm font-medium
    text-gray-900 bg-gray-100
  ">
    Home
  </a>
  <a href="#" class="
    px-3 py-2 rounded-md text-sm font-medium
    text-gray-600 hover:text-gray-900 hover:bg-gray-50
    transition-colors
  ">
    Products
  </a>
  <a href="#" class="
    px-3 py-2 rounded-md text-sm font-medium
    text-gray-600 hover:text-gray-900 hover:bg-gray-50
    transition-colors
  ">
    About
  </a>
</nav>
```

## Responsive Design

### Breakpoint Prefixes

| Prefix | Min Width | Usage |
|--------|-----------|-------|
| `sm:` | 640px | Small screens |
| `md:` | 768px | Medium screens |
| `lg:` | 1024px | Large screens |
| `xl:` | 1280px | Extra large |
| `2xl:` | 1536px | 2x extra large |

### Responsive Layout Example

```html
<div class="
  grid grid-cols-1 gap-4
  sm:grid-cols-2 sm:gap-6
  lg:grid-cols-3 lg:gap-8
">
  <div class="bg-white rounded-lg shadow p-4">Card 1</div>
  <div class="bg-white rounded-lg shadow p-4">Card 2</div>
  <div class="bg-white rounded-lg shadow p-4">Card 3</div>
</div>
```

## Dark Mode

```html
<div class="
  bg-white dark:bg-gray-800
  text-gray-900 dark:text-gray-100
  border border-gray-200 dark:border-gray-700
  rounded-lg p-4
">
  <h3 class="font-medium">Dark mode compatible</h3>
  <p class="text-gray-600 dark:text-gray-400 mt-1">
    Supporting text with dark mode
  </p>
</div>
```

## Component Extraction with @apply

For repeated patterns, use `@apply` in CSS:

```css
/* components.css */
@layer components {
  .btn {
    @apply inline-flex items-center justify-center gap-2
           px-4 py-2 rounded-md
           font-medium text-sm
           transition-colors
           focus:outline-none focus:ring-2 focus:ring-offset-2;
  }

  .btn-primary {
    @apply btn bg-primary-500 text-white
           hover:bg-primary-600 active:bg-primary-700
           focus:ring-primary-500;
  }

  .btn-secondary {
    @apply btn bg-gray-100 text-gray-900
           hover:bg-gray-200 active:bg-gray-300
           focus:ring-gray-500;
  }

  .card {
    @apply bg-white rounded-lg shadow-md p-4;
  }

  .input {
    @apply block w-full px-3 py-2
           border border-gray-300 rounded-md
           text-gray-900 placeholder-gray-400
           focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
           sm:text-sm;
  }
}
```

## Accessibility

Include accessibility utilities:

```html
<!-- Screen reader only text -->
<span class="sr-only">Description for screen readers</span>

<!-- Focus visible states -->
<button class="focus-visible:ring-2 focus-visible:ring-primary-500">
  Button
</button>

<!-- Reduced motion -->
<div class="motion-safe:animate-bounce motion-reduce:animate-none">
  Animated element
</div>
```

## See Also

- `design-tokens-extraction` skill - Extract tokens first
- `design-token-tailwind` style - Tailwind config generation
- `component-spec` style - Documentation format
