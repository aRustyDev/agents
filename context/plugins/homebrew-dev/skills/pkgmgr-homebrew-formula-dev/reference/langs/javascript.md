## JavaScript Formula Patterns

> **Recommended:** Use `language: "nodejs"` — JavaScript CLI tools run on Node.js.

### Overview

JavaScript CLI tools use the Node.js runtime. Use `language: "nodejs"` for all JavaScript formulas — the build pipeline is identical.

### Dependencies

```text
depends_on "node"
```

### Build Notes

The `std_npm_args` helper handles `npm install` with the correct prefix settings. Binaries are symlinked from `libexec/bin/` to `bin/`.

### Common Issues

- **Same as Node.js:** Follow all Node.js formula patterns
- **ESM vs CJS:** Ensure the package works with the Node.js version in Homebrew
- **Native addons:** Check for `node-gyp` dependencies
