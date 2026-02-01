## Formula

- **Name:** <!-- formula name -->
- **Version:** <!-- vX.Y.Z or HEAD-only -->
- **Language:** <!-- go | rust | python | ... -->
- **Type:** <!-- new | update | fix -->

## Changes

<!-- What this PR adds or changes -->

## Validation

- [ ] `ruby -c Formula/<letter>/<name>.rb` passes
- [ ] `brew audit --new <name>` passes (new formulas)
- [ ] `brew audit <name>` passes (existing formulas)
- [ ] `brew style <tap>` passes
- [ ] `brew install --build-from-source <name>` succeeds
- [ ] `brew test <name>` passes
- [ ] Binary executes correctly (`<binary> --version` or `--help`)
- [ ] Livecheck returns correct version (`brew livecheck <name>`)

## Test Output

```
<!-- paste brew test output -->
```

## Notes

<!-- Any caveats, known issues, or follow-up work -->
