---
name: export-assets
description: Export and optimize images, icons, and other assets from design files for target platforms
---

# Export Assets

Export images, icons, and other assets from design files, with optimization for target platforms.

## Arguments

- `<assets>` - Asset selection: `all`, `icons`, `images`, or specific names
- `--source` - Design source: `figma:key`, `sketch:path`, `penpot:id`
- `--platform` - Target platform: `ios`, `android`, `web`, `all`
- `--output` - Output directory (default: `./assets/`)
- `--format` - Image format: `png`, `svg`, `pdf`, `webp`
- `--optimize` - Optimization level: `none`, `standard`, `aggressive`
- `--prefix` - Filename prefix (e.g., `ic_` for icons)

## Workflow

### Step 1: Connect to Design Source

Connect via MCP and identify exportable assets:

**Figma:**

```text
Use figma MCP server
- Call get_file to read structure
- Identify components marked for export
- List images, icons, illustrations
```

**Sketch:**

```text
Use sketch-context MCP server
- Call get_exportable_layers
- List slices and export presets
```

### Step 2: Select Assets

Based on `<assets>` argument:

| Selector | Assets Included |
|----------|-----------------|
| `all` | All exportable assets |
| `icons` | Components in "Icons" folder/frame |
| `images` | Components in "Images" folder/frame |
| `<name>` | Specific named asset |
| `<pattern>` | Glob pattern match (e.g., `icon-*`) |

### Step 3: Configure Export

**Platform-specific settings:**

| Platform | Scales | Format | Optimization |
|----------|--------|--------|--------------|
| `ios` | 1x, 2x, 3x | PNG, PDF | ImageOptim |
| `android` | mdpi, hdpi, xhdpi, xxhdpi, xxxhdpi | PNG, WebP | pngquant |
| `web` | 1x, 2x | SVG, WebP, PNG | SVGO, sharp |

### Step 4: Export and Optimize

For each asset:

1. Export from design file at required scales
2. Apply format conversion if needed
3. Run optimization:
   - SVG: SVGO (remove metadata, optimize paths)
   - PNG: pngquant, oxipng (lossy/lossless compression)
   - WebP: sharp (quality optimization)
4. Generate asset catalog structure

### Step 5: Write Output

**iOS Output Structure:**

```text
Assets.xcassets/
├── Icons/
│   ├── icon-home.imageset/
│   │   ├── Contents.json
│   │   ├── icon-home.png      (1x)
│   │   ├── icon-home@2x.png   (2x)
│   │   └── icon-home@3x.png   (3x)
│   └── icon-settings.imageset/
│       └── ...
└── Images/
    └── hero-banner.imageset/
        └── ...
```

**Android Output Structure:**

```text
res/
├── drawable-mdpi/
│   ├── ic_home.png
│   └── ic_settings.png
├── drawable-hdpi/
│   └── ...
├── drawable-xhdpi/
│   └── ...
├── drawable-xxhdpi/
│   └── ...
└── drawable-xxxhdpi/
    └── ...
```

**Web Output Structure:**

```text
assets/
├── icons/
│   ├── home.svg
│   └── settings.svg
├── images/
│   ├── hero-banner.webp
│   ├── hero-banner@2x.webp
│   └── hero-banner.png  (fallback)
└── sprites/
    └── icons.svg  (sprite sheet)
```

## Examples

```bash
# Export all icons for iOS
/export-assets icons --source figma:abc123 --platform ios --output ./Assets.xcassets/

# Export specific image for web
/export-assets hero-banner --source figma:abc123 --platform web --format webp

# Export all assets for Android with aggressive optimization
/export-assets all --source sketch:./app.sketch --platform android --optimize aggressive

# Export icons as SVG sprite
/export-assets icons --source figma:abc123 --platform web --format svg --output ./public/sprites/
```

## Icon Search

Use the iconify MCP server to search for existing icons:

```bash
# Search for icons
/export-assets --search "arrow right"

# Results from iconify:
# - mdi:arrow-right
# - heroicons:arrow-right
# - lucide:arrow-right

# Use icon from library instead of exporting
/export-assets --use mdi:arrow-right --output ./assets/icons/
```

## Output Summary

```text
## Export Complete

### Assets Exported

| Type | Count | Size (Original) | Size (Optimized) | Savings |
|------|-------|-----------------|------------------|---------|
| Icons | 24 | 156 KB | 42 KB | 73% |
| Images | 8 | 2.4 MB | 890 KB | 63% |

### Files Created

| Platform | Directory | Files |
|----------|-----------|-------|
| iOS | Assets.xcassets/ | 96 |
| Android | res/drawable-*/ | 160 |
| Web | assets/ | 32 |

### Optimization Details

- SVG: SVGO removed 45% of path data
- PNG: pngquant achieved 68% compression
- WebP: 72% smaller than PNG equivalent
```

## Asset Naming

| Design Name | Output Name |
|-------------|-------------|
| `Icon/Arrow Right` | `ic_arrow_right` (Android), `arrow-right` (iOS/Web) |
| `Image - Hero Banner` | `hero_banner` |
| `Button/Primary/Icon` | `btn_primary_icon` |

Naming rules:

1. Convert to lowercase
2. Replace spaces/slashes with underscores (Android) or hyphens (iOS/Web)
3. Remove special characters
4. Apply platform prefix if specified

## Error Handling

| Error | Resolution |
|-------|------------|
| Asset not found | Check asset name/path in design file |
| Export failed | Verify asset is marked exportable |
| Optimization failed | Check tool dependencies (svgo, pngquant) |
| Invalid format | Use supported format for platform |

## Related Commands

- `/extract-tokens` - Extract design tokens
- `/generate-component` - Generate component code
- `/sync-design-system` - Sync design system
