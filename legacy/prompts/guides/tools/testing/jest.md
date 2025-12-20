---
name: Jest Testing Guide
module_type: guide
scope: temporary
priority: low
triggers: ["jest", "javascript testing", "jest mocks", "snapshot testing", "react testing", "jest coverage"]
dependencies: []
conflicts: []
version: 1.0.0
---

# Jest Testing Guide

## Purpose
Master Jest, the delightful JavaScript testing framework with a focus on simplicity, including mocking, snapshots, coverage, and React component testing.

## Installation and Setup

### Basic Setup
```bash
# Install Jest
npm install --save-dev jest

# For TypeScript support
npm install --save-dev jest @types/jest ts-jest typescript

# For React testing
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Update package.json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

### Configuration (jest.config.js)
```javascript
module.exports = {
  // Test environment
  testEnvironment: 'node', // or 'jsdom' for browser-like

  // File patterns
  testMatch: [
    '**/__tests__/**/*.[jt]s?(x)',
    '**/?(*.)+(spec|test).[jt]s?(x)'
  ],

  // Coverage settings
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/index.js',
    '!src/**/*.d.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },

  // Module paths
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss)$': 'identity-obj-proxy'
  },

  // Setup files
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],

  // Transform files
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest'
  }
};
```

### TypeScript Configuration
```javascript
// jest.config.js for TypeScript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  globals: {
    'ts-jest': {
      tsconfig: {
        jsx: 'react'
      }
    }
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  }
};
```

## Basic Testing

### Simple Test Cases
```javascript
// math.test.js
describe('Math operations', () => {
  test('adds 1 + 2 to equal 3', () => {
    expect(1 + 2).toBe(3);
  });

  test('multiplies 3 * 4 to equal 12', () => {
    expect(3 * 4).toBe(12);
  });
});

// Using test.each for multiple cases
test.each([
  [1, 1, 2],
  [1, 2, 3],
  [2, 1, 3],
])('add(%i, %i) returns %i', (a, b, expected) => {
  expect(a + b).toBe(expected);
});
```

### Testing Async Code
```javascript
// Promises
test('fetches user data', () => {
  return fetchUser(1).then(user => {
    expect(user.name).toBe('John Doe');
  });
});

// Async/Await
test('fetches user data async', async () => {
  const user = await fetchUser(1);
  expect(user.name).toBe('John Doe');
});

// Expect assertions count
test('fetches user data with assertions', async () => {
  expect.assertions(2);
  const user = await fetchUser(1);
  expect(user.name).toBe('John Doe');
  expect(user.id).toBe(1);
});

// Testing rejected promises
test('rejects with error', async () => {
  await expect(fetchUser(999)).rejects.toThrow('User not found');
});
```

### Testing Errors
```javascript
// Testing thrown errors
function divide(a, b) {
  if (b === 0) throw new Error('Division by zero');
  return a / b;
}

test('throws on division by zero', () => {
  expect(() => divide(10, 0)).toThrow();
  expect(() => divide(10, 0)).toThrow('Division by zero');
  expect(() => divide(10, 0)).toThrow(Error);
});
```

## Matchers

### Common Matchers
```javascript
// Exact equality
expect(2 + 2).toBe(4);

// Object equality
expect({name: 'John'}).toEqual({name: 'John'});

// Truthiness
expect('Hello').toBeTruthy();
expect('').toBeFalsy();
expect(null).toBeNull();
expect(undefined).toBeUndefined();
expect('Defined').toBeDefined();

// Numbers
expect(2 + 2).toBeGreaterThan(3);
expect(2 + 2).toBeGreaterThanOrEqual(4);
expect(2 + 2).toBeLessThan(5);
expect(0.1 + 0.2).toBeCloseTo(0.3);

// Strings
expect('team').not.toMatch(/I/);
expect('Christoph').toMatch(/stop/);

// Arrays and Iterables
expect(['Alice', 'Bob', 'Eve']).toContain('Alice');
expect(new Set(['Alice', 'Bob'])).toContain('Alice');
expect(['Alice', 'Bob']).toHaveLength(2);

// Objects
expect({name: 'John', age: 30}).toHaveProperty('name');
expect({name: 'John', age: 30}).toHaveProperty('name', 'John');
expect({a: {b: {c: 1}}}).toHaveProperty('a.b.c', 1);
```

### Custom Matchers
```javascript
// Define custom matcher
expect.extend({
  toBeWithinRange(received, floor, ceiling) {
    const pass = received >= floor && received <= ceiling;
    if (pass) {
      return {
        message: () =>
          `expected ${received} not to be within range ${floor} - ${ceiling}`,
        pass: true,
      };
    } else {
      return {
        message: () =>
          `expected ${received} to be within range ${floor} - ${ceiling}`,
        pass: false,
      };
    }
  },
});

