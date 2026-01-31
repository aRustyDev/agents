# Analysis: Why Zed Extension Hash Sync Keeps Failing

## The Pattern

Throughout Phases 1-3, we've repeatedly encountered the same issue:
1. Complete phase implementation
2. Push to GitHub
3. Update extension.toml
4. Zed fails with: `failed to fetch revision <hash>`

## Root Causes

### 1. Assistant Behavior Patterns

**Hash Truncation**: The assistant consistently provides shortened hashes
- Often provides 7-char hash: `c00e2c1`
- Sometimes 12-char: `c00e2c140c93`
- Sometimes 16-char: `c00e2c140c93fe4c`
- Zed requires FULL 40-char: `c00e2c1aff554005cb668c92f7dd74a92d345296`

**Why this happens**:
- Git commonly uses short hashes in output (git log --oneline)
- Most git operations accept short hashes
- The assistant is trained on git documentation showing short hashes
- Zed is an exception requiring full hashes

### 2. Instruction Ambiguity

Original instructions in phase plans:
```
Update extension.toml with full commit hash
```

Problems:
- "Full" is ambiguous - could mean "complete" or "long form"
- No explicit command to get 40-char hash
- No verification step
- No explanation of WHY it must be 40 chars

### 3. Lack of Feedback Loop

The plans didn't include:
- Hash length verification
- Pre-installation fetch test
- Clear failure criteria
- Recovery instructions

## The Solution

All phase plans now include:
```bash
# Get FULL hash (40 chars) - DO NOT TRUNCATE
FULL_HASH=$(git log -1 --format="%H")
echo "Full hash: $FULL_HASH (length: ${#FULL_HASH})"
[[ ${#FULL_HASH} -eq 40 ]] || exit 1
```

And checkpoint requirements:
```
- [ ] extension.toml commit hash is EXACTLY 40 characters
- [ ] Hash matches latest pushed commit
- [ ] Manual fetch test passed
- [ ] FAILURE = CHECKPOINT NOT PASSED
```

## Why This Matters

1. **User Trust**: Repeated failures erode confidence
2. **Time Waste**: Each failure requires debugging
3. **Documentation**: Plans should be foolproof
4. **Quality**: This is a simple, preventable error

## Recommendations

1. **Be Explicit**: Never assume the assistant understands implicit requirements
2. **Add Verification**: Every critical step needs a verification command
3. **Test Early**: Catch failures before the user encounters them
4. **Document Why**: Explain unusual requirements (like 40-char hashes)

## Future Prevention

For any tool integration:
1. Document ALL requirements explicitly
2. Include verification steps
3. Add pre-flight checks
4. Provide clear error messages
5. Include recovery procedures

This issue has been a valuable lesson in the importance of explicit, verifiable instructions.