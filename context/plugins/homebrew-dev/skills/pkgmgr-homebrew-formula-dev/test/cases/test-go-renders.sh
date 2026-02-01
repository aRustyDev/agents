#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SKILL_DIR"

output=$(just template-formula "$SKILL_DIR/test/data/go-standard.json")

errors=0
for pattern in "class MyTool < Formula" "std_go_args" "depends_on \"go\"" "depends_on \"pkg-config\"" "livecheck do" "head \"https://github.com/example/my-tool.git\"" "generate_completions_from_executable" "test do"; do
  if ! echo "$output" | grep -q "$pattern"; then
    echo "FAIL: expected '$pattern' in output"
    errors=$((errors + 1))
  fi
done

if [ "$errors" -eq 0 ]; then
  echo "PASS: test-go-renders"
else
  echo "FAIL: test-go-renders ($errors assertions failed)"
  echo "--- output ---"
  echo "$output"
  exit 1
fi
