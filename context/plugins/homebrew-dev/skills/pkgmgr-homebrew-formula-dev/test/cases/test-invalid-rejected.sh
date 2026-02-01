#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SKILL_DIR"

errors=0

for file in "$SKILL_DIR"/test/data/invalid-*.json; do
  if just template-formula "$file" >/dev/null 2>&1; then
    echo "FAIL: expected $(basename "$file") to be rejected"
    errors=$((errors + 1))
  else
    echo "  OK: $(basename "$file") correctly rejected"
  fi
done

if [ "$errors" -eq 0 ]; then
  echo "PASS: test-invalid-rejected"
else
  echo "FAIL: test-invalid-rejected ($errors assertions failed)"
  exit 1
fi
