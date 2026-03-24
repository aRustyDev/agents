## TypeScript Formula Patterns

> **Recommended:** Use `language: "nodejs"` — TypeScript compiles to JavaScript and runs on Node.js.

### Overview

TypeScript is a superset of JavaScript. TypeScript projects compile to JavaScript and use the same `npm` build pipeline. Use `language: "nodejs"` for all TypeScript formulas.

### Dependencies

```text
depends_on "node"
```

### Build Notes

TypeScript projects typically have a `build` script in `package.json` that runs `tsc`. The `npm install` step handled by `std_npm_args` will invoke the build.

### Common Issues

- **Same as Node.js:** Follow all Node.js formula patterns
- **Build step:** Ensure `package.json` includes a `prepare` or `build` script
- **Type declarations:** Only the compiled `.js` files are needed at runtime
