#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SKILL_DIR"

output=$(just javascript-recipe "$SKILL_DIR/test/data/service-formula.json")

errors=0
for pattern in "class MyDaemon < Formula" "service do" "run_type :immediate" "keep_alive true" "log_path" "def caveats"; do
  if ! echo "$output" | grep -q "$pattern"; then
    echo "FAIL: expected '$pattern' in output"
    errors=$((errors + 1))
  fi
done

if [ "$errors" -eq 0 ]; then
  echo "PASS: test-service-formula"
else
  echo "FAIL: test-service-formula ($errors assertions failed)"
  echo "--- output ---"
  echo "$output"
  exit 1
fi
