# Task 1: Install sqlite-vec and verify it works

## Objective

Install the sqlite-vec Python package and verify it loads correctly on macOS ARM64.

## Prerequisites

- Python 3.11+ installed
- uv package manager (installed via `brew bundle`)

## Steps

### 1.1 Add to pyproject.toml

Already done. Verify `sqlite-vec>=0.1.6` is in dependencies.

### 1.2 Install via uv

```bash
uv sync
```

### 1.3 Verify installation

Create `scripts/test-sqlite-vec.py`:

```python
#!/usr/bin/env python3
"""Verify sqlite-vec installation."""

import sqlite3
import struct
import sqlite_vec

def main():
    # Connect to in-memory database
    conn = sqlite3.connect(':memory:')
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    # Check version
    version = conn.execute('SELECT vec_version()').fetchone()[0]
    print(f"sqlite-vec version: {version}")

    # Create test vector table
    conn.execute('CREATE VIRTUAL TABLE test_vec USING vec0(embedding FLOAT[4])')

    # Insert test vector
    test_vector = [0.1, 0.2, 0.3, 0.4]
    conn.execute(
        'INSERT INTO test_vec(rowid, embedding) VALUES (1, ?)',
        (struct.pack('4f', *test_vector),)
    )

    # Query back
    result = conn.execute(
        'SELECT rowid, vec_to_json(embedding) FROM test_vec'
    ).fetchone()
    print(f"Stored vector: rowid={result[0]}, embedding={result[1]}")

    # Test distance function
    query_vector = [0.1, 0.2, 0.3, 0.5]
    distance = conn.execute(
        'SELECT vec_distance_cosine(?, embedding) FROM test_vec WHERE rowid = 1',
        (struct.pack('4f', *query_vector),)
    ).fetchone()[0]
    print(f"Cosine distance: {distance:.6f}")

    print("\n✓ sqlite-vec is working correctly")

if __name__ == '__main__':
    main()
```

### 1.4 Run verification

```bash
uv run python scripts/test-sqlite-vec.py
```

Expected output:
```
sqlite-vec version: 0.1.6
Stored vector: rowid=1, embedding=[0.1, 0.2, 0.3, 0.4]
Cosine distance: 0.002494
✓ sqlite-vec is working correctly
```

## Known Issues

### macOS system sqlite3 CLI cannot load extensions

The system `/usr/bin/sqlite3` has extension loading disabled at compile time. This is expected. Use Python instead:

```bash
# This will NOT work:
sqlite3 :memory: ".load vec0"

# Use Python instead:
uv run python -c "import sqlite3; import sqlite_vec; print('OK')"
```

## Acceptance Criteria

- [ ] `uv sync` completes without errors
- [ ] `uv run python scripts/test-sqlite-vec.py` outputs success message
- [ ] Version is 0.1.6 or higher

## Files Created

- `scripts/test-sqlite-vec.py`

## Next

→ [02-init-database.md](02-init-database.md)
