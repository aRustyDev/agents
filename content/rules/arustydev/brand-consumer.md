# Consuming aRustyDev Brand Assets

This rule applies to any project that needs to use brand assets from `brand.arusty.dev`.

## Quick Start

```html
<!-- Import a theme (pick one) -->
<link rel="stylesheet" href="https://brand.arusty.dev/assets/colors/themes/forest-night.css">

<!-- Set mode on html element -->
<html data-theme="dark">
```

Available themes: `deep-water`, `forest-night`, `twilight`

---

## Color System

### How It Works

1. **Pick a theme** - Each theme has both light and dark mode colors
2. **Import the CSS** - One file per theme
3. **Set data-theme** - Use `light` or `dark` on the `<html>` element

### Theme Files

```
https://brand.arusty.dev/assets/colors/themes/
├── deep-water.css      # Blue ocean theme
├── forest-night.css    # Green forest theme
└── twilight.css        # Teal/amber theme
```

### CSS Selectors in Theme Files

Each theme file contains:
- `:root, [data-theme="light"]` - Light mode colors (default)
- `[data-theme="dark"]` - Dark mode colors
- `@media (prefers-color-scheme: dark)` - Auto dark when no `data-theme` set

---

## Color Tokens

All colors use the `--color-` prefix:

| Token | Purpose |
|-------|---------|
| `--color-background` | Page/app background |
| `--color-surface` | Card/container background |
| `--color-surface-elevated` | Elevated cards, modals |
| `--color-primary` | Primary actions, links |
| `--color-primary-muted` | Hover/disabled primary |
| `--color-accent` | Secondary emphasis |
| `--color-accent-muted` | Hover/disabled accent |
| `--color-warm` | Highlights, notifications |
| `--color-warm-muted` | Hover/disabled warm |
| `--color-text` | Primary text |
| `--color-text-muted` | Secondary text |
| `--color-text-subtle` | Tertiary/hint text |
| `--color-border` | Borders, dividers |
| `--color-border-muted` | Subtle borders |

### Semantic Colors

| Token | Purpose |
|-------|---------|
| `--color-success` | Success states |
| `--color-warning` | Warning states |
| `--color-error` | Error states |
| `--color-info` | Informational states |

### Usage in CSS

```css
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.card-title {
  color: var(--color-primary);
}

.card-subtitle {
  color: var(--color-text-muted);
}
```

---

## Theme Switching

### Option 1: Theme Switcher Utility (Recommended)

Include the utility script for full runtime control:

```html
<script src="https://brand.arusty.dev/assets/js/theme-switcher.js"></script>
<script>
  // Initialize with a theme
  BrandTheme.init('forest-night');

  // Or with options
  BrandTheme.init({
    theme: 'forest-night',
    mode: 'dark',              // 'light', 'dark', or 'auto'
    persist: true,             // save to localStorage (default: true)
    onThemeChange: (theme) => console.log('Theme:', theme),
    onModeChange: (mode) => console.log('Mode:', mode),
  });
</script>
```

**API:**

| Method | Description |
|--------|-------------|
| `BrandTheme.init(config)` | Initialize with theme/mode/options |
| `BrandTheme.theme('twilight')` | Switch to a different theme |
| `BrandTheme.mode('dark')` | Set mode: `'light'`, `'dark'`, or `'auto'` |
| `BrandTheme.toggle()` | Toggle between light and dark |
| `BrandTheme.getTheme()` | Get current theme name |
| `BrandTheme.getMode()` | Get current mode setting |
| `BrandTheme.getEffectiveMode()` | Get actual mode (resolves 'auto') |
| `BrandTheme.themes` | Array of available themes |

**Example: Theme selector dropdown**

```html
<select onchange="BrandTheme.theme(this.value)">
  <option value="deep-water">Deep Water</option>
  <option value="forest-night">Forest Night</option>
  <option value="twilight">Twilight</option>
</select>

<button onclick="BrandTheme.toggle()">Toggle Dark/Light</button>
```

### Option 2: Manual Control

For simpler setups without the utility:

```js
// Toggle light/dark mode
function toggleMode() {
  const current = document.documentElement.getAttribute('data-theme');
  document.documentElement.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark');
}

// Switch themes manually
function setTheme(themeName) {
  const link = document.querySelector('link[href*="brand.arusty.dev/assets/colors/themes"]');
  link.href = `https://brand.arusty.dev/assets/colors/themes/${themeName}.css`;
}
```

### Auto Mode (System Preference)

If no `data-theme` attribute is set, the theme respects `prefers-color-scheme`:

```html
<!-- No data-theme = follows system preference -->
<html>
```

### Prevent Flash on Load

```html
<head>
  <!-- Option A: With theme-switcher.js (handles everything) -->
  <script src="https://brand.arusty.dev/assets/js/theme-switcher.js"></script>
  <script>BrandTheme.init('forest-night');</script>

  <!-- Option B: Manual (if not using theme-switcher.js) -->
  <script>
    const saved = localStorage.getItem('brand-mode') ||
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', saved);
  </script>
  <link rel="stylesheet" href="https://brand.arusty.dev/assets/colors/themes/forest-night.css">
