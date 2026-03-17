## Python Formula Patterns

### Researching a Python Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system | Repo root | `pyproject.toml` (modern), `setup.py`/`setup.cfg` (legacy) |
| Binary name(s) | `pyproject.toml` `[project.scripts]` or `setup.py` `entry_points` | The key is the binary name, the value is the module path |
| Python version | `pyproject.toml` `requires-python` | Map to Homebrew's `python@3.XX` — use latest compatible |
| Direct dependencies | `pyproject.toml` `[project.dependencies]` or `requirements.txt` | Each becomes a `resource` block unless already in homebrew-core |
| Resource URLs | PyPI | `https://pypi.org/project/<pkg>/#files` — use the `.tar.gz` sdist, not wheel |
| Completions | CLI framework | If using `click`: look for `shell_complete`; if using `argparse`: check for custom completion |
| Native extensions | `setup.py` or `pyproject.toml` build-backend | If using `setuptools` with C extensions: needs compiler deps |
| Test command | README, `--help` output | Check if tool supports `--version` or `--help` |

**Quick check sequence:**

```bash
# Confirm Python project, find entry points
gh api repos/OWNER/REPO/contents/pyproject.toml --jq '.content' | base64 -d | grep -A10 '\[project.scripts\]'

# Find Python version requirement
gh api repos/OWNER/REPO/contents/pyproject.toml --jq '.content' | base64 -d | grep 'requires-python'

# List dependencies
gh api repos/OWNER/REPO/contents/pyproject.toml --jq '.content' | base64 -d | grep -A30 '\[project\]' | grep -A20 'dependencies'
```

**Generating resource blocks:** After initial formula creation, use `brew update-python-resources <formula>` to auto-generate resource blocks from PyPI.

### Dependencies

```text
depends_on "python@3.12"
```

### Install Block

**Standard pattern (with resource blocks):**
```text
include Language::Python::Virtualenv

def install
  virtualenv_install_with_resources
end
```

- `virtualenv_install_with_resources` creates a venv, installs resource blocks, then installs the formula
- Requires `resource` blocks for all pip dependencies (generate with `brew update-python-resources`)

**Alternative pattern (install from PyPI - recommended when no resource blocks):**
```text
include Language::Python::Virtualenv

def install
  venv = virtualenv_create(libexec, "python3.14")
  venv.pip_install "package-name==#{version}"
  bin.install_symlink Dir[libexec/"bin/tool"]
end
```

- Installs from PyPI with proper dependency resolution
- No resource blocks needed, but less reproducible builds
- **Important:** Check if PyPI package name differs from repo name (e.g., `ktool` → `k2l`)

**Alternative pattern (build from source - may have issues):**
```text
include Language::Python::Virtualenv

def install
  venv = virtualenv_create(libexec, "python3.14")
  venv.pip_install buildpath
  bin.install_symlink Dir[libexec/"bin/tool"]
end
```

- Builds from the downloaded source tarball
- **Warning:** May not reliably resolve dependencies with some build backends (hatchling, etc.)
- **Important:** Use `venv.pip_install`, NOT `system libexec/"bin/pip"` — the latter doesn't work

**With setuptools dependency (for packages using pkg_resources):**
```text
def install
  venv = virtualenv_create(libexec, "python3.14")
  venv.pip_install "setuptools"
  venv.pip_install buildpath
  bin.install_symlink Dir[libexec/"bin/tool"]
end
```

- Check `pyproject.toml`, `setup.py`, or `setup.cfg` for the project's build system

### JSON Schema Fields (`install-python`)

| Field | Default | Purpose |
|-------|---------|---------|
| `python_version` | `"python3"` | Python version dependency |
| `using` | `"virtualenv"` | Install method (`virtualenv`, `pip`, `setuptools`) |
| `site_packages` | `false` | Allow access to system site-packages |
| `resources` | — | Python package dependencies (defined at formula level) |

### Mustache Partial

The `langs/python.mustache` partial renders `virtualenv_install_with_resources`.

### Resource Blocks

Python formulas need `resource` blocks for pip dependencies not in homebrew-core:

```text
resource "certifi" do
  url "https://files.pythonhosted.org/packages/certifi-2024.2.2.tar.gz"
  sha256 "..."
end
```

Generate resource blocks with:

```bash
brew update-python-resources <formula-name>
```

### Entry Points

Check `pyproject.toml` `[project.scripts]` for the binary names the formula will install:

```toml
[project.scripts]
my-tool = "my_package.cli:main"
```

### Common Issues

- **Missing resources:** Python dependencies must be declared as `resource` blocks — they're not auto-resolved
- **Version pinning:** Use the exact source tarball versions that match the project's requirements
- **Site packages:** Set `site_packages: true` only when the formula needs access to Homebrew-installed Python packages
- **buildpath not resolving deps:** Some build backends (hatchling, poetry) may not properly resolve dependencies when using `venv.pip_install buildpath`. If you see `ModuleNotFoundError` at runtime, switch to `venv.pip_install "package==#{version}"` to install from PyPI instead

### Reference

See `reference/templates/formulas/python.rb` for a pipeline-generated example.