// Use custom matcher
test('numeric ranges', () => {
  expect(100).toBeWithinRange(90, 110);
  expect(101).not.toBeWithinRange(0, 100);
});
```

## Mocking

### Function Mocks
```javascript
// Create a mock function
const mockFn = jest.fn();
mockFn('arg1', 'arg2');

// Check mock calls
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(1);
expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
expect(mockFn).toHaveBeenLastCalledWith('arg1', 'arg2');

// Mock return values
const mockReturnValue = jest.fn();
mockReturnValue.mockReturnValue(42);
expect(mockReturnValue()).toBe(42);

// Mock implementation
const mockImplementation = jest.fn((x, y) => x + y);
expect(mockImplementation(1, 2)).toBe(3);

// Chained methods
const mockChained = jest.fn();
mockChained
  .mockReturnValueOnce(1)
  .mockReturnValueOnce(2)
  .mockReturnValue(3);

expect(mockChained()).toBe(1);
expect(mockChained()).toBe(2);
expect(mockChained()).toBe(3);
expect(mockChained()).toBe(3);
```

### Module Mocks
```javascript
// Mock entire module
jest.mock('./config');

// Mock with factory
jest.mock('./config', () => ({
  apiUrl: 'http://localhost:3000',
  timeout: 5000
}));

// Partial mocking
jest.mock('./math', () => ({
  ...jest.requireActual('./math'),
  add: jest.fn((a, b) => a + b + 1) // Override just one function
}));

// Mock ES6 classes
jest.mock('./UserService');
import UserService from './UserService';

test('should create user', () => {
  const mockCreate = jest.fn();
  UserService.prototype.create = mockCreate;
  
  const service = new UserService();
  service.create({name: 'John'});
  
  expect(mockCreate).toHaveBeenCalledWith({name: 'John'});
});
```

### Mocking Timers
```javascript
// Enable fake timers
jest.useFakeTimers();

test('calls callback after 1 second', () => {
  const callback = jest.fn();
  setTimeout(callback, 1000);

  // At this point, callback hasn't been called
  expect(callback).not.toHaveBeenCalled();

  // Fast-forward time
  jest.advanceTimersByTime(1000);
  expect(callback).toHaveBeenCalledTimes(1);
});

// Run all timers
jest.runAllTimers();

// Run only pending timers
jest.runOnlyPendingTimers();

// Restore real timers
jest.useRealTimers();
```

## Snapshot Testing

### Basic Snapshots
```javascript
// Component snapshot
test('renders correctly', () => {
  const tree = renderer
    .create(<Button label="Click me" />)
    .toJSON();
  expect(tree).toMatchSnapshot();
});

// Object snapshot
test('user object structure', () => {
  const user = {
    id: 1,
    name: 'John Doe',
    createdAt: new Date('2024-01-15')
  };
  expect(user).toMatchSnapshot({
    createdAt: expect.any(Date) // Dynamic matchers
  });
});
```

### Inline Snapshots
```javascript
test('inline snapshot', () => {
  const user = {name: 'John', role: 'admin'};
  expect(user).toMatchInlineSnapshot(`
    Object {
      "name": "John",
      "role": "admin",
    }
  `);
});
```

### Property Matchers
```javascript
test('snapshot with dynamic values', () => {
  const result = {
    id: Math.random(),
    timestamp: Date.now(),
    data: 'static content'
  };

  expect(result).toMatchSnapshot({
    id: expect.any(Number),
    timestamp: expect.any(Number)
  });
});
```

## Testing React Components

### Basic Component Testing
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Button from './Button';

test('renders button with text', () => {
  render(<Button>Click me</Button>);
  const button = screen.getByText('Click me');
  expect(button).toBeInTheDocument();
});

test('calls onClick handler', () => {
  const handleClick = jest.fn();
  render(<Button onClick={handleClick}>Click me</Button>);
  
  fireEvent.click(screen.getByText('Click me'));
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

### Testing Hooks
```javascript
import { renderHook, act } from '@testing-library/react';
import useCounter from './useCounter';

test('should increment counter', () => {
  const { result } = renderHook(() => useCounter());

  expect(result.current.count).toBe(0);

  act(() => {
    result.current.increment();
  });

  expect(result.current.count).toBe(1);
});
```

### Testing Async Components
```javascript
import { render, screen, waitFor } from '@testing-library/react';
import UserProfile from './UserProfile';

