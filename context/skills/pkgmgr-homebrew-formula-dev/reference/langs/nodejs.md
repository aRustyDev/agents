## Node.js Formula Patterns

### Researching a Node.js Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system confirmation | Repo root | Look for `package.json` |
| Binary name(s) | `package.json` `bin` field | The key is the binary name |
| Node version | `package.json` `engines.node` | Map to Homebrew's `node` or `node@XX` |
| Native addons | `package.json` `dependencies` | Look for `node-gyp`, `nan`, `napi` |
| Test command | `package.json` `scripts.test` or `--help` | Check if tool supports `--help` or `--version` |

**Quick check sequence:**

```bash
gh api repos/OWNER/REPO/contents/package.json --jq '.content' | base64 -d | jq '.bin'
gh api repos/OWNER/REPO/contents/package.json --jq '.content' | base64 -d | jq '.engines.node'
```

### Dependencies

```text
depends_on "node"
```

### Install Block

```text
def install
  system "npm", "install", *std_npm_args
  bin.install_symlink Dir["#{libexec}/bin/*"]
end
```

### JSON Schema Fields (`install-nodejs`)

| Field | Default | Purpose |
|-------|---------|---------|
| `node_version` | `"node"` | Node.js version dependency |
| `npm_install` | `true` | Use npm install for building |
| `build_from_source` | `false` | Build native addons from source |

### Mustache Partial

The `langs/nodejs.mustache` partial renders `std_npm_args` with symlinked binaries.

### Common Issues

- **Native addons:** If the package has native dependencies, add `depends_on "python" => :build` for node-gyp
- **Lockfile:** Ensure `package-lock.json` is included in the source tarball
- **Global vs local:** Homebrew uses `--prefix` to install to `libexec/`, then symlinks binaries

### Reference

See `reference/templates/formulas/nodejs.rb` for a pipeline-generated example.
