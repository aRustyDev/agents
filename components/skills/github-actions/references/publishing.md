# Publishing GitHub Actions

Complete guide to publishing actions to the GitHub Marketplace.

## Marketplace Requirements

### Repository Setup

1. **Public repository** - Actions must be in a public repo
2. **action.yml** in repository root (not in subdirectory for Marketplace)
3. **README.md** with usage documentation
4. **LICENSE** file (MIT, Apache 2.0 recommended)

### action.yml Requirements

```yaml
name: 'My Action'                    # Required, unique in Marketplace
description: 'What it does'          # Required, max 125 chars
author: 'Your Name or Org'           # Recommended

branding:                            # Required for Marketplace
  icon: 'check-circle'               # Feather icon name
  color: 'green'                     # blue, green, orange, purple, yellow, gray-dark, white

inputs:
  # Document all inputs
  token:
    description: 'GitHub token for API access'
    required: true
    default: ${{ github.token }}

outputs:
  # Document all outputs
  result:
    description: 'The result of running the action'

runs:
  using: 'node20'
  main: 'dist/index.js'
```

### Available Branding Icons

Common icons from Feather: `activity`, `alert-circle`, `anchor`, `aperture`, `archive`, `award`, `bar-chart`, `battery`, `bell`, `bluetooth`, `bold`, `book`, `bookmark`, `box`, `briefcase`, `calendar`, `camera`, `cast`, `check`, `check-circle`, `check-square`, `chevron-down`, `chevron-left`, `chevron-right`, `chevron-up`, `clipboard`, `clock`, `cloud`, `code`, `coffee`, `command`, `compass`, `copy`, `cpu`, `credit-card`, `database`, `delete`, `disc`, `dollar-sign`, `download`, `edit`, `eye`, `fast-forward`, `feather`, `file`, `file-minus`, `file-plus`, `file-text`, `filter`, `flag`, `folder`, `git-branch`, `git-commit`, `git-merge`, `git-pull-request`, `globe`, `grid`, `hard-drive`, `hash`, `headphones`, `heart`, `help-circle`, `home`, `image`, `inbox`, `info`, `key`, `layers`, `layout`, `life-buoy`, `link`, `list`, `lock`, `log-in`, `log-out`, `mail`, `map`, `map-pin`, `maximize`, `menu`, `message-circle`, `message-square`, `mic`, `minimize`, `minus`, `monitor`, `moon`, `more-horizontal`, `more-vertical`, `move`, `music`, `navigation`, `octagon`, `package`, `paperclip`, `pause`, `pen-tool`, `percent`, `phone`, `pie-chart`, `play`, `play-circle`, `plus`, `plus-circle`, `plus-square`, `pocket`, `power`, `printer`, `radio`, `refresh-ccw`, `refresh-cw`, `repeat`, `rewind`, `rotate-ccw`, `rotate-cw`, `rss`, `save`, `scissors`, `search`, `send`, `server`, `settings`, `share`, `share-2`, `shield`, `shield-off`, `shopping-bag`, `shopping-cart`, `shuffle`, `sidebar`, `skip-back`, `skip-forward`, `slash`, `sliders`, `smartphone`, `speaker`, `square`, `star`, `stop-circle`, `sun`, `sunrise`, `sunset`, `tablet`, `tag`, `target`, `terminal`, `thermometer`, `thumbs-down`, `thumbs-up`, `toggle-left`, `toggle-right`, `trash`, `trash-2`, `trending-down`, `trending-up`, `triangle`, `truck`, `tv`, `type`, `umbrella`, `underline`, `unlock`, `upload`, `upload-cloud`, `user`, `user-check`, `user-minus`, `user-plus`, `user-x`, `users`, `video`, `video-off`, `voicemail`, `volume`, `volume-1`, `volume-2`, `volume-x`, `watch`, `wifi`, `wifi-off`, `wind`, `x`, `x-circle`, `x-square`, `zap`, `zoom-in`, `zoom-out`

## Versioning Strategy

### Semantic Versioning

