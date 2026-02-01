---
name: New Formula Request
about: Request a Homebrew formula for a new package
labels: formula, new
---

## Package

- **Name:** <!-- kebab-case, e.g. my-tool -->
- **Repository:** <!-- https://github.com/owner/repo -->
- **Language:** <!-- go | rust | python | zig | cmake | autotools | meson -->
- **License:** <!-- SPDX identifier, e.g. MIT, Apache-2.0 -->

## Release

- **Latest version:** <!-- vX.Y.Z or HEAD-only -->
- **Release URL:** <!-- link to release page or tag -->
- **Source tarball:** <!-- https://github.com/owner/repo/archive/refs/tags/vX.Y.Z.tar.gz -->
- **SHA256:** <!-- output of `curl -sL <tarball> | shasum -a 256` -->

## Build Details

- **Binary name(s):** <!-- may differ from formula name -->
- **Build dependencies:** <!-- e.g. rust => :build, python@3.12 -->
- **Runtime dependencies:** <!-- e.g. openssl@3, libgit2 -->
- **uses_from_macos:** <!-- e.g. zlib, curl -->

## Install Notes

<!-- Any special install steps, features to enable, workspace paths, etc. -->

## Test Command

```bash
# Command to verify the install works
```

## Checklist

- [ ] Repository is public
- [ ] Has tagged releases (or explicitly HEAD-only)
- [ ] License file exists in repo
- [ ] Binary runs on macOS (arm64 + x86_64)
