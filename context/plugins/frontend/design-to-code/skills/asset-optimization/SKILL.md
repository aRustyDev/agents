---
name: asset-optimization
description: Optimize design assets for production deployment with format-specific compression, resolution scaling, and bundle optimization
tags: [design, assets, optimization, images, svg, performance]
---

# Asset Optimization

Optimize design assets for production deployment across platforms. Apply format-specific compression, resolution scaling, and bundle optimization techniques.

## Optimization Techniques

### SVG Optimization (SVGO)

Apply SVGO for vector graphics:

```bash
# Install
npm install -g svgo

# Optimize single file
svgo input.svg -o output.svg

# Optimize directory
svgo -f ./icons/ -o ./icons-optimized/

# With config
svgo --config svgo.config.js input.svg
```

**SVGO Configuration:**

```javascript
// svgo.config.js
module.exports = {
  multipass: true,
  plugins: [
    'preset-default',
    'removeDimensions',
    {
      name: 'removeAttrs',
      params: { attrs: '(stroke|fill)' }
    },
    {
      name: 'addAttributesToSVGElement',
      params: { attributes: [{ fill: 'currentColor' }] }
    }
  ]
}
```

**Typical Results:**

| Before | After | Savings |
|--------|-------|---------|
| 4.2 KB | 1.8 KB | 57% |
| 12 KB | 4.1 KB | 66% |
| 156 KB (set) | 42 KB | 73% |

### PNG Optimization

Use multiple tools for best results:

**pngquant (lossy):**

```bash
# Install
brew install pngquant

# Optimize with quality range
pngquant --quality=65-80 --speed 1 --output output.png input.png

# Batch process
pngquant --quality=65-80 --ext .png --force *.png
```

**oxipng (lossless):**

```bash
# Install
brew install oxipng

# Optimize
oxipng -o 4 -i 0 --strip safe input.png

# Batch with parallel processing
oxipng -o 4 -i 0 --strip safe -r ./images/
```

**Combined approach:**

```bash
# First lossy, then lossless
pngquant --quality=70-85 input.png -o temp.png
oxipng -o 4 temp.png -o output.png
```

**Typical Results:**

| Tool | Compression | Quality Loss |
|------|-------------|--------------|
| pngquant | 60-80% | Minimal (dithering) |
| oxipng | 5-15% | None |
| Combined | 65-85% | Minimal |

### WebP Conversion

Convert to WebP for web deployment:

```bash
# Install
brew install webp

# Convert from PNG
cwebp -q 80 input.png -o output.webp

# Convert from JPEG
cwebp -q 85 input.jpg -o output.webp

# Batch conversion
for f in *.png; do cwebp -q 80 "$f" -o "${f%.png}.webp"; done
```

**sharp (Node.js):**

```javascript
const sharp = require('sharp');

// Convert with quality
await sharp('input.png')
  .webp({ quality: 80, effort: 6 })
  .toFile('output.webp');

// Resize and convert
await sharp('input.png')
  .resize(800, 600)
  .webp({ quality: 85 })
  .toFile('output.webp');
```

**Typical Results:**

| Source | WebP Size | Savings |
|--------|-----------|---------|
| PNG 100KB | 28KB | 72% |
| JPEG 200KB | 85KB | 58% |
| PNG 1MB | 180KB | 82% |

### JPEG Optimization

Use MozJPEG for best quality/size:

```bash
# Install
brew install mozjpeg

# Optimize
cjpeg -quality 85 -optimize -progressive input.bmp > output.jpg

# From existing JPEG (re-compress)
djpeg input.jpg | cjpeg -quality 85 -optimize > output.jpg
```

**ImageMagick:**

```bash
# Convert and optimize
magick input.png -quality 85 -strip output.jpg

# Resize for different scales
magick input.png -resize 50% -quality 85 output@1x.jpg
magick input.png -quality 85 output@2x.jpg
```

### Resolution Scaling

Generate multi-resolution assets:

**iOS Scales:**

```bash
# From @3x source
magick hero@3x.png -resize 66.67% hero@2x.png
magick hero@3x.png -resize 33.33% hero@1x.png
```

**Android Densities:**

| Density | Scale | From xxxhdpi |
|---------|-------|--------------|
| mdpi | 0.25x | 25% |
| hdpi | 0.375x | 37.5% |
| xhdpi | 0.5x | 50% |
| xxhdpi | 0.75x | 75% |
| xxxhdpi | 1.0x | 100% |

```bash
# Generate all densities
magick icon-xxxhdpi.png -resize 75% icon-xxhdpi.png
magick icon-xxxhdpi.png -resize 50% icon-xhdpi.png
magick icon-xxxhdpi.png -resize 37.5% icon-hdpi.png
magick icon-xxxhdpi.png -resize 25% icon-mdpi.png
```

### Sprite Generation

Combine icons into sprite sheets:

**SVG Sprite:**

```bash
# Install
npm install -g svg-sprite

# Generate sprite
svg-sprite --mode symbol --dest ./sprites ./icons/*.svg
```

**Configuration:**

```javascript
// svg-sprite.config.js
module.exports = {
  mode: {
    symbol: {
      dest: '.',
      sprite: 'sprite.svg',
      inline: true
    }
  },
  svg: {
    xmlDeclaration: false,
    doctypeDeclaration: false
  }
}
```

**CSS Sprite (PNG):**

