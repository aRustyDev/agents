#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SKILL_DIR"

output=$(just template-formula "$SKILL_DIR/test/data/haskell-standard.json")

errors=0
for pattern in "class MyHaskellTool < Formula" "cabal" "v2-install" "depends_on \"ghc\"" "test do"; do
  if ! echo "$output" | grep -q "$pattern"; then
    echo "FAIL: expected '$pattern' in output"
    errors=$((errors + 1))
  fi
done

if [ "$errors" -eq 0 ]; then
  echo "PASS: test-haskell-renders"
else
  echo "FAIL: test-haskell-renders ($errors assertions failed)"
  echo "--- output ---"
  echo "$output"
  exit 1
fi
