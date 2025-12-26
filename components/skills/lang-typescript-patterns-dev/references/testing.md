# TypeScript Testing Patterns

Comprehensive testing strategies for TypeScript applications using Vitest and Testing Library.

## Test Setup

### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: ['**/*.d.ts', '**/types/**', '**/test/**'],
    },
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
});
```

### Test Setup File

```typescript
// src/test/setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Cleanup after each test
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver
class MockIntersectionObserver {
  observe = vi.fn();
  disconnect = vi.fn();
  unobserve = vi.fn();
}
Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  value: MockIntersectionObserver,
});
```

## Type-Safe Mocking

### Function Mocks

```typescript
import { vi, type MockedFunction } from 'vitest';

// Mock a specific function
const mockFetch = vi.fn() as MockedFunction<typeof fetch>;

// Mock with implementation
const mockGetUser = vi.fn<[string], Promise<User>>().mockImplementation(
  async (id) => ({ id, name: 'Test User', email: 'test@example.com' })
);

// Mock return value
mockGetUser.mockResolvedValue({ id: '1', name: 'Mocked', email: 'mock@test.com' });

// Mock rejection
mockGetUser.mockRejectedValue(new Error('Network error'));
```

### Module Mocks

```typescript
// Mock entire module
vi.mock('@/lib/api', () => ({
  fetchUser: vi.fn(),
  fetchPosts: vi.fn(),
}));

// Import mocked module
import { fetchUser, fetchPosts } from '@/lib/api';

// Type as mocked
const mockedFetchUser = fetchUser as MockedFunction<typeof fetchUser>;
mockedFetchUser.mockResolvedValue({ id: '1', name: 'Test' });
```

### Partial Mocks

```typescript
// Mock only specific exports
vi.mock('@/lib/utils', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/utils')>();
  return {
    ...actual,
    formatDate: vi.fn(() => '2024-01-01'),
  };
});
```

## Test Data Factories

### Basic Factory

```typescript
function createUser(overrides: Partial<User> = {}): User {
  return {
    id: crypto.randomUUID(),
    name: 'Test User',
    email: 'test@example.com',
    role: 'user',
    createdAt: new Date().toISOString(),
    ...overrides,
  };
}

function createPost(overrides: Partial<Post> = {}): Post {
  return {
    id: crypto.randomUUID(),
    title: 'Test Post',
    content: 'Test content',
    authorId: crypto.randomUUID(),
    published: false,
    ...overrides,
  };
}

// Usage
const user = createUser({ role: 'admin' });
const posts = Array.from({ length: 5 }, () => createPost({ authorId: user.id }));
```

### Factory with Builder Pattern

```typescript
class UserBuilder {
  private user: User = {
    id: crypto.randomUUID(),
    name: 'Test User',
    email: 'test@example.com',
    role: 'user',
    createdAt: new Date().toISOString(),
  };

  withName(name: string): this {
    this.user.name = name;
    return this;
  }

  withEmail(email: string): this {
    this.user.email = email;
    return this;
  }

  asAdmin(): this {
    this.user.role = 'admin';
    return this;
  }

  build(): User {
    return { ...this.user };
  }
}

// Usage
const admin = new UserBuilder().withName('Admin').asAdmin().build();
```

## Component Testing

### Basic Component Test

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<Button onClick={handleClick}>Click me</Button>);
    await user.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### Testing with Context

```typescript
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { ThemedButton } from './ThemedButton';

function renderWithTheme(ui: React.ReactElement, theme: 'light' | 'dark' = 'light') {
  return render(
    <ThemeProvider initialTheme={theme}>
      {ui}
    </ThemeProvider>
  );
}

describe('ThemedButton', () => {
  it('applies dark theme styles', () => {
    renderWithTheme(<ThemedButton>Dark Button</ThemedButton>, 'dark');
    expect(screen.getByRole('button')).toHaveClass('dark-theme');
  });
});
```

### Testing Forms

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('submits with valid data', async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn();

    render(<LoginForm onSubmit={handleSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  it('shows validation errors for invalid email', async () => {
    const user = userEvent.setup();

    render(<LoginForm onSubmit={vi.fn()} />);

    await user.type(screen.getByLabelText(/email/i), 'invalid-email');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    expect(await screen.findByText(/invalid email/i)).toBeInTheDocument();
  });
});
```

## Hook Testing

### Testing Custom Hooks

