# Design Token Tailwind

Output style for generating Tailwind CSS configuration from design tokens. Use this style when converting extracted design tokens to a Tailwind theme configuration.

## Tailwind Config Format

Generate a `tailwind.config.js` theme extension:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      colors: {
        // Primary palette
        primary: {
          50: '#E3F2FD',
          100: '#BBDEFB',
          200: '#90CAF9',
          300: '#64B5F6',
          400: '#42A5F5',
          500: '#2196F3', // Default
          600: '#1E88E5',
          700: '#1976D2',
          800: '#1565C0',
          900: '#0D47A1',
        },

        // Semantic colors
        background: 'var(--color-background)',
        surface: 'var(--color-surface)',
        error: '#DC2626',
        success: '#16A34A',
        warning: '#D97706',
      },

      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },

      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem' }],
        sm: ['0.875rem', { lineHeight: '1.25rem' }],
        base: ['1rem', { lineHeight: '1.5rem' }],
        lg: ['1.125rem', { lineHeight: '1.75rem' }],
        xl: ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      },

      fontWeight: {
        regular: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
      },

      spacing: {
        // Custom spacing scale
        '4.5': '1.125rem',
        '18': '4.5rem',
      },

      borderRadius: {
        sm: '0.125rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
      },

      boxShadow: {
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
      },

      transitionDuration: {
        instant: '0ms',
        fast: '150ms',
        normal: '300ms',
        slow: '500ms',
      },
    },
  },
  plugins: [],
};
```

## CSS Variables Integration

For theming support, use CSS variables:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'rgb(var(--color-primary) / <alpha-value>)',
          50: 'rgb(var(--color-primary-50) / <alpha-value>)',
          500: 'rgb(var(--color-primary-500) / <alpha-value>)',
          900: 'rgb(var(--color-primary-900) / <alpha-value>)',
        },
        background: 'rgb(var(--color-background) / <alpha-value>)',
        surface: 'rgb(var(--color-surface) / <alpha-value>)',
        foreground: 'rgb(var(--color-foreground) / <alpha-value>)',
      },
    },
  },
};
```

With corresponding CSS:

```css
@tailwind base;

@layer base {
  :root {
    --color-primary: 33 150 243;
    --color-primary-50: 227 242 253;
    --color-primary-500: 33 150 243;
    --color-primary-900: 13 71 161;
    --color-background: 250 250 250;
    --color-surface: 255 255 255;
    --color-foreground: 33 33 33;
  }

  .dark {
    --color-background: 17 24 39;
    --color-surface: 31 41 55;
    --color-foreground: 249 250 251;
  }
}
```

## Complete Config Example

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx,html}'],
  darkMode: 'class',
  theme: {
    extend: {
      // From design tokens
      colors: {
        brand: {
          50: '#E8F5E9',
          100: '#C8E6C9',
          200: '#A5D6A7',
          300: '#81C784',
          400: '#66BB6A',
          500: '#4CAF50',
          600: '#43A047',
          700: '#388E3C',
          800: '#2E7D32',
          900: '#1B5E20',
        },
        accent: {
          50: '#FFF3E0',
          500: '#FF9800',
          900: '#E65100',
        },
      },

      fontFamily: {
        display: ['Poppins', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        code: ['Fira Code', 'monospace'],
      },

      fontSize: {
        // Design system typography
        'display-lg': ['3.5rem', { lineHeight: '1.1', fontWeight: '700' }],
        'display-md': ['2.75rem', { lineHeight: '1.2', fontWeight: '700' }],
        'heading-lg': ['2rem', { lineHeight: '1.25', fontWeight: '600' }],
        'heading-md': ['1.5rem', { lineHeight: '1.3', fontWeight: '600' }],
        'body-lg': ['1.125rem', { lineHeight: '1.6', fontWeight: '400' }],
        'body-md': ['1rem', { lineHeight: '1.5', fontWeight: '400' }],
        'body-sm': ['0.875rem', { lineHeight: '1.4', fontWeight: '400' }],
        'label-lg': ['0.875rem', { lineHeight: '1.4', fontWeight: '500' }],
        'label-md': ['0.75rem', { lineHeight: '1.3', fontWeight: '500' }],
      },

      spacing: {
        // Design system spacing scale
        'space-1': '0.25rem',
        'space-2': '0.5rem',
        'space-3': '0.75rem',
        'space-4': '1rem',
        'space-5': '1.25rem',
        'space-6': '1.5rem',
        'space-8': '2rem',
        'space-10': '2.5rem',
        'space-12': '3rem',
      },

      borderRadius: {
        'radius-sm': '0.25rem',
        'radius-md': '0.5rem',
        'radius-lg': '0.75rem',
        'radius-xl': '1rem',
        'radius-full': '9999px',
      },

      boxShadow: {
        'elevation-1': '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
        'elevation-2': '0 3px 6px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.12)',
        'elevation-3': '0 10px 20px rgba(0,0,0,0.15), 0 3px 6px rgba(0,0,0,0.10)',
        'elevation-4': '0 15px 25px rgba(0,0,0,0.15), 0 5px 10px rgba(0,0,0,0.05)',
      },

      animation: {
        'fade-in': 'fadeIn 300ms ease-out',
        'slide-up': 'slideUp 300ms ease-out',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
```

## Naming Conventions

| Design Token Format | Tailwind Config Key | Usage |
|---------------------|---------------------|-------|
| `color.primary.500` | `colors.primary.500` | `bg-primary-500` |
| `typography.fontSize.lg` | `fontSize.lg` | `text-lg` |
| `spacing.4` | `spacing.4` | `p-4`, `m-4` |
| `borderRadius.md` | `borderRadius.md` | `rounded-md` |
| `shadow.lg` | `boxShadow.lg` | `shadow-lg` |

## Plugin Integration

For complex design systems, create a Tailwind plugin:

```javascript
const plugin = require('tailwindcss/plugin');

module.exports = {
  plugins: [
    plugin(function({ addComponents, theme }) {
      addComponents({
        '.btn': {
          padding: `${theme('spacing.2')} ${theme('spacing.4')}`,
          borderRadius: theme('borderRadius.md'),
          fontWeight: theme('fontWeight.medium'),
          fontSize: theme('fontSize.sm'),
          transition: 'all 150ms ease-in-out',
        },
        '.btn-primary': {
          backgroundColor: theme('colors.primary.500'),
          color: '#ffffff',
          '&:hover': {
            backgroundColor: theme('colors.primary.600'),
          },
        },
        '.card': {
          backgroundColor: theme('colors.white'),
          borderRadius: theme('borderRadius.lg'),
          boxShadow: theme('boxShadow.md'),
          padding: theme('spacing.4'),
        },
      });
    }),
  ],
};
```

## Preset Export

For reusable design systems, export as a preset:

```javascript
// design-system-preset.js
module.exports = {
  theme: {
    extend: {
      colors: { /* ... */ },
      fontFamily: { /* ... */ },
      // ... all design tokens
    },
  },
  plugins: [
    // Design system plugins
  ],
};

// tailwind.config.js
module.exports = {
  presets: [require('./design-system-preset')],
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
};
```

## Usage Notes

1. Use `extend` to add tokens without replacing Tailwind defaults
2. Include `DEFAULT` key for base color values
3. Use CSS variables with `<alpha-value>` for opacity support
4. Group related tokens with descriptive key names
5. Consider creating a preset for reusable design systems
6. Add line height and font weight to fontSize definitions for typography tokens
