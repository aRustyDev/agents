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
