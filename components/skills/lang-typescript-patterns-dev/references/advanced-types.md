# Advanced TypeScript Types

Deep dive into conditional types, mapped types, template literal types, and type inference patterns.

## Conditional Types

### Basic Syntax

```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<string>;  // true
type B = IsString<number>;  // false
```

### Distributive Conditional Types

When a conditional type acts on a union, it distributes over each member:

```typescript
type ToArray<T> = T extends unknown ? T[] : never;

type Result = ToArray<string | number>;
// Distributes to: string[] | number[]
// Not: (string | number)[]
```

### Preventing Distribution

Wrap both sides in tuples to prevent distribution:

```typescript
type ToArrayNonDist<T> = [T] extends [unknown] ? T[] : never;

type Result = ToArrayNonDist<string | number>;
// Result: (string | number)[]
```

### The `infer` Keyword

Extract types from other types:

```typescript
// Extract return type
type ReturnOf<T> = T extends (...args: any[]) => infer R ? R : never;

// Extract promise value
type Unwrap<T> = T extends Promise<infer V> ? Unwrap<V> : T;

// Extract array element
type Elem<T> = T extends (infer E)[] ? E : T;

// Extract function parameters
type Params<T> = T extends (...args: infer P) => any ? P : never;
```

### Practical Examples

```typescript
// Type-safe event handler extraction
type EventHandler<T> = T extends `on${infer Event}` ? Event : never;
type Events = EventHandler<'onClick' | 'onSubmit' | 'disabled'>;
// Result: 'Click' | 'Submit'

// Extract component props
type PropsOf<T> = T extends React.ComponentType<infer P> ? P : never;
```

## Mapped Types

### Basic Mapping

```typescript
type Readonly<T> = {
  readonly [K in keyof T]: T[K];
};

type Partial<T> = {
  [K in keyof T]?: T[K];
};

type Nullable<T> = {
  [K in keyof T]: T[K] | null;
};
```

### Key Remapping (TypeScript 4.1+)

```typescript
// Prefix keys
type Prefixed<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface User {
  name: string;
  age: number;
}

type Getters = Prefixed<User>;
// { getName: () => string; getAge: () => number; }
```

### Filtering Keys

```typescript
// Keep only string properties
type StringProps<T> = {
  [K in keyof T as T[K] extends string ? K : never]: T[K];
};

// Remove specific keys
type RemoveKeys<T, K> = {
  [P in keyof T as P extends K ? never : P]: T[P];
};
```

### Deep Mapping

```typescript
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object
    ? T[K] extends Function
      ? T[K]
      : DeepReadonly<T[K]>
    : T[K];
};

type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object
    ? T[K] extends Function
      ? T[K]
      : DeepPartial<T[K]>
    : T[K];
};
```

## Template Literal Types

### Basic Patterns

```typescript
type EventName = `on${Capitalize<'click' | 'focus' | 'blur'>}`;
// 'onClick' | 'onFocus' | 'onBlur'

type Locale = `${Language}-${Country}`;
type Language = 'en' | 'es' | 'fr';
type Country = 'US' | 'UK' | 'ES';
// 'en-US' | 'en-UK' | 'en-ES' | 'es-US' | ...
```

### String Manipulation Types

```typescript
type Upper = Uppercase<'hello'>;        // 'HELLO'
type Lower = Lowercase<'HELLO'>;        // 'hello'
type Cap = Capitalize<'hello'>;         // 'Hello'
type Uncap = Uncapitalize<'Hello'>;     // 'hello'
```

### Path Types

```typescript
type PathOf<T, Prefix extends string = ''> = T extends object
  ? {
      [K in keyof T & string]: T[K] extends object
        ? `${Prefix}${K}` | PathOf<T[K], `${Prefix}${K}.`>
        : `${Prefix}${K}`;
    }[keyof T & string]
  : never;

interface Config {
  database: {
    host: string;
    port: number;
  };
  cache: {
    enabled: boolean;
  };
}

type ConfigPath = PathOf<Config>;
// 'database' | 'database.host' | 'database.port' | 'cache' | 'cache.enabled'
```

## Type-Safe Builders

### Builder Pattern

```typescript
type RequiredKeys<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;

class QueryBuilder<T extends Partial<Query>> {
  private query: T = {} as T;

  select<K extends string>(field: K): QueryBuilder<T & { select: K }> {
    this.query = { ...this.query, select: field };
    return this as any;
  }

  from<K extends string>(table: K): QueryBuilder<T & { from: K }> {
    this.query = { ...this.query, from: table };
    return this as any;
  }

  build(this: QueryBuilder<RequiredKeys<Query, 'select' | 'from'>>): string {
    return `SELECT ${this.query.select} FROM ${this.query.from}`;
  }
}

// Forces correct order
new QueryBuilder()
  .select('*')
  .from('users')
  .build(); // OK

new QueryBuilder()
  .select('*')
  .build(); // Error: 'from' is required
```

## Type-Safe Event Emitter

```typescript
type EventMap = {
  connect: { host: string; port: number };
  disconnect: { reason: string };
  error: Error;
};

class TypedEmitter<Events extends Record<string, unknown>> {
  private listeners = new Map<keyof Events, Set<Function>>();

  on<E extends keyof Events>(
    event: E,
    listener: (payload: Events[E]) => void
  ): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(listener);
  }

  emit<E extends keyof Events>(event: E, payload: Events[E]): void {
    this.listeners.get(event)?.forEach(fn => fn(payload));
  }
}

const emitter = new TypedEmitter<EventMap>();

emitter.on('connect', ({ host, port }) => {
  console.log(`Connected to ${host}:${port}`);
});

emitter.emit('connect', { host: 'localhost', port: 3000 }); // OK
emitter.emit('connect', { host: 'localhost' }); // Error: missing 'port'
```

## Branded Types

Prevent mixing incompatible values that share the same primitive type:

```typescript
declare const brand: unique symbol;

type Brand<T, B> = T & { [brand]: B };

type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;

function getUser(id: UserId): User { ... }
function getOrder(id: OrderId): Order { ... }

const userId = 'abc' as UserId;
const orderId = 'xyz' as OrderId;

getUser(userId);   // OK
getUser(orderId);  // Error: OrderId not assignable to UserId
```

## Exhaustiveness Checking

```typescript
function assertNever(x: never): never {
  throw new Error(`Unexpected value: ${x}`);
}

type Shape = { kind: 'circle'; radius: number }
           | { kind: 'square'; side: number }
           | { kind: 'triangle'; base: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'square':
      return shape.side ** 2;
    case 'triangle':
      return (shape.base * shape.height) / 2;
    default:
      return assertNever(shape); // Compile error if case missing
  }
}
```