test('loads and displays user', async () => {
  render(<UserProfile userId="1" />);

  // Wait for async content
  const userName = await screen.findByText('John Doe');
  expect(userName).toBeInTheDocument();

  // Alternative with waitFor
  await waitFor(() => {
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
```

## Coverage

### Coverage Configuration
```javascript
// jest.config.js
module.exports = {
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/index.js',
    '!src/serviceWorker.js'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    },
    './src/utils/': {
      branches: 100,
      functions: 100,
      lines: 100,
      statements: 100
    }
  }
};
```

### Coverage Commands
```bash
# Run with coverage
npm test -- --coverage

# Coverage with watch
npm test -- --coverage --watchAll

# Update snapshots
npm test -- -u

# Run specific test file
npm test Button.test.js

# Run tests matching pattern
npm test -- --testNamePattern="should add"
```

## Advanced Configuration

### Setup and Teardown
```javascript
// Global setup (jest.setup.js)
beforeAll(() => {
  // Setup before all tests
  global.localStorage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    clear: jest.fn()
  };
});

afterAll(() => {
  // Cleanup after all tests
});

// Per test setup
beforeEach(() => {
  // Reset mocks
  jest.clearAllMocks();
});

afterEach(() => {
  // Cleanup
});
```

### Test Environment Setup
```javascript
// setupTests.js
import '@testing-library/jest-dom';
import 'jest-canvas-mock';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};
```

### Custom Test Utilities
```javascript
// testUtils.js
import { render } from '@testing-library/react';
import { ThemeProvider } from 'styled-components';
import { Provider } from 'react-redux';
import { store } from './store';
import { theme } from './theme';

export function renderWithProviders(
  ui,
  {
    preloadedState = {},
    store = createStore(rootReducer, preloadedState),
    ...renderOptions
  } = {}
) {
  function Wrapper({ children }) {
    return (
      <Provider store={store}>
        <ThemeProvider theme={theme}>
          {children}
        </ThemeProvider>
      </Provider>
    );
  }
  return render(ui, { wrapper: Wrapper, ...renderOptions });
}
```

## Best Practices

### Test Organization
```javascript
// Group related tests
describe('UserService', () => {
  describe('authentication', () => {
    test('should login with valid credentials', () => {});
    test('should reject invalid credentials', () => {});
  });

  describe('profile management', () => {
    test('should update user profile', () => {});
    test('should validate email format', () => {});
  });
});
```

### Test Data Builders
```javascript
// Test data factory
class UserBuilder {
  constructor() {
    this.user = {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      role: 'user'
    };
  }

  withName(name) {
    this.user.name = name;
    return this;
  }

  withRole(role) {
    this.user.role = role;
    return this;
  }

  build() {
    return this.user;
  }
}

// Usage
test('admin user', () => {
  const admin = new UserBuilder()
    .withRole('admin')
    .withName('Admin User')
    .build();

  expect(admin.role).toBe('admin');
});
```

### Common Patterns
```javascript
// Testing private methods indirectly
class Calculator {
  add(a, b) {
    return this.#validateAndCompute(a, b, (x, y) => x + y);
  }

  #validateAndCompute(a, b, operation) {
    if (typeof a !== 'number' || typeof b !== 'number') {
      throw new Error('Invalid input');
    }
    return operation(a, b);
  }
}

test('validates input through public method', () => {
  const calc = new Calculator();
  expect(() => calc.add('a', 1)).toThrow('Invalid input');
});

// Testing time-dependent code
function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 18) return 'Good afternoon';
  return 'Good evening';
}

test('returns correct greeting', () => {
  // Mock Date
  const mockDate = new Date('2024-01-15 10:00:00');
  jest.spyOn(global, 'Date').mockImplementation(() => mockDate);

  expect(getGreeting()).toBe('Good morning');

  Date.mockRestore();
});
```

## Debugging Tests

### Debug Output
```javascript
test('debug example', () => {
  const data = { foo: 'bar', nested: { value: 42 } };
  
  // Print to console
  console.log('Data:', data);
  
  // Pretty print
  console.log(JSON.stringify(data, null, 2));
  
  // Use debug from testing-library
  const { debug } = render(<Component />);
  debug(); // Prints component tree
});

// Run single test for debugging
test.only('focused test', () => {
  // Only this test runs
});

// Skip test
test.skip('not ready yet', () => {
  // This test is skipped
});
```

---
*Jest provides a comprehensive testing solution for JavaScript applications with powerful features like mocking, snapshots, and excellent assertion APIs.*