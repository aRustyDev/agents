---
name: typescript-dev
description: TypeScript development guidelines and patterns. Use this skill when writing TypeScript code, creating React components with TypeScript, configuring tsconfig.json, using advanced types like generics or utility types, or when the user asks about TypeScript best practices.
---

# TypeScript Development Guidelines

## Compiler Configuration

### Strict Mode Settings

Always enable strict mode in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true
  }
}
```

### Path Aliases

Configure path aliases for clean imports:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "~types": ["src/types"],
      "~components/*": ["src/components/*"],
      "~features/*": ["src/features/*"]
    }
  }
}
```

## Type Patterns

### Prefer `unknown` Over `any`

```typescript
// Avoid
function parse(input: any): object { ... }

// Prefer
function parse(input: unknown): object {
  if (typeof input !== 'string') {
    throw new Error('Expected string input');
  }
  return JSON.parse(input);
}
```

### Use Type Guards Instead of Assertions

```typescript
// Avoid
const user = data as User;

// Prefer
function isUser(data: unknown): data is User {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'name' in data
  );
}

if (isUser(data)) {
  console.log(data.name); // Type-safe access
}
```

### Discriminated Unions for State

```typescript
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

function handleState<T>(state: AsyncState<T>) {
  switch (state.status) {
    case 'idle':
      return null;
    case 'loading':
      return <Spinner />;
    case 'success':
      return <Data value={state.data} />;
    case 'error':
      return <ErrorMessage error={state.error} />;
  }
}
```

### Generic Constraints

```typescript
// Constrain generics to specific shapes
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// Constrain to types with specific methods
function sortItems<T extends { compareTo(other: T): number }>(items: T[]): T[] {
  return [...items].sort((a, b) => a.compareTo(b));
}
```

### Utility Types

| Type | Purpose | Example |
|------|---------|---------|
| `Partial<T>` | All properties optional | `Partial<User>` for updates |
| `Required<T>` | All properties required | `Required<Config>` for validation |
| `Pick<T, K>` | Select specific properties | `Pick<User, 'id' \| 'name'>` |
| `Omit<T, K>` | Exclude specific properties | `Omit<User, 'password'>` |
| `Record<K, V>` | Object with typed keys/values | `Record<string, number>` |
| `NonNullable<T>` | Exclude null/undefined | `NonNullable<string \| null>` |

### Mapped Types

```typescript
// Make all properties readonly
type Immutable<T> = {
  readonly [K in keyof T]: T[K] extends object ? Immutable<T[K]> : T[K];
};

// Make specific properties optional
type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// Extract function parameter types
type FirstParam<T> = T extends (first: infer P, ...args: any[]) => any ? P : never;
```

### Conditional Types

```typescript
// Extract array element type
type ArrayElement<T> = T extends (infer E)[] ? E : never;

// Extract promise result type
type Awaited<T> = T extends Promise<infer R> ? Awaited<R> : T;

// Filter union types
type ExtractStrings<T> = T extends string ? T : never;
```

## React + TypeScript Patterns

### Component Definition

```typescript
// Define props interface separately
interface ButtonProps {
  variant: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}

// Function component (React 19: React.FC discouraged)
function Button({ variant, size = 'md', disabled, onClick, children }: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

### Refs (React 19+)

```typescript
// React 19: ref is a regular prop, forwardRef not required
interface InputProps {
  ref?: React.Ref<HTMLInputElement>;
  label: string;
  value: string;
  onChange: (value: string) => void;
}

function Input({ ref, label, value, onChange }: InputProps) {
  return (
    <label>
      {label}
      <input ref={ref} value={value} onChange={(e) => onChange(e.target.value)} />
    </label>
  );
}
```

### Hooks with Types

```typescript
// useState with explicit type
const [user, setUser] = useState<User | null>(null);

// useRef with DOM element
const inputRef = useRef<HTMLInputElement>(null);

// useCallback with typed parameters
const handleSubmit = useCallback((data: FormData) => {
  submitForm(data);
}, [submitForm]);

// useMemo for derived state
const sortedItems = useMemo(() =>
  [...items].sort((a, b) => a.name.localeCompare(b.name)),
  [items]
);
```

### Event Handlers

```typescript
// Form events
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setValue(e.target.value);
};

const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  // process form
};

// Mouse/keyboard events
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
  console.log(e.clientX, e.clientY);
};

