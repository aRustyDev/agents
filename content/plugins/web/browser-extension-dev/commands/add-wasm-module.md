---
name: add-wasm-module
description: Add a WebAssembly module to a browser extension project with Rust scaffolding, wasm-pack build configuration, and cross-browser loading code.
---

# Add WASM Module

Scaffold a Rust WASM module for browser extension development with proper build configuration and cross-browser loading patterns.

## Arguments

- `<module-name>` - Name for the WASM module (kebab-case)
- `--template <type>` - Module template: `minimal` | `crypto` | `parser` | `compression` (default: minimal)
- `--target <browser>` - Primary browser target: `all` | `chrome` | `firefox` | `safari` (default: all)

## Workflow

### Step 1: Validate Environment

1. Check for required tools:

   ```bash
   command -v cargo || echo "Install Rust: https://rustup.rs"
   command -v wasm-pack || echo "Install wasm-pack: cargo install wasm-pack"
   ```

2. Verify project structure:
   - Must be in a WXT or browser extension project
   - Check for `wxt.config.ts` or `manifest.json`

### Step 2: Create Rust Project

Create the WASM module directory structure:

```text
wasm/<module-name>/
├── Cargo.toml
├── src/
│   └── lib.rs
└── tests/
    └── web.rs
```

Generate `Cargo.toml`:

```toml
[package]
name = "<module-name>"
version = "0.1.0"
edition = "2021"
authors = ["Extension Developer"]
description = "WASM module for browser extension"

[lib]
crate-type = ["cdylib", "rlib"]

[dependencies]
wasm-bindgen = "0.2"
js-sys = "0.3"
web-sys = { version = "0.3", features = [
    "console",
    "Performance",
    "Window"
]}
serde = { version = "1.0", features = ["derive"] }
serde-wasm-bindgen = "0.6"

# Optional: smaller allocator
wee_alloc = { version = "0.4", optional = true }

[dev-dependencies]
wasm-bindgen-test = "0.3"

[features]
default = []
small = ["wee_alloc"]

[profile.release]
opt-level = "s"
lto = true
codegen-units = 1
strip = true
panic = "abort"
```

Generate `src/lib.rs` based on template:

**minimal template:**

```rust
use wasm_bindgen::prelude::*;

#[cfg(feature = "small")]
#[global_allocator]
static ALLOC: wee_alloc::WeeAlloc = wee_alloc::WeeAlloc::INIT;

#[wasm_bindgen]
pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

#[wasm_bindgen]
pub fn process(data: &[u8]) -> Vec<u8> {
    // Process data and return result
    data.to_vec()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_greet() {
        assert_eq!(greet("World"), "Hello, World!");
    }
}
```

**crypto template:**

```rust
use wasm_bindgen::prelude::*;
use sha2::{Sha256, Digest};

#[wasm_bindgen]
pub fn hash_sha256(data: &[u8]) -> Vec<u8> {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hasher.finalize().to_vec()
}

#[wasm_bindgen]
pub fn hash_sha256_hex(data: &[u8]) -> String {
    let hash = hash_sha256(data);
    hex::encode(hash)
}
```

Add to Cargo.toml for crypto:

```toml
sha2 = "0.10"
hex = "0.4"
```

**parser template:**

```rust
use wasm_bindgen::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct ParseResult {
    pub success: bool,
    pub data: Option<serde_json::Value>,
    pub error: Option<String>,
}

#[wasm_bindgen]
pub fn parse_json(input: &str) -> JsValue {
    match serde_json::from_str::<serde_json::Value>(input) {
        Ok(data) => {
            let result = ParseResult {
                success: true,
                data: Some(data),
                error: None,
            };
            serde_wasm_bindgen::to_value(&result).unwrap()
        }
        Err(e) => {
            let result = ParseResult {
                success: false,
                data: None,
                error: Some(e.to_string()),
            };
            serde_wasm_bindgen::to_value(&result).unwrap()
        }
    }
}
```

Add to Cargo.toml for parser:

```toml
serde_json = "1.0"
```

**compression template:**

```rust
use wasm_bindgen::prelude::*;
use flate2::Compression;
use flate2::write::{GzEncoder, GzDecoder};
use std::io::{Write, Read};

#[wasm_bindgen]
pub fn compress_gzip(data: &[u8]) -> Vec<u8> {
    let mut encoder = GzEncoder::new(Vec::new(), Compression::default());
    encoder.write_all(data).unwrap();
    encoder.finish().unwrap()
}

#[wasm_bindgen]
pub fn decompress_gzip(data: &[u8]) -> Result<Vec<u8>, JsValue> {
    let mut decoder = GzDecoder::new(data);
    let mut result = Vec::new();
    decoder.read_to_end(&mut result)
        .map_err(|e| JsValue::from_str(&e.to_string()))?;
    Ok(result)
}
```

Add to Cargo.toml for compression:

```toml
flate2 = "1.0"
```

### Step 3: Create TypeScript Bindings

Generate `entrypoints/wasm/<module-name>.ts`:

```typescript
// WASM module loader for <module-name>
import type { InitOutput } from '../../wasm/<module-name>/pkg/<module-name>';

let wasmInstance: InitOutput | null = null;
let initPromise: Promise<InitOutput> | null = null;

/**
 * Initialize the WASM module
 * Safe to call multiple times - returns cached instance
 */
export async function initWasm(): Promise<InitOutput> {
  if (wasmInstance) {
    return wasmInstance;
  }

  if (initPromise) {
    return initPromise;
  }

  initPromise = (async () => {
    const wasmUrl = browser.runtime.getURL('wasm/<module-name>/pkg/<module-name>_bg.wasm');

    // Dynamic import to handle module loading
    const wasm = await import('../../wasm/<module-name>/pkg/<module-name>');

    // Initialize with explicit WASM URL for extension context
    await wasm.default(wasmUrl);

    wasmInstance = wasm;
    return wasm;
  })();

  return initPromise;
}

/**
 * Check if WASM module is ready
 */
export function isWasmReady(): boolean {
  return wasmInstance !== null;
}

/**
 * Get the initialized WASM instance
 * Throws if not initialized
 */
export function getWasm(): InitOutput {
  if (!wasmInstance) {
    throw new Error('WASM module not initialized. Call initWasm() first.');
  }
  return wasmInstance;
}

// Re-export WASM functions for convenience
export * from '../../wasm/<module-name>/pkg/<module-name>';
```

### Step 4: Update WXT Configuration

Add WASM build integration to `wxt.config.ts`:

```typescript
import { defineConfig } from 'wxt';
import { execSync } from 'child_process';

export default defineConfig({
  // ... existing config
  hooks: {
    'build:before': async () => {
      console.log('Building WASM modules...');
      execSync('wasm-pack build wasm/<module-name> --target web --out-dir pkg', {
        stdio: 'inherit'
      });
    }
  },
  vite: () => ({
    build: {
      rollupOptions: {
        // Ensure WASM files are copied
        external: [/\.wasm$/]
      }
    },
    optimizeDeps: {
      exclude: ['*.wasm']
    }
  })
});
```

### Step 5: Add to web_accessible_resources

Update manifest (via wxt.config.ts):

```typescript
export default defineConfig({
  manifest: {
    web_accessible_resources: [
      {
        resources: ['wasm/<module-name>/pkg/*'],
        matches: ['<all_urls>']
      }
    ]
  }
});
```

### Step 6: Create Build Script

Add to `package.json`:

```json
{
  "scripts": {
    "wasm:build": "wasm-pack build wasm/<module-name> --target web --out-dir pkg",
    "wasm:build:release": "wasm-pack build wasm/<module-name> --target web --out-dir pkg --release",
    "wasm:test": "wasm-pack test --headless --chrome wasm/<module-name>",
    "wasm:optimize": "wasm-opt -Os wasm/<module-name>/pkg/<module-name>_bg.wasm -o wasm/<module-name>/pkg/<module-name>_bg.wasm"
  }
}
```

### Step 7: Report

````markdown
## WASM Module Added

| Field | Value |
|-------|-------|
| Module | <module-name> |
| Template | <template> |
| Location | wasm/<module-name>/ |
| Bindings | entrypoints/wasm/<module-name>.ts |

**Build commands:**

- `npm run wasm:build` - Build for development
- `npm run wasm:build:release` - Build optimized for production
- `npm run wasm:test` - Run WASM tests

**Usage:**

```typescript
import { initWasm, greet } from './wasm/<module-name>';

await initWasm();
const result = greet('World');
```

**Next steps:**

1. Implement your WASM functions in `wasm/<module-name>/src/lib.rs`
2. Run `npm run wasm:build` to compile
3. Import and use in your extension code
````

## Examples

```bash
# Add minimal WASM module
/add-wasm-module crypto-utils

# Add with crypto template
/add-wasm-module hash-functions --template crypto

# Add parser module for Chrome
/add-wasm-module json-parser --template parser --target chrome

# Add compression module
/add-wasm-module compressor --template compression
```

## Fallback Patterns

The generated code includes fallbacks for browsers without streaming compilation:

```typescript
// Included in generated loader
async function loadWasm(url: string): Promise<WebAssembly.Module> {
  const response = await fetch(url);

  if (WebAssembly.instantiateStreaming) {
    // Modern browsers - streaming compilation
    const { instance } = await WebAssembly.instantiateStreaming(response);
    return instance;
  } else {
    // Safari fallback - buffer-based
    const bytes = await response.arrayBuffer();
    const { instance } = await WebAssembly.instantiate(bytes);
    return instance;
  }
}
```

## Cross-Browser Considerations

| Browser | Notes |
|---------|-------|
| Chrome | Full WASM support, streaming compilation |
| Firefox | Full WASM support, streaming compilation |
| Safari | No streaming from cross-origin, bundle required |
| Edge | Same as Chrome (Chromium-based) |

The generated code handles these differences automatically.