```bash
# Patch: Bug fixes (1.0.0 → 1.0.1)
git tag v1.0.1

# Minor: New features, backward compatible (1.0.0 → 1.1.0)
git tag v1.1.0

# Major: Breaking changes (1.0.0 → 2.0.0)
git tag v2.0.0
```

### Major Version Tags

Users reference actions with major version tags for automatic minor/patch updates:

```yaml
uses: owner/action@v1  # Gets v1.x.x updates automatically
```

Maintain major version tags:

```bash
# After releasing v1.2.3
git tag -fa v1 -m "Update v1 tag"
git push origin v1 --force
```

### Automated Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  release:
    types: [published]

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build
        run: npm ci && npm run build

      - name: Update major version tag
        run: |
          VERSION=${GITHUB_REF#refs/tags/}
          MAJOR=${VERSION%%.*}

          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

          git tag -fa $MAJOR -m "Update $MAJOR tag to $VERSION"
          git push origin $MAJOR --force
```

## Publishing Steps

### 1. Create Release

```bash
# Ensure dist is up to date
npm run build
git add dist
git commit -m "Build for release"

# Tag and push
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 2. Create GitHub Release

Go to repository → Releases → "Draft a new release"

Or via CLI:

```bash
gh release create v1.0.0 \
  --title "v1.0.0" \
  --notes "Initial release" \
  --generate-notes
```

### 3. Publish to Marketplace

1. Go to repository → Releases → Select release
2. Click "Edit" on the release
3. Check "Publish this Action to the GitHub Marketplace"
4. Select primary and secondary categories
5. Save

### Categories for Marketplace

- **Code quality** - Linting, formatting, analysis
- **Code review** - PR automation, review helpers
- **Continuous integration** - Build, test automation
- **Dependency management** - Updates, security
- **Deployment** - Cloud, container, serverless
- **IDEs** - Editor integrations
- **Learning** - Educational tools
- **Localization** - Translation, i18n
- **Mobile** - iOS, Android builds
- **Monitoring** - Alerts, observability
- **Project management** - Issues, projects
- **Publishing** - Package registries
- **Security** - Scanning, secrets
- **Support** - Communication
- **Testing** - Test runners, coverage
- **Utilities** - General purpose

## README Best Practices

```markdown
# My Action

Description of what this action does.

## Usage

\`\`\`yaml
- uses: owner/my-action@v1
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    config-path: '.github/config.yml'
\`\`\`

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `token` | GitHub token | Yes | - |
| `config-path` | Path to config | No | `.github/config.yml` |

## Outputs

| Output | Description |
|--------|-------------|
| `result` | The result of the action |

## Examples

### Basic Usage

\`\`\`yaml
jobs:
  example:
    runs-on: ubuntu-latest
    steps:
      - uses: owner/my-action@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
\`\`\`

### Advanced Configuration

\`\`\`yaml
# More complex example
\`\`\`

## License

MIT
```

## Monorepo Actions

For multiple actions in one repository, use subdirectories:

```
my-actions/
├── setup-foo/
│   ├── action.yml
│   └── dist/
├── run-bar/
│   ├── action.yml
│   └── dist/
└── README.md
```

Reference with path:

```yaml
uses: owner/my-actions/setup-foo@v1
uses: owner/my-actions/run-bar@v1
```

**Note**: Subdirectory actions cannot be published to Marketplace individually. Consider separate repos for Marketplace visibility.

## Deprecation

When deprecating an action or input:

```yaml
inputs:
  old-input:
    description: 'DEPRECATED: Use new-input instead'
    deprecationMessage: 'old-input is deprecated. Use new-input instead.'
```

In code:

```typescript
const oldInput = core.getInput('old-input');
if (oldInput) {
  core.warning('old-input is deprecated. Use new-input instead.');
}
```

## Troubleshooting

### "Action does not exist"

- Ensure action.yml is in repo root (for Marketplace)
- Check tag/branch reference is correct
- Verify repository is public

### "Node.js version not supported"

- Use `using: 'node20'` (current recommended)
- Node 16 deprecated as of Sep 2024

### Marketplace not showing updates

- Verify release is published (not draft)
- Check "Publish to Marketplace" is checked
- Allow a few minutes for propagation