</head>
```

---

## Changing Themes

### Runtime (User Choice / Seasonal)

With the theme switcher utility:

```js
// Switch themes at runtime
BrandTheme.theme('twilight');
BrandTheme.theme('forest-night');
BrandTheme.theme('deep-water');
```

### Build-time (Hardcoded)

Change the import URL in source and redeploy:

```html
<link rel="stylesheet" href="https://brand.arusty.dev/assets/colors/themes/twilight.css">
```

---

## Logos

### CDN URLs

```
https://brand.arusty.dev/assets/images/logos/logo-{variant}.{ext}
```

| Variant | Description |
|---------|-------------|
| `color` | Full color logo |
| `color-transparent` | Color, transparent background |
| `color-hires` | High resolution PNG |
| `color-transparent-hires` | High res, transparent |
| `grayscale` | Grayscale version |
| `grayscale-inverted` | Light grayscale (for dark bg) |
| `grayscale-hires` | High res grayscale |
| `grayscale-transparent-hires` | High res grayscale, transparent |

### Examples

```html
<!-- SVG (preferred for web) -->
<img src="https://brand.arusty.dev/assets/images/logos/logo-color.svg" alt="aRustyDev">

<!-- PNG for contexts requiring raster -->
<img src="https://brand.arusty.dev/assets/images/logos/logo-color-hires.png" alt="aRustyDev">
```

---

## Monograms / Favicons

```
https://brand.arusty.dev/assets/images/monograms/monogram-{variant}.png
```

| Variant | Use Case |
|---------|----------|
| `16px` | Favicon |
| `hq` | App icons |
| `black-16px` | Favicon (light backgrounds) |
| `black-hq` | App icons (light backgrounds) |

```html
<link rel="icon" type="image/png" sizes="16x16"
      href="https://brand.arusty.dev/assets/images/monograms/monogram-16px.png">
```

---

## Fonts

```
https://brand.arusty.dev/assets/fonts/{font}.ttf
```

| Font | Purpose |
|------|---------|
| `Krona One.ttf` | Headings, display |
| `Chivo Mono.ttf` | Code, monospace |

```css
@font-face {
  font-family: 'Krona One';
  src: url('https://brand.arusty.dev/assets/fonts/Krona One.ttf') format('truetype');
  font-display: swap;
}

@font-face {
  font-family: 'Chivo Mono';
  src: url('https://brand.arusty.dev/assets/fonts/Chivo Mono.ttf') format('truetype');
  font-display: swap;
}
```

---

## JSON API (Programmatic Access)

For build-time generation or advanced use cases:

```js
const palette = await fetch('https://brand.arusty.dev/assets/colors/palette.json')
  .then(r => r.json());

// Get a specific theme's dark mode colors
const colors = palette.themes['forest-night'].colors;
console.log(colors.primary); // "#238636"

// Get light mode colors
const lightColors = palette.themes['forest-night-light'].colors;
```

---

## Framework Integration

### Tailwind CSS

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        background: 'var(--color-background)',
        surface: 'var(--color-surface)',
        primary: 'var(--color-primary)',
        accent: 'var(--color-accent)',
        warm: 'var(--color-warm)',
      }
    }
  }
}
```

### Astro / AstroPaper

```astro
---
// Layout.astro
---
<html data-theme="dark">
  <head>
    <link rel="stylesheet" href="https://brand.arusty.dev/assets/colors/themes/forest-night.css">
  </head>
</html>
```

The standard `data-theme="light"` / `data-theme="dark"` selectors work directly with AstroPaper and similar frameworks.

---

## Best Practices

1. **One theme import per site** - Pick a theme, use light/dark toggle for mode
2. **Use CSS variables** - Never hardcode hex values
3. **Set data-theme early** - In `<head>` before CSS loads to prevent flash
4. **Use SVG logos** for web - PNG only when raster required
5. **Test both modes** - Verify light and dark work correctly

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Colors not changing | Ensure `data-theme` is on `<html>`, not `<body>` |
| Theme flicker on load | Set `data-theme` in `<head>` script before CSS |
| Wrong mode on refresh | Persist choice in localStorage, restore on load |
| CORS errors | Brand CDN allows all origins; check URL typos |
