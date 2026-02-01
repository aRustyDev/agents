#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SKILL_DIR"

output=$(just template-formula "$SKILL_DIR/test/data/gleam-standard.json")

errors=0
for pattern in "class MyGleamTool < Formula" "gleam" "erlang-shipment" "depends_on \"erlang\"" "test do"; do
  if ! echo "$output" | grep -q "$pattern"; then
    echo "FAIL: expected '$pattern' in output"
    errors=$((errors + 1))
  fi
done

if [ "$errors" -eq 0 ]; then
  echo "PASS: test-gleam-renders"
else
  echo "FAIL: test-gleam-renders ($errors assertions failed)"
  echo "--- output ---"
  echo "$output"
  exit 1
fi
