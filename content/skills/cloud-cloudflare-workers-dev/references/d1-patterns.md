# D1 Database Patterns

Patterns for working with Cloudflare D1 SQLite database.

## Schema Management

### Migration Files

```
migrations/
├── 0001_initial.sql
├── 0002_add_users.sql
└── 0003_add_indexes.sql
```

### Creating Migrations

```sql
-- migrations/0001_initial.sql
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_users_email ON users(email);
```

### Running Migrations

```bash
# Apply migrations
wrangler d1 migrations apply my-database

# Apply to remote
wrangler d1 migrations apply my-database --remote

# List migrations
wrangler d1 migrations list my-database
```

## Query Patterns

### Basic CRUD

```typescript
interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

// Create
async function createUser(env: Env, email: string, name: string): Promise<number> {
  const result = await env.DB.prepare(
    'INSERT INTO users (email, name) VALUES (?, ?) RETURNING id'
  ).bind(email, name).first<{ id: number }>();

  return result?.id ?? 0;
}

// Read one
async function getUser(env: Env, id: number): Promise<User | null> {
  return env.DB.prepare('SELECT * FROM users WHERE id = ?')
    .bind(id)
    .first<User>();
}

// Read many
async function getUsers(env: Env, limit = 10, offset = 0): Promise<User[]> {
  const { results } = await env.DB.prepare(
    'SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?'
  ).bind(limit, offset).all<User>();

  return results;
}

// Update
async function updateUser(env: Env, id: number, name: string): Promise<boolean> {
  const result = await env.DB.prepare(
    "UPDATE users SET name = ?, updated_at = datetime('now') WHERE id = ?"
  ).bind(name, id).run();

  return result.changes > 0;
}

// Delete
async function deleteUser(env: Env, id: number): Promise<boolean> {
  const result = await env.DB.prepare('DELETE FROM users WHERE id = ?')
    .bind(id)
    .run();

  return result.changes > 0;
}
```

### Batch Operations

```typescript
async function createUsers(env: Env, users: Array<{ email: string; name: string }>) {
  const statements = users.map(({ email, name }) =>
    env.DB.prepare('INSERT INTO users (email, name) VALUES (?, ?)').bind(email, name)
  );

  return env.DB.batch(statements);
}
```

### Transactions

```typescript
async function transferCredits(
  env: Env,
  fromId: number,
  toId: number,
  amount: number
): Promise<boolean> {
  const statements = [
    env.DB.prepare('UPDATE users SET credits = credits - ? WHERE id = ? AND credits >= ?')
      .bind(amount, fromId, amount),
    env.DB.prepare('UPDATE users SET credits = credits + ? WHERE id = ?')
      .bind(amount, toId),
  ];

  const results = await env.DB.batch(statements);

  // Check if deduction succeeded (had enough credits)
  return results[0].changes > 0;
}
```

### Pagination

```typescript
interface PaginatedResult<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

async function paginateUsers(
  env: Env,
  page: number,
  pageSize: number
): Promise<PaginatedResult<User>> {
  const offset = (page - 1) * pageSize;

  const [countResult, dataResult] = await env.DB.batch([
    env.DB.prepare('SELECT COUNT(*) as total FROM users'),
    env.DB.prepare('SELECT * FROM users ORDER BY id LIMIT ? OFFSET ?')
      .bind(pageSize, offset),
  ]);

  const total = (countResult.results[0] as { total: number }).total;

  return {
    data: dataResult.results as User[],
    total,
    page,
    pageSize,
    totalPages: Math.ceil(total / pageSize),
  };
}
```

### Search

```typescript
async function searchUsers(env: Env, query: string): Promise<User[]> {
  const { results } = await env.DB.prepare(
    "SELECT * FROM users WHERE name LIKE ? OR email LIKE ? LIMIT 20"
  ).bind(`%${query}%`, `%${query}%`).all<User>();

  return results;
}
```

### Full-Text Search

```sql
-- Create FTS table
CREATE VIRTUAL TABLE users_fts USING fts5(name, email, content=users, content_rowid=id);

-- Triggers to keep FTS in sync
CREATE TRIGGER users_ai AFTER INSERT ON users BEGIN
  INSERT INTO users_fts(rowid, name, email) VALUES (new.id, new.name, new.email);
END;

CREATE TRIGGER users_ad AFTER DELETE ON users BEGIN
  INSERT INTO users_fts(users_fts, rowid, name, email) VALUES('delete', old.id, old.name, old.email);
END;

CREATE TRIGGER users_au AFTER UPDATE ON users BEGIN
  INSERT INTO users_fts(users_fts, rowid, name, email) VALUES('delete', old.id, old.name, old.email);
  INSERT INTO users_fts(rowid, name, email) VALUES (new.id, new.name, new.email);
END;
```

```typescript
async function fullTextSearch(env: Env, query: string): Promise<User[]> {
  const { results } = await env.DB.prepare(`
    SELECT users.* FROM users
    JOIN users_fts ON users.id = users_fts.rowid
    WHERE users_fts MATCH ?
    ORDER BY rank
    LIMIT 20
  `).bind(query).all<User>();

  return results;
}
```

## Type-Safe Queries

```typescript
// Define result types
type UserRow = {
  id: number;
  email: string;
  name: string;
  created_at: string;
};

// Use generics
const user = await env.DB.prepare('SELECT * FROM users WHERE id = ?')
  .bind(id)
  .first<UserRow>();

// Handle nullability
if (!user) {
  throw new Error('User not found');
}
```

## Error Handling

```typescript
async function safeQuery<T>(
  env: Env,
  query: string,
  bindings: unknown[]
): Promise<{ data: T[] | null; error: string | null }> {
  try {
    const stmt = env.DB.prepare(query);
    const bound = bindings.length > 0 ? stmt.bind(...bindings) : stmt;
    const { results } = await bound.all<T>();
    return { data: results, error: null };
  } catch (error) {
    return { data: null, error: error instanceof Error ? error.message : 'Unknown error' };
  }
}
```

## Performance Tips

1. **Use indexes** for frequently queried columns
2. **Batch related queries** to reduce round trips
3. **Use LIMIT** to avoid returning too many rows
4. **Avoid SELECT *** when you only need specific columns
5. **Use prepared statements** (always use `.prepare()`)

```typescript
// Bad: N+1 queries
for (const userId of userIds) {
  const user = await env.DB.prepare('SELECT * FROM users WHERE id = ?')
    .bind(userId)
    .first();
}

// Good: Single query with IN clause
const placeholders = userIds.map(() => '?').join(',');
const { results } = await env.DB.prepare(
  `SELECT * FROM users WHERE id IN (${placeholders})`
).bind(...userIds).all();
```
