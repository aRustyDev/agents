# WASM Architecture Decision

Decision framework for WebAssembly usage in browser extensions, including browser-specific loading patterns, architectural patterns, and performance considerations.

## Decision Framework

### When to Use WASM

| Use Case | Recommendation | Rationale |
|----------|---------------|-----------|
| Cryptographic operations | **Strong yes** | 10-100x faster, constant-time |
| Image/video processing | **Strong yes** | Parallelizable, memory efficient |
| Compression/decompression | **Yes** | CPU-intensive, existing Rust libs |
| Complex parsing (binary) | **Yes** | Type safety, predictable perf |
| Scientific computing | **Yes** | Numerical precision, speed |
| Simple data transforms | **No** | Overhead exceeds benefit |
| DOM manipulation | **No** | JS required, no benefit |
| API calls/networking | **No** | I/O bound, not CPU bound |
| String manipulation | **Maybe** | Only for large-scale ops |

### Decision Matrix

Score each factor 1-5, then calculate totals:

| Factor | Weight | Score |
|--------|--------|-------|
| CPU intensity | 3x | [1-5] |
| Data volume | 2x | [1-5] |
| Performance criticality | 2x | [1-5] |
| Existing Rust/C++ code | 2x | [1-5] |
| Team Rust expertise | 1x | [1-5] |

**Scoring guide:**
- **Total 30+**: Strong WASM candidate
- **Total 20-29**: Consider WASM
- **Total <20**: Use JavaScript

### Anti-Patterns

| Pattern | Problem | Alternative |
|---------|---------|-------------|
| WASM for DOM access | Impossible, must call JS | Keep DOM in JS layer |
| WASM for simple logic | Overhead exceeds benefit | Native JS |
| Frequent WASM↔JS calls | Call overhead ~10μs each | Batch operations |
| Large data copies | Memory duplication | Use SharedArrayBuffer |
| Sync WASM in main thread | Blocks UI | Web Worker or async |

## Browser-Specific Loading Patterns

### Chrome (MV3 Service Worker)

```typescript
// Service worker has no DOM, but full WASM support
let wasmModule: WebAssembly.Module | null = null;

// Pre-compile on install for fast instantiation
chrome.runtime.onInstalled.addListener(async () => {
  const response = await fetch(chrome.runtime.getURL('wasm/module.wasm'));
  wasmModule = await WebAssembly.compileStreaming(response);
});

// Instantiate per-use (service worker may have terminated)
async function getWasmInstance(): Promise<WebAssembly.Instance> {
  if (!wasmModule) {
    const response = await fetch(chrome.runtime.getURL('wasm/module.wasm'));
    wasmModule = await WebAssembly.compileStreaming(response);
  }
  return new WebAssembly.Instance(wasmModule);
}
```

### Firefox (MV3 or MV2)

```typescript
// Firefox supports both event pages and service workers
// Event page approach (MV2) - has DOM access
let wasmInstance: WebAssembly.Instance | null = null;

async function initWasm(): Promise<WebAssembly.Instance> {
  if (wasmInstance) return wasmInstance;

  const response = await fetch(browser.runtime.getURL('wasm/module.wasm'));

  // Firefox supports streaming compilation
  const { instance } = await WebAssembly.instantiateStreaming(response);
  wasmInstance = instance;

  return instance;
}
```

### Safari

```typescript
// Safari has strict WASM policies
// 1. No streaming from cross-origin (must use buffer)
// 2. WASM files must be in extension bundle
// 3. Content-Type must be application/wasm

async function initWasmSafari(): Promise<WebAssembly.Instance> {
  const response = await fetch(browser.runtime.getURL('wasm/module.wasm'));

  // Safari fallback: no streaming compilation
  const bytes = await response.arrayBuffer();
  const { instance } = await WebAssembly.instantiate(bytes);

  return instance;
}

// Cross-browser wrapper
async function initWasmCrossBrowser(): Promise<WebAssembly.Instance> {
  const response = await fetch(browser.runtime.getURL('wasm/module.wasm'));

  if (typeof WebAssembly.instantiateStreaming === 'function') {
    try {
      const { instance } = await WebAssembly.instantiateStreaming(response);
      return instance;
    } catch {
      // Fallback on streaming failure
    }
  }

  // Safari and fallback path
  const bytes = await response.arrayBuffer();
  const { instance } = await WebAssembly.instantiate(bytes);
  return instance;
}
```

