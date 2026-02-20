#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SKILL_DIR"

output=$(just template-formula "$SKILL_DIR/test/data/elixir-standard.json")

errors=0
for pattern in "class MyElixirTool < Formula" "mix" "escript.build" "depends_on \"erlang\"" "test do"; do
  if ! echo "$output" | grep -q "$pattern"; then
    echo "FAIL: expected '$pattern' in output"
    errors=$((errors + 1))
  fi
done

if [ "$errors" -eq 0 ]; then
  echo "PASS: test-elixir-renders"
else
  echo "FAIL: test-elixir-renders ($errors assertions failed)"
  echo "--- output ---"
  echo "$output"
  exit 1
fi
