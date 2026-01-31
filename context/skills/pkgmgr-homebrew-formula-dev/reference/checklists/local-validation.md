## Local Validation

### Step 1: Sync to Tap Location

Formula files must be in the Homebrew tap location for testing:

```bash
mkdir -p /opt/homebrew/Library/Taps/arustydev/homebrew-tap/Formula/<letter>/
cp Formula/<letter>/<name>.rb /opt/homebrew/Library/Taps/arustydev/homebrew-tap/Formula/<letter>/
```

**Note:** On Apple Silicon Macs the prefix is `/opt/homebrew`, on Intel Macs it's `/usr/local`. Check with `brew --prefix`.

### Step 2: Run Audit

```bash
brew audit --new --formula arustydev/tap/<name>
```

This checks for common formula issues but NOT style violations.

### Step 3: Run CI Syntax Check (Critical)

```bash
brew style arustydev/tap
```

This runs rubocop against ALL files in the tap — same as CI. This catches issues that `brew audit` misses.

### Step 4: Test Installation

```bash
brew install --build-from-source arustydev/tap/<name>
# For HEAD-only:
brew install --HEAD arustydev/tap/<name>
```

### Step 5: Run Formula Tests

```bash
brew test arustydev/tap/<name>
```

### Step 6: Verify Binary

```bash
<name> --help
```