```bash
# Using spritesmith
npx spritesmith ./icons/*.png --destImage sprite.png --destCSS sprite.css
```

## Platform-Specific Guidelines

### iOS

**Asset Catalog Requirements:**

- Use PDF for vector icons (resolution independent)
- PNG for raster images at 1x, 2x, 3x
- Maximum 500KB per asset recommended
- sRGB color space

**Contents.json Template:**

```json
{
  "images": [
    { "filename": "icon.png", "scale": "1x", "idiom": "universal" },
    { "filename": "icon@2x.png", "scale": "2x", "idiom": "universal" },
    { "filename": "icon@3x.png", "scale": "3x", "idiom": "universal" }
  ],
  "info": { "author": "xcode", "version": 1 }
}
```

### Android

**Resource Guidelines:**

- VectorDrawable for icons (API 21+)
- WebP for images (API 18+, lossless API 14+)
- Maximum 100KB per drawable recommended

**VectorDrawable Conversion:**

```bash
# Convert SVG to VectorDrawable
npx svg2vectordrawable input.svg output.xml

# Or use vd-tool (Android SDK)
vd-tool -c -in icon.svg -out icon.xml
```

### Web

**Modern Approach:**

```html
<!-- Responsive images with fallback -->
<picture>
  <source srcset="hero.webp" type="image/webp">
  <source srcset="hero.jpg" type="image/jpeg">
  <img src="hero.jpg" alt="Hero" loading="lazy">
</picture>

<!-- Responsive with sizes -->
<img
  srcset="hero-400.webp 400w,
          hero-800.webp 800w,
          hero-1200.webp 1200w"
  sizes="(max-width: 600px) 400px,
         (max-width: 1200px) 800px,
         1200px"
  src="hero-800.webp"
  alt="Hero"
>
```

**Icon Usage:**

```html
<!-- SVG sprite usage -->
<svg class="icon">
  <use href="sprite.svg#icon-home"></use>
</svg>

<!-- Inline SVG for critical icons -->
<svg viewBox="0 0 24 24" fill="currentColor">
  <path d="M12 2L2 12h3v8h6v-6h2v6h6v-8h3L12 2z"/>
</svg>
```

## Quality Validation

### Visual Comparison

Compare before/after for quality loss:

```bash
# Generate comparison with ImageMagick
magick compare original.png optimized.png diff.png

# Calculate SSIM (structural similarity)
magick compare -metric SSIM original.png optimized.png null:
```

**Acceptable Thresholds:**

| Metric | Threshold | Meaning |
|--------|-----------|---------|
| SSIM | > 0.95 | Visually identical |
| PSNR | > 35 dB | Excellent quality |
| File size | < 500KB | Mobile-friendly |

### File Size Targets

| Asset Type | Target Size | Max Size |
|------------|-------------|----------|
| Icon (SVG) | < 5 KB | 10 KB |
| Icon (PNG) | < 10 KB | 20 KB |
| Thumbnail | < 50 KB | 100 KB |
| Hero image | < 200 KB | 500 KB |
| Background | < 300 KB | 800 KB |

## Automation Scripts

### Batch Optimization Script

```bash
#!/bin/bash
# optimize-assets.sh

INPUT_DIR="${1:-.}"
OUTPUT_DIR="${2:-./optimized}"

mkdir -p "$OUTPUT_DIR"

# Optimize SVGs
find "$INPUT_DIR" -name "*.svg" -exec sh -c '
  svgo "$1" -o "$2/$(basename "$1")"
' _ {} "$OUTPUT_DIR" \;

# Optimize PNGs
find "$INPUT_DIR" -name "*.png" -exec sh -c '
  pngquant --quality=70-85 "$1" -o "$2/$(basename "$1")"
  oxipng -o 4 "$2/$(basename "$1")"
' _ {} "$OUTPUT_DIR" \;

# Generate WebP
find "$OUTPUT_DIR" -name "*.png" -exec sh -c '
  cwebp -q 80 "$1" -o "${1%.png}.webp"
' _ {} \;

echo "Optimization complete: $OUTPUT_DIR"
```

### Node.js Pipeline

```javascript
const sharp = require('sharp');
const { optimize } = require('svgo');
const fs = require('fs').promises;
const path = require('path');

async function optimizeAssets(inputDir, outputDir) {
  const files = await fs.readdir(inputDir);

  for (const file of files) {
    const ext = path.extname(file).toLowerCase();
    const input = path.join(inputDir, file);
    const output = path.join(outputDir, file);

    if (ext === '.svg') {
      const svg = await fs.readFile(input, 'utf8');
      const result = optimize(svg, { multipass: true });
      await fs.writeFile(output, result.data);
    } else if (ext === '.png') {
      await sharp(input)
        .png({ quality: 80, compressionLevel: 9 })
        .toFile(output);

      // Also generate WebP
      await sharp(input)
        .webp({ quality: 80 })
        .toFile(output.replace('.png', '.webp'));
    }
  }
}
```

## Tool Dependencies

Install required tools:

```bash
# macOS
brew install svgo pngquant oxipng webp imagemagick mozjpeg

# npm tools
npm install -g svgo svg-sprite sharp
```

## Integration with Pipeline

The asset-optimization skill is used by:

- **asset-pipeline agent**: Applies optimizations during batch processing
- **/export-assets command**: Optimization flag triggers these techniques
- **design-system-architect**: Optimizes assets as part of full system generation