### Content Script Loading

```typescript
// Content scripts run in isolated world
// WASM must be in web_accessible_resources

async function loadWasmInContentScript(): Promise<WebAssembly.Instance> {
  // Use chrome.runtime.getURL for proper extension URL
  const wasmUrl = chrome.runtime.getURL('wasm/module.wasm');

  const response = await fetch(wasmUrl, {
    credentials: 'omit', // Don't send cookies
    cache: 'force-cache' // Cache aggressively
  });

  if (!response.ok) {
    throw new Error(`Failed to load WASM: ${response.status}`);
  }

  return initWasmCrossBrowser();
}
```

## Architecture Patterns

### Pattern 1: Background-Only WASM

WASM runs only in service worker, content scripts communicate via messaging.

```text
┌─────────────────┐     message      ┌──────────────────┐
│ Content Script  │◄───────────────►│ Service Worker   │
│ (no WASM)       │                  │ (WASM loaded)    │
└─────────────────┘                  └──────────────────┘

Pros: Single WASM instance, simpler memory management
Cons: Message serialization overhead, latency
Best for: Infrequent operations, small data
```

```typescript
// content-script.ts
async function processData(data: Uint8Array): Promise<Uint8Array> {
  const response = await chrome.runtime.sendMessage({
    type: 'WASM_PROCESS',
    data: Array.from(data) // Must serialize
  });
  return new Uint8Array(response.result);
}

// background.ts
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'WASM_PROCESS') {
    processWithWasm(new Uint8Array(msg.data))
      .then(result => sendResponse({ result: Array.from(result) }));
    return true;
  }
});
```

### Pattern 2: Content Script WASM

WASM runs in each content script instance.

```text
┌────────────────────────────────────────────────────────┐
│                     Tab 1                               │
│  ┌─────────────────┐     ┌──────────────────────────┐ │
│  │ Content Script  │────►│ WASM (per-tab instance)  │ │
│  └─────────────────┘     └──────────────────────────┘ │
└────────────────────────────────────────────────────────┘

Pros: No message latency, parallel processing
Cons: Memory per tab, startup per tab
Best for: Per-page processing, large data
```

```typescript
// content-script.ts
import init, { process } from './wasm/module';

let wasmReady = false;

async function ensureWasm(): Promise<void> {
  if (wasmReady) return;
  await init(chrome.runtime.getURL('wasm/module_bg.wasm'));
  wasmReady = true;
}

async function processLocally(data: Uint8Array): Promise<Uint8Array> {
  await ensureWasm();
  return process(data);
}
```

### Pattern 3: Web Worker WASM

WASM runs in dedicated worker, avoiding main thread blocking.

```text
┌─────────────────┐     postMessage    ┌─────────────────┐
│ Content Script  │◄──────────────────►│ Web Worker      │
│ (main thread)   │                    │ (WASM loaded)   │
└─────────────────┘                    └─────────────────┘

Pros: Non-blocking, parallelizable
Cons: Setup complexity, message overhead
Best for: Heavy computation, real-time processing
```

```typescript
// wasm-worker.ts
import init, { process } from './wasm/module';

self.onmessage = async (e) => {
  await init();

  const result = process(e.data.input);

  // Transfer buffer ownership (zero-copy)
  self.postMessage(
    { result: result.buffer },
    [result.buffer]
  );
};

// content-script.ts
const worker = new Worker(chrome.runtime.getURL('wasm-worker.js'));

function processAsync(data: Uint8Array): Promise<Uint8Array> {
  return new Promise((resolve) => {
    worker.onmessage = (e) => resolve(new Uint8Array(e.data.result));
    worker.postMessage(
      { input: data.buffer },
      [data.buffer] // Transfer ownership
    );
  });
}
```

### Pattern 4: Offscreen Document (Chrome MV3)

Use offscreen document for DOM-dependent WASM operations.

