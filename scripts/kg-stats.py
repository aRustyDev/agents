#!/usr/bin/env python3
"""Show knowledge graph statistics."""

import sqlite3
import sqlite_vec
from pathlib import Path

DB_PATH = Path('.data/mcp/knowledge-graph.db')


def main():
    if not DB_PATH.exists():
        print("Database not found. Run: just kg-init")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)

    entities = conn.execute(
        'SELECT entity_type, count(*) FROM entities GROUP BY entity_type'
    ).fetchall()
    chunks = conn.execute('SELECT count(*) FROM chunks').fetchone()[0]
    embeddings = conn.execute('SELECT count(*) FROM embedding_meta').fetchone()[0]
    similarity = conn.execute('SELECT count(*) FROM similarity_cache').fetchone()[0]

    print('Knowledge Graph Statistics:')
    print('  Entities:')
    if entities:
        for etype, count in entities:
            print(f'    {etype}: {count}')
    else:
        print('    (none)')
    print(f'  Chunks: {chunks}')
    print(f'  Embeddings: {embeddings}')
    print(f'  Similarity cache: {similarity}')

    conn.close()


if __name__ == '__main__':
    main()