```typescript
import { renderHook, act, waitFor } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  it('initializes with default value', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  it('initializes with custom value', () => {
    const { result } = renderHook(() => useCounter(10));
    expect(result.current.count).toBe(10);
  });

  it('increments count', () => {
    const { result } = renderHook(() => useCounter());

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it('decrements count', () => {
    const { result } = renderHook(() => useCounter(5));

    act(() => {
      result.current.decrement();
    });

    expect(result.current.count).toBe(4);
  });
});
```

### Testing Async Hooks

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useUser } from './useUser';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };
}

describe('useUser', () => {
  it('fetches user data', async () => {
    const mockUser = createUser();
    vi.mocked(fetchUser).mockResolvedValue(mockUser);

    const { result } = renderHook(() => useUser('123'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockUser);
  });

  it('handles error', async () => {
    const error = new Error('User not found');
    vi.mocked(fetchUser).mockRejectedValue(error);

    const { result } = renderHook(() => useUser('invalid'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBe(error);
  });
});
```

## API Testing

### Testing API Routes

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { createServer } from '@/test/server';

describe('POST /api/users', () => {
  const server = createServer();

  beforeEach(() => {
    server.reset();
  });

  it('creates a new user', async () => {
    const response = await server.inject({
      method: 'POST',
      url: '/api/users',
      payload: {
        name: 'New User',
        email: 'new@example.com',
      },
    });

    expect(response.statusCode).toBe(201);
    expect(response.json()).toMatchObject({
      id: expect.any(String),
      name: 'New User',
      email: 'new@example.com',
    });
  });

  it('returns 400 for invalid data', async () => {
    const response = await server.inject({
      method: 'POST',
      url: '/api/users',
      payload: {
        email: 'invalid-email',
      },
    });

    expect(response.statusCode).toBe(400);
    expect(response.json().errors).toBeDefined();
  });
});
```

## Integration Testing

### MSW for API Mocking

```typescript
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

const handlers = [
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      name: 'Test User',
      email: 'test@example.com',
    });
  }),

  http.post('/api/users', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json(
      { id: crypto.randomUUID(), ...body },
      { status: 201 }
    );
  }),
];

const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Override for specific test
it('handles server error', async () => {
  server.use(
    http.get('/api/users/:id', () => {
      return HttpResponse.json(
        { error: 'Internal server error' },
        { status: 500 }
      );
    })
  );

  // Test error handling...
});
```

## Snapshot Testing

```typescript
import { render } from '@testing-library/react';

describe('Card', () => {
  it('matches snapshot', () => {
    const { container } = render(
      <Card title="Test Card" description="Test description">
        Card content
      </Card>
    );

    expect(container.firstChild).toMatchSnapshot();
  });

  it('matches inline snapshot', () => {
    const { container } = render(<Badge>New</Badge>);

    expect(container.innerHTML).toMatchInlineSnapshot(
      `"<span class=\\"badge\\">New</span>"`
    );
  });
});
```

## Test Organization

### File Structure

```
src/
├── components/
│   └── Button/
│       ├── Button.tsx
│       ├── Button.test.tsx      # Unit tests
│       └── Button.stories.tsx   # Storybook stories
├── hooks/
│   └── useAuth/
│       ├── useAuth.ts
│       └── useAuth.test.ts
├── test/
│   ├── setup.ts                 # Global setup
│   ├── mocks/                   # Shared mocks
│   │   ├── handlers.ts          # MSW handlers
│   │   └── server.ts            # MSW server
│   └── utils/                   # Test utilities
│       ├── render.tsx           # Custom render
│       └── factories.ts         # Data factories
└── __tests__/
    └── integration/             # Integration tests
        └── auth-flow.test.tsx
```

### Custom Render Function

```typescript
// test/utils/render.tsx
import { render, type RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@/contexts/ThemeContext';

interface CustomRenderOptions extends RenderOptions {
  theme?: 'light' | 'dark';
  queryClient?: QueryClient;
}

function customRender(
  ui: React.ReactElement,
  {
    theme = 'light',
    queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } }),
    ...options
  }: CustomRenderOptions = {}
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <ThemeProvider initialTheme={theme}>
          {children}
        </ThemeProvider>
      </QueryClientProvider>
    );
  }

  return render(ui, { wrapper: Wrapper, ...options });
}

export * from '@testing-library/react';
export { customRender as render };
```
