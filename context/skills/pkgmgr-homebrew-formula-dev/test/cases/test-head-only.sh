#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SKILL_DIR"

output=$(just template-formula "$SKILL_DIR/test/data/head-only.json")

errors=0

# Should have head
if ! echo "$output" | grep -q 'head "https://github.com/example/bleeding-edge.git"'; then
  echo "FAIL: expected head URL in output"
  errors=$((errors + 1))
fi

# Should NOT have url/sha256 lines (no stable URL)
if echo "$output" | grep -q '  url "https://'; then
  echo "FAIL: unexpected url line in HEAD-only formula"
  errors=$((errors + 1))
fi
if echo "$output" | grep -q '  sha256 "'; then
  echo "FAIL: unexpected sha256 line in HEAD-only formula"
  errors=$((errors + 1))
fi

# Should NOT have livecheck
if echo "$output" | grep -q 'livecheck do'; then
  echo "FAIL: unexpected livecheck in HEAD-only formula"
  errors=$((errors + 1))
fi

if [ "$errors" -eq 0 ]; then
  echo "PASS: test-head-only"
else
  echo "FAIL: test-head-only ($errors assertions failed)"
  echo "--- output ---"
  echo "$output"
  exit 1
fi
