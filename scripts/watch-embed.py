#!/usr/bin/env python3
"""Watch context files and auto-embed on changes.

Usage:
    watch-embed.py              # Watch and process changes
    watch-embed.py --dry-run    # Show what would be processed
"""

import argparse
import time
from pathlib import Path
from typing import Optional
from collections import defaultdict
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# Import from embed.py
import sys
sys.path.insert(0, str(Path(__file__).parent))
from embed import get_connection, ingest_file, guess_entity_type, ENTITY_PATTERNS
from lib.embedder import get_embedder


# Debounce settings
DEBOUNCE_SECONDS = 0.5


class DebounceHandler(FileSystemEventHandler):
    """Handler that debounces rapid file changes."""

    def __init__(self, callback, dry_run: bool = False):
        self.callback = callback
        self.dry_run = dry_run
        self.pending: dict[str, float] = {}
        self.lock = threading.Lock()
        self._start_processor()

    def _start_processor(self):
        """Start background thread to process pending changes."""
        def processor():
            while True:
                time.sleep(DEBOUNCE_SECONDS / 2)
                self._process_pending()

        thread = threading.Thread(target=processor, daemon=True)
        thread.start()

    def _process_pending(self):
        """Process any changes that have settled."""
        now = time.time()
        to_process = []

        with self.lock:
            for path, timestamp in list(self.pending.items()):
                if now - timestamp >= DEBOUNCE_SECONDS:
                    to_process.append(path)
                    del self.pending[path]

        for path in to_process:
            if self.dry_run:
                print(f"[DRY RUN] Would process: {path}")
            else:
                self.callback(path)

    def on_modified(self, event: FileSystemEvent):
        if event.is_directory:
            return
        self._queue_change(event.src_path)

    def on_created(self, event: FileSystemEvent):
        if event.is_directory:
            return
        self._queue_change(event.src_path)

    def _queue_change(self, path: str):
        """Queue a file change for processing."""
        # Only process markdown and json files
        if not (path.endswith('.md') or path.endswith('.json')):
            return

        # Check if it matches any of our patterns
        path_obj = Path(path)
        entity_type = guess_entity_type(path_obj)
        if entity_type == 'unknown':
            return

        with self.lock:
            self.pending[path] = time.time()
            print(f"Queued: {path}")


def process_file_change(path: str):
    """Process a single file change."""
    path_obj = Path(path)

    if not path_obj.exists():
        print(f"  Deleted: {path}")
        # TODO: Handle deletion
        return

    entity_type = guess_entity_type(path_obj)
    print(f"  Processing [{entity_type}]: {path}")

    try:
        conn = get_connection()
        embedder = get_embedder()
        ingest_file(conn, path_obj, entity_type, embedder)
        conn.close()
        print(f"  ✓ Done")
    except Exception as e:
        print(f"  ✗ Error: {e}")


def main():
    parser = argparse.ArgumentParser(description='Watch and auto-embed context files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be processed')
    parser.add_argument('--model', default='st:all-MiniLM-L6-v2', help='Embedding model (use st: prefix for sentence-transformers)')
    args = parser.parse_args()

    # Directories to watch
    watch_dirs = [
        'context/agents',
        'context/skills',
        'context/commands',
        'context/rules',
        'context/plugins',
        'context/output-styles',
        '.claude/commands',
        '.claude/rules',
    ]

    # Filter to existing directories
    watch_dirs = [d for d in watch_dirs if Path(d).exists()]

    print(f"Watching directories:")
    for d in watch_dirs:
        print(f"  {d}")
    print()

    # Set up observer
    observer = Observer()
    handler = DebounceHandler(process_file_change, dry_run=args.dry_run)

    for directory in watch_dirs:
        observer.schedule(handler, directory, recursive=True)

    observer.start()
    print("Watching for changes... (Ctrl+C to stop)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped")

    observer.join()


if __name__ == '__main__':
    main()