const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
  if (e.key === 'Enter') {
    submit();
  }
};
```

### Context with Types

```typescript
interface ThemeContextValue {
  theme: 'light' | 'dark';
  toggle: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

## Code Organization

### Feature-Based Structure

```
src/
├── features/
│   └── auth/
│       ├── api/              # API calls
│       ├── components/       # Feature components
│       ├── hooks/           # Feature hooks
│       ├── types/           # Feature types
│       └── index.ts         # Public exports
├── components/              # Shared components
├── hooks/                   # Shared hooks
├── types/                   # Global types
├── utils/                   # Utility functions
└── lib/                     # Third-party integrations
```

### Barrel Exports

```typescript
// features/auth/index.ts
export { LoginForm } from './components/LoginForm';
export { useAuth } from './hooks/useAuth';
export type { User, AuthState } from './types';
```

### Type-Only Imports

```typescript
// Prefer type-only imports for types
import type { User, AuthState } from './types';
import { validateUser } from './utils';
```

## Validation with Zod

```typescript
import { z } from 'zod';

// Define schema
const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1).max(100),
  role: z.enum(['admin', 'user', 'guest']),
  createdAt: z.coerce.date(),
});

// Infer TypeScript type from schema
type User = z.infer<typeof UserSchema>;

// Validate at runtime
function parseUser(data: unknown): User {
  return UserSchema.parse(data);
}

// Safe parse (doesn't throw)
function tryParseUser(data: unknown): User | null {
  const result = UserSchema.safeParse(data);
  return result.success ? result.data : null;
}
```

## Testing Patterns

### Type-Safe Mocks

```typescript
import { vi, type MockedFunction } from 'vitest';

// Mock with proper types
const mockFetch = vi.fn() as MockedFunction<typeof fetch>;

// Factory for test data
function createUser(overrides: Partial<User> = {}): User {
  return {
    id: crypto.randomUUID(),
    name: 'Test User',
    email: 'test@example.com',
    ...overrides,
  };
}
```

### Testing React Components

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('submits form with valid data', async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn();

  render(<LoginForm onSubmit={onSubmit} />);

  await user.type(screen.getByLabelText('Email'), 'test@example.com');
  await user.type(screen.getByLabelText('Password'), 'password123');
  await user.click(screen.getByRole('button', { name: 'Login' }));

  expect(onSubmit).toHaveBeenCalledWith({
    email: 'test@example.com',
    password: 'password123',
  });
});
```

## Common Pitfalls

### Avoid Object Index Signatures Without Guards

```typescript
// Dangerous: assumes key exists
const value = obj[key]; // type is T | undefined with noUncheckedIndexedAccess

// Safe: check before access
if (key in obj) {
  const value = obj[key];
}
```

### Handle Promise Rejections

```typescript
// Avoid: unhandled rejection
async function fetchData() {
  const response = await fetch('/api/data');
  return response.json();
}

// Prefer: explicit error handling
async function fetchData(): Promise<Result<Data, Error>> {
  try {
    const response = await fetch('/api/data');
    if (!response.ok) {
      return { success: false, error: new Error(`HTTP ${response.status}`) };
    }
    return { success: true, data: await response.json() };
  } catch (error) {
    return { success: false, error: error instanceof Error ? error : new Error(String(error)) };
  }
}
```

### Avoid Enums, Use Const Objects

```typescript
// Avoid: enums have quirks
enum Status {
  Active = 'active',
  Inactive = 'inactive',
}

// Prefer: const object with as const
const Status = {
  Active: 'active',
  Inactive: 'inactive',
} as const;

type Status = typeof Status[keyof typeof Status]; // 'active' | 'inactive'
```

### Type Narrowing in Callbacks

```typescript
// Problem: TypeScript doesn't narrow in callbacks
function process(value: string | null) {
  if (value === null) return;

  // value is string here, but...
  setTimeout(() => {
    // TypeScript can't guarantee value is still string
    console.log(value.toUpperCase()); // Error without storing in const
  }, 100);
}

// Solution: store narrowed value
function process(value: string | null) {
  if (value === null) return;
  const safeValue = value; // captured as string

  setTimeout(() => {
    console.log(safeValue.toUpperCase()); // OK
  }, 100);
}
```

## ESLint Configuration

```javascript
// eslint.config.js (flat config)
import tseslint from 'typescript-eslint';

export default tseslint.config(
  ...tseslint.configs.strictTypeChecked,
  {
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/prefer-nullish-coalescing': 'error',
      '@typescript-eslint/strict-boolean-expressions': 'error',
    },
  }
);
```

## See Also

- Reference: [advanced-types.md](references/advanced-types.md) - Deep dive into conditional and mapped types
- Reference: [react-patterns.md](references/react-patterns.md) - React 19 patterns with TypeScript
- Reference: [testing.md](references/testing.md) - Comprehensive testing strategies