```typescript
// background.ts
async function ensureOffscreen(): Promise<void> {
  if (await chrome.offscreen.hasDocument()) return;

  await chrome.offscreen.createDocument({
    url: 'offscreen.html',
    reasons: ['DOM_PARSER', 'WORKERS'],
    justification: 'WASM processing with DOM'
  });
}

async function processViaOffscreen(data: Uint8Array): Promise<Uint8Array> {
  await ensureOffscreen();

  const response = await chrome.runtime.sendMessage({
    target: 'offscreen',
    type: 'WASM_PROCESS',
    data: Array.from(data)
  });

  return new Uint8Array(response.result);
}
```

## Performance Benchmarks

### Typical Performance Gains

| Operation | JS (ms) | WASM (ms) | Speedup |
|-----------|---------|-----------|---------|
| SHA-256 (1MB) | 45 | 8 | 5.6x |
| AES-256 encrypt | 120 | 15 | 8x |
| JSON parse (10MB) | 150 | 40 | 3.75x |
| GZIP compress | 200 | 35 | 5.7x |
| Image resize | 300 | 50 | 6x |
| Regex (complex) | 80 | 25 | 3.2x |
| Simple sum | 0.1 | 0.2 | 0.5x (slower!) |

### When JavaScript is Faster

| Scenario | Why JS Wins |
|----------|-------------|
| <1ms operations | WASM call overhead dominates |
| Single string ops | JS strings optimized |
| DOM manipulation | Must call JS anyway |
| Small arrays (<1KB) | Copy overhead dominates |
| JIT-optimized hot paths | V8/SpiderMonkey excellent |

### Benchmarking Template

```typescript
async function benchmarkOperation(
  jsImpl: (data: Uint8Array) => Uint8Array,
  wasmImpl: (data: Uint8Array) => Uint8Array,
  data: Uint8Array,
  iterations: number = 100
): Promise<{ js: number; wasm: number; speedup: number }> {
  // Warm up
  jsImpl(data);
  wasmImpl(data);

  // Measure JS
  const jsStart = performance.now();
  for (let i = 0; i < iterations; i++) {
    jsImpl(data);
  }
  const jsTime = (performance.now() - jsStart) / iterations;

  // Measure WASM
  const wasmStart = performance.now();
  for (let i = 0; i < iterations; i++) {
    wasmImpl(data);
  }
  const wasmTime = (performance.now() - wasmStart) / iterations;

  return {
    js: jsTime,
    wasm: wasmTime,
    speedup: jsTime / wasmTime
  };
}
```

## Memory Architecture

### Extension Memory Limits

| Context | Chrome | Firefox | Safari |
|---------|--------|---------|--------|
| Service Worker | 128MB | 512MB | 128MB |
| Event Page | N/A | 512MB | N/A |
| Content Script | Tab limit | Tab limit | Tab limit |
| Popup | 128MB | 128MB | 128MB |

### Memory-Efficient Patterns

```rust
// Rust: Reuse buffers to avoid allocation
static mut BUFFER: Vec<u8> = Vec::new();

#[wasm_bindgen]
pub fn process_reuse(data: &[u8]) -> *const u8 {
    unsafe {
        BUFFER.clear();
        BUFFER.extend_from_slice(data);
        // Process BUFFER...
        BUFFER.as_ptr()
    }
}

// Return length separately
#[wasm_bindgen]
pub fn get_result_len() -> usize {
    unsafe { BUFFER.len() }
}
```

```typescript
// TypeScript: Read result without copy
const ptr = wasmInstance.exports.process_reuse(inputPtr);
const len = wasmInstance.exports.get_result_len();
const memory = new Uint8Array(wasmInstance.exports.memory.buffer);
const result = memory.slice(ptr, ptr + len);
```

### Streaming Processing

```typescript
// Process large files in chunks to stay within memory limits
async function processLargeFile(
  file: File,
  chunkSize: number = 1024 * 1024 // 1MB chunks
): Promise<Uint8Array[]> {
  const results: Uint8Array[] = [];
  const reader = file.stream().getReader();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const processed = await processChunkWithWasm(value);
    results.push(processed);
  }

  return results;
}
```

## Related Resources

- **wasm-extension-integration skill**: Build pipeline and tooling
- **wasm-integration-advisor agent**: Suitability analysis
- **wasm-decision-report style**: Report format
- **/add-wasm-module command**: Scaffolding tool
