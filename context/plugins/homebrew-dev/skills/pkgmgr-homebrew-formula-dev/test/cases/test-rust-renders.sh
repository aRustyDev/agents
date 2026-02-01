#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SKILL_DIR"

output=$(just template-formula "$SKILL_DIR/test/data/rust-standard.json")

errors=0
for pattern in "class RustAnalyzer < Formula" "std_cargo_args" "depends_on \"rust\"" "uses_from_macos \"zlib\"" '"lsp"' '"jemalloc"'; do
  if ! echo "$output" | grep -q "$pattern"; then
    echo "FAIL: expected '$pattern' in output"
    errors=$((errors + 1))
  fi
done

if [ "$errors" -eq 0 ]; then
  echo "PASS: test-rust-renders"
else
  echo "FAIL: test-rust-renders ($errors assertions failed)"
  echo "--- output ---"
  echo "$output"
  exit 1
fi
