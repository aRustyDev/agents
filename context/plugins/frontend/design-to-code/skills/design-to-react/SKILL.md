---
name: design-to-react
description: Convert design specifications from Figma, Sketch, or Penpot to React components with CSS modules or styled-components
created: 2026-02-22
updated: 2026-02-22
tags: [design, react, typescript, css-modules, styled-components]
requires: design-tokens-extraction
---

# Design to React

Convert design component specifications to React components.

## Overview

This skill transforms design specifications into idiomatic React components with TypeScript support, proper prop interfaces, and flexible styling approaches.

**This skill covers:**

- Converting design frames to React component hierarchy
- Mapping design properties to CSS/styled-components
- Generating TypeScript interfaces for props
- Creating Storybook stories for documentation

**This skill does NOT cover:**

- Design token extraction (see `design-tokens-extraction` skill)
- State management (Redux, Zustand, etc.)
- Data fetching and API integration

## Quick Reference

### Design to React Mapping

| Design Element | React Component |
|----------------|-----------------|
| Frame/Group | `<div>` with className |
| Auto-layout horizontal | Flexbox `flex-direction: row` |
| Auto-layout vertical | Flexbox `flex-direction: column` |
| Text | `<span>` or `<p>` |
| Rectangle | `<div>` with border-radius |
| Image | `<img>` or CSS background |
| Button | `<button>` |
| Input | `<input>` |

### Styling Approaches

| Approach | When to Use |
|----------|-------------|
| CSS Modules | Default, good isolation |
| styled-components | Dynamic styling needs |
| Tailwind | Project uses Tailwind |
| Inline styles | Simple, one-off styles |

## Workflow: Convert Design Component

### Step 1: Analyze Design Structure

Read the design component and identify:

- Component hierarchy and nesting
- Layout direction and spacing
- Interactive elements
- Variants and states

### Step 2: Generate TypeScript Interface

```typescript
interface ComponentNameProps {
  /** Primary content */
  title: string;
  /** Optional secondary content */
  subtitle?: string;
  /** Size variant */
  size?: 'small' | 'medium' | 'large';
  /** Click handler */
  onClick?: () => void;
  /** Additional CSS classes */
  className?: string;
}
```

### Step 3: Generate Component Code

**With CSS Modules:**

```tsx
import React from 'react';
import styles from './ComponentName.module.css';
import clsx from 'clsx';

interface ComponentNameProps {
  title: string;
  subtitle?: string;
  size?: 'small' | 'medium' | 'large';
  onClick?: () => void;
  className?: string;
}

export const ComponentName: React.FC<ComponentNameProps> = ({
  title,
  subtitle,
  size = 'medium',
  onClick,
  className,
}) => {
  return (
    <div
      className={clsx(styles.container, styles[size], className)}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <span className={styles.title}>{title}</span>
      {subtitle && <span className={styles.subtitle}>{subtitle}</span>}
    </div>
  );
};
```

**CSS Module:**

```css
.container {
  display: flex;
  flex-direction: column;
  padding: var(--spacing-md);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color var(--duration-fast);
}

.container:hover {
  background: var(--color-surface-hover);
}

.title {
  font: var(--font-body-medium);
  color: var(--color-text);
}

.subtitle {
  font: var(--font-body-small);
  color: var(--color-text-secondary);
}

/* Size variants */
.small {
  padding: var(--spacing-sm);
}

.medium {
  padding: var(--spacing-md);
}

.large {
  padding: var(--spacing-lg);
}
```

**With styled-components:**

```tsx
import React from 'react';
import styled from 'styled-components';

interface ContainerProps {
  $size: 'small' | 'medium' | 'large';
}

const Container = styled.div<ContainerProps>`
  display: flex;
  flex-direction: column;
  padding: ${({ $size }) => {
    switch ($size) {
      case 'small': return 'var(--spacing-sm)';
      case 'large': return 'var(--spacing-lg)';
      default: return 'var(--spacing-md)';
    }
  }};
  background: var(--color-surface);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color var(--duration-fast);

  &:hover {
    background: var(--color-surface-hover);
  }
