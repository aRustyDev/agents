# Dependencies & Troubleshooting

## Common Dependencies

### Logging

```swift
dependencies: [
    .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),
]

// Usage
import Logging

let logger = Logger(label: "com.example.mypackage")
logger.info("Processing started")
```

### Async/Concurrency

```swift
dependencies: [
    .package(url: "https://github.com/apple/swift-async-algorithms.git", from: "1.0.0"),
]

// Provides AsyncSequence utilities like merge, debounce, throttle
```

### Argument Parsing (for CLIs)

```swift
dependencies: [
    .package(url: "https://github.com/apple/swift-argument-parser.git", from: "1.3.0"),
]
```

### Testing

```swift
dependencies: [
    .package(url: "https://github.com/pointfreeco/swift-snapshot-testing.git", from: "1.15.0"),
]
```

### Networking (Server-Side)

```swift
dependencies: [
    .package(url: "https://github.com/swift-server/async-http-client.git", from: "1.20.0"),
]
```

### Date/Time

```swift
dependencies: [
    .package(url: "https://github.com/apple/swift-format.git", from: "509.0.0"),
]
```

---

## Troubleshooting

### Package Resolution Issues

**Problem:** `error: package at '...' is using Swift tools version but package is at '...'`

**Solution:** Update `swift-tools-version` in Package.swift header

```swift
// swift-tools-version: 5.9
```

### Missing Module Errors

**Problem:** `error: no such module 'MyPackage'`

**Solution:** Ensure target dependencies are correctly specified

```swift
.testTarget(
    name: "MyPackageTests",
    dependencies: ["MyPackage"]  // Add module dependency
)
```

### Xcode Build Issues

**Problem:** Xcode can't find package

**Solution:**
1. Delete derived data: `rm -rf ~/Library/Developer/Xcode/DerivedData`
2. `File > Packages > Reset Package Caches`
3. `swift package resolve`

### Dependency Conflicts

**Problem:** Two packages require incompatible versions

**Solution:**
```swift
// Force specific version
.package(url: "...", exact: "1.2.3")

// Or use broader range
.package(url: "...", "1.0.0"..<"3.0.0")
```

### Local Package Development

**Problem:** Need to test changes to dependency locally

**Solution:** Use path-based dependency temporarily

```swift
// Development only - switch back to URL before committing
.package(path: "../LocalPackage")
```

### Slow Resolution

**Problem:** `swift package resolve` takes too long

**Solution:**
```bash
# Clear cache
rm -rf ~/Library/Caches/org.swift.swiftpm

# Resolve with verbose output
swift package resolve -v
```

### Checksum Mismatch

**Problem:** Binary target checksum doesn't match

**Solution:**
```bash
# Recompute checksum
swift package compute-checksum MyPackage.xcframework.zip
# Update Package.swift with new checksum
```
