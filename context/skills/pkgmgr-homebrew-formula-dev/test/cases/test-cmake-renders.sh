#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SKILL_DIR"

output=$(just template-formula "$SKILL_DIR/test/data/cmake-standard.json")

errors=0
for pattern in "class MyCmakeTool < Formula" "cmake" "std_cmake_args" "depends_on \"cmake\"" "test do"; do
  if ! echo "$output" | grep -q "$pattern"; then
    echo "FAIL: expected '$pattern' in output"
    errors=$((errors + 1))
  fi
done

if [ "$errors" -eq 0 ]; then
  echo "PASS: test-cmake-renders"
else
  echo "FAIL: test-cmake-renders ($errors assertions failed)"
  echo "--- output ---"
  echo "$output"
  exit 1
fi