`;

const Title = styled.span`
  font: var(--font-body-medium);
  color: var(--color-text);
`;

const Subtitle = styled.span`
  font: var(--font-body-small);
  color: var(--color-text-secondary);
`;

export const ComponentName: React.FC<ComponentNameProps> = ({
  title,
  subtitle,
  size = 'medium',
  onClick,
}) => {
  return (
    <Container $size={size} onClick={onClick}>
      <Title>{title}</Title>
      {subtitle && <Subtitle>{subtitle}</Subtitle>}
    </Container>
  );
};
```

### Step 4: Generate Storybook Story

```tsx
import type { Meta, StoryObj } from '@storybook/react';
import { ComponentName } from './ComponentName';

const meta: Meta<typeof ComponentName> = {
  title: 'Components/ComponentName',
  component: ComponentName,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: 'select',
      options: ['small', 'medium', 'large'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof ComponentName>;

export const Default: Story = {
  args: {
    title: 'Component Title',
    subtitle: 'Supporting text',
  },
};

export const Small: Story = {
  args: {
    ...Default.args,
    size: 'small',
  },
};

export const Large: Story = {
  args: {
    ...Default.args,
    size: 'large',
  },
};

export const WithoutSubtitle: Story = {
  args: {
    title: 'Title Only',
  },
};
```

## Common Patterns

### Card Component

```tsx
import React from 'react';
import styles from './Card.module.css';

interface CardProps {
  children: React.ReactNode;
  variant?: 'elevated' | 'outlined' | 'filled';
  padding?: 'none' | 'small' | 'medium' | 'large';
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'elevated',
  padding = 'medium',
  onClick,
}) => {
  const Component = onClick ? 'button' : 'div';

  return (
    <Component
      className={`${styles.card} ${styles[variant]} ${styles[`padding-${padding}`]}`}
      onClick={onClick}
    >
      {children}
    </Component>
  );
};
```

### Button Component

```tsx
import React from 'react';
import styles from './Button.module.css';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  leftIcon,
  rightIcon,
  onClick,
}) => {
  return (
    <button
      className={`${styles.button} ${styles[variant]} ${styles[size]}`}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading && <span className={styles.spinner} />}
      {!loading && leftIcon && <span className={styles.icon}>{leftIcon}</span>}
      <span>{children}</span>
      {!loading && rightIcon && <span className={styles.icon}>{rightIcon}</span>}
    </button>
  );
};
```

## Token Integration

Reference design tokens via CSS custom properties:

```css
.component {
  /* Colors */
  background: var(--color-surface);
  color: var(--color-text);
  border-color: var(--color-border);

  /* Typography */
  font-family: var(--font-family-sans);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);

  /* Spacing */
  padding: var(--spacing-md);
  gap: var(--spacing-sm);

  /* Shape */
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);

  /* Motion */
  transition: all var(--duration-fast) var(--easing-default);
}
```

## Naming Conventions

| Design Name | React Component | File |
|-------------|-----------------|------|
| `Button/Primary` | `PrimaryButton` or `Button` | `Button.tsx` |
| `Card - Article` | `ArticleCard` | `ArticleCard.tsx` |
| `Input/Text Field` | `TextField` | `TextField.tsx` |
| `List Item/Default` | `ListItem` | `ListItem.tsx` |

## File Structure

```text
components/
├── Button/
│   ├── Button.tsx
│   ├── Button.module.css
│   ├── Button.stories.tsx
│   ├── Button.test.tsx
│   └── index.ts
├── Card/
│   ├── Card.tsx
│   ├── Card.module.css
│   └── index.ts
└── index.ts
```

## See Also

- `design-tokens-extraction` skill - Extract tokens first
- `design-token-css` style - CSS custom properties
- `component-spec` style - Documentation format
