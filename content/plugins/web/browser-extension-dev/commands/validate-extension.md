---
description: Validate browser extension for manifest issues, CSP violations, and cross-browser compatibility
argument-hint: "[path] [--browsers chrome,firefox,safari] [--fix] [--strict]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(npx:*), Bash(web-ext:*), Bash(wxt:*), Bash(cat:*), Bash(jq:*), Bash(ls:*), AskUserQuestion
---

# Validate Browser Extension

Comprehensive validation of browser extensions checking manifest compatibility, CSP issues, API usage, and cross-browser support.

## Arguments

- `$1` - Path to extension directory (default: current directory)
- `--browsers` - Target browsers to validate against (default: `chrome,firefox`). Options: `chrome`, `firefox`, `safari`, `edge`, `all`
- `--fix` - Attempt to auto-fix issues where possible
- `--strict` - Fail on warnings (not just errors)
- `--output` - Output format: `terminal`, `json`, `markdown` (default: `terminal`)

## Workflow

### Step 1: Detect Extension Type

Determine if this is a WXT project or raw extension:

```bash
# Check for WXT
if [ -f "wxt.config.ts" ] || [ -f "wxt.config.js" ]; then
  TYPE="wxt"
  # Build first to get manifest
  npx wxt build --analyze
else
  TYPE="raw"
fi
```

Locate the manifest:

```bash
# WXT: dist/<browser>-mv3/manifest.json
# Raw: manifest.json or src/manifest.json
```

### Step 2: Run Web-ext Lint

For all extension types:

```bash
npx web-ext lint --source-dir <dist-path> --output json
```

Parse and categorize results:

| Severity | Action |
|----------|--------|
| error | Must fix before submission |
| warning | Should fix, may cause rejection |
| notice | Best practice recommendation |

### Step 3: Validate Manifest

#### 3.1 Required Fields

Check presence of required fields:

```
manifest_version: 3
name: <string, max 45 chars>
version: <semver>
description: <string, max 132 chars>
icons: { 16, 32, 48, 128 }
```

#### 3.2 Permission Audit

Check against hardening rules:

| Check | Severity | Rule |
|-------|----------|------|
| Uses `<all_urls>` | error | Avoid broad host permissions |
| Uses `*://*/*` | error | Narrow to specific domains |
| Unused permissions declared | warning | Remove unnecessary permissions |
| Sensitive permissions without justification | warning | Document in store listing |
| Missing `optional_permissions` for upgradeable perms | notice | Better UX |

Sensitive permissions that require justification:

```
tabs, history, bookmarks, downloads, webRequest,
webRequestBlocking, management, debugger, proxy,
cookies, clipboardRead, clipboardWrite, geolocation
```

#### 3.3 Browser-Specific Checks

**Firefox:**

```javascript
// Required for AMO submission
browser_specific_settings: {
  gecko: {
    id: "<email-format-id>",  // Required
    strict_min_version: "109.0"  // Recommended
  }
}

// Required since Nov 2025
data_collection_permissions: {
  required: [],
  optional: []
}
```

**Chrome:**

```javascript
// Recommended
minimum_chrome_version: "116"

// MV3 required
background: {
  service_worker: "background.js"
}
```

**Safari:**

```
// Check for PrivacyInfo.xcprivacy in Xcode project
// Not in manifest, but required for App Store
```

### Step 4: Validate CSP

#### 4.1 Check content_security_policy

```javascript
// BAD: Allows unsafe-eval
"content_security_policy": {
  "extension_pages": "script-src 'self' 'unsafe-eval'"
}

// GOOD: Strict CSP
"content_security_policy": {
  "extension_pages": "script-src 'self'; object-src 'self'"
}
```

| Check | Severity | Rule |
|-------|----------|------|
| Contains `unsafe-eval` | error | Store rejection |
| Contains `unsafe-inline` | error | Store rejection |
| External script URLs | error | Remote code execution |
| Missing CSP (MV3) | warning | Use strict default |

#### 4.2 Scan Source Files

Check for CSP violations in code:

```bash
# Find eval() usage
grep -r "eval(" --include="*.js" --include="*.ts"

# Find new Function()
grep -r "new Function" --include="*.js" --include="*.ts"

# Find innerHTML with variables
grep -r "innerHTML\s*=" --include="*.js" --include="*.ts"

# Find document.write
grep -r "document.write" --include="*.js" --include="*.ts"
```

### Step 5: API Compatibility Check

#### 5.1 Detect Used APIs

Scan source files for browser API usage:

```bash
# Extract API calls
grep -roh "browser\.\w\+\.\w\+" --include="*.js" --include="*.ts" | sort -u
grep -roh "chrome\.\w\+\.\w\+" --include="*.js" --include="*.ts" | sort -u
```

#### 5.2 Check Compatibility Matrix

| API | Chrome | Firefox | Safari | Edge |
|-----|--------|---------|--------|------|
| `sidePanel.*` | 114+ | - | - | 114+ |
| `offscreen.*` | 109+ | - | - | 109+ |
| `scripting.executeScript` | Full | Full | Limited | Full |
| `declarativeNetRequest` | Full | Partial | Limited | Full |
| `action.*` (MV3) | Full | Full | Full | Full |
| `browserAction.*` (MV2) | MV2 | MV2/3 | MV2 | MV2 |
| `storage.session` | 102+ | 115+ | 16.4+ | 102+ |

Report incompatible APIs:

```
⚠️ chrome.sidePanel used but not available in Firefox, Safari
⚠️ chrome.offscreen used but not available in Firefox, Safari
```

#### 5.3 Polyfill Check

Verify webextension-polyfill usage for cross-browser:

```bash
# Check if polyfill is installed
grep "webextension-polyfill" package.json

# Check if browser.* is used (polyfill) vs chrome.* (Chrome-only)
```

### Step 6: Content Script Analysis

#### 6.1 Match Pattern Validation

```javascript
// Validate match patterns
content_scripts: [{
  matches: ["*://*.example.com/*"],  // Valid
  matches: ["<all_urls>"],  // Warning: very broad
  matches: ["*://*/*"],  // Warning: very broad
}]
```

#### 6.2 Run-at Timing

```javascript
// Check run_at setting
run_at: "document_idle"  // Recommended (default)
run_at: "document_start"  // Warning: may cause issues
run_at: "document_end"  // OK
```

#### 6.3 World Setting

```javascript
// MV3 world setting
world: "ISOLATED"  // Default, safe
world: "MAIN"  // Warning: security implications
```

### Step 7: Generate Report

#### Terminal Output (default)

```
╭──────────────────────────────────────────────────────────────╮
│  Extension Validation Report                                  │
│  my-extension v1.0.0                                         │
╰──────────────────────────────────────────────────────────────╯

📋 Manifest Validation
  ✓ Required fields present
  ✓ Icons all sizes present
  ⚠ Missing gecko.data_collection_permissions (Firefox 2025+)
  ✗ Uses <all_urls> - narrow to specific domains

🔒 CSP Validation
  ✓ No unsafe-eval
  ✓ No unsafe-inline
  ✗ Found eval() in src/utils.js:42

🌐 Cross-Browser Compatibility
  Chrome:  ✓ Compatible
  Firefox: ⚠ 2 issues
    - Missing gecko.id
    - Uses chrome.sidePanel (not supported)
  Safari:  ⚠ 3 issues
    - Uses chrome.offscreen (not supported)
    - Uses chrome.sidePanel (not supported)
    - No PrivacyInfo.xcprivacy detected

📊 Summary
  Errors:   2
  Warnings: 5
  Notices:  3

Run with --fix to auto-fix applicable issues.
```

#### JSON Output

```json
{
  "extension": {
    "name": "my-extension",
    "version": "1.0.0",
    "manifestVersion": 3
  },
  "results": {
    "manifest": {
      "errors": [],
      "warnings": [
        {
          "code": "MISSING_GECKO_DATA_COLLECTION",
          "message": "Missing gecko.data_collection_permissions",
          "fix": "auto"
        }
      ]
    },
    "csp": {
      "errors": [
        {
          "code": "EVAL_USAGE",
          "file": "src/utils.js",
          "line": 42,
          "fix": "manual"
        }
      ]
    },
    "compatibility": {
      "chrome": { "supported": true, "issues": [] },
      "firefox": { "supported": true, "issues": [...] },
      "safari": { "supported": false, "issues": [...] }
    }
  },
  "summary": {
    "errors": 2,
    "warnings": 5,
    "notices": 3,
    "fixable": 3
  }
}
```

### Step 8: Auto-Fix (if --fix)

Fixable issues:

| Issue | Fix |
|-------|-----|
| Missing gecko.id | Generate from package name |
| Missing gecko.strict_min_version | Add `"109.0"` |
| Missing gecko.data_collection_permissions | Add empty arrays |
| Missing minimum_chrome_version | Add `"116"` |
| Missing icon sizes | Generate from largest |

Non-fixable (manual required):

| Issue | Guidance |
|-------|----------|
| `<all_urls>` usage | Narrow to specific domains |
| eval() in code | Refactor to static code |
| Unsupported API usage | Feature detection or polyfill |

## Validation Rules Reference

### Store Rejection Rules

| Rule | Chrome | Firefox | Safari |
|------|--------|---------|--------|
| Obfuscated code | Reject | Reject | Reject |
| Remote code execution | Reject | Reject | Reject |
| Broad host permissions without justification | Reject | Reject | Reject |
| eval() / new Function() | Reject | Reject | Reject |
| Missing privacy policy (if collecting data) | Reject | Reject | Reject |
| Missing gecko.id | N/A | Reject | N/A |
| Missing PrivacyInfo.xcprivacy | N/A | N/A | Reject |

### Performance Checks

| Check | Threshold | Severity |
|-------|-----------|----------|
| Total bundle size | >5MB | warning |
| Single file size | >1MB | warning |
| Content script size | >500KB | warning |
| Icon files missing | any | error |

## Examples

```bash
# Validate current directory
/validate-extension

# Validate specific path
/validate-extension ./my-extension

# Validate for all browsers
/validate-extension --browsers all

# Strict mode (fail on warnings)
/validate-extension --strict

# Auto-fix issues
/validate-extension --fix

# JSON output for CI
/validate-extension --output json > validation.json
```

## Integration with CI

```yaml
# GitHub Actions example
- name: Validate Extension
  run: |
    npx wxt build
    npx web-ext lint --source-dir dist/chrome-mv3
    # Additional custom checks from this command
```

## Related

- `/create-extension` - Scaffold new extension with proper defaults
- `extension-anti-patterns` skill - Common mistakes to avoid
- `wxt-framework-patterns` skill - Framework patterns and hardening rules
