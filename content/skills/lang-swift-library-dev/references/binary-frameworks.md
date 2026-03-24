# Binary Frameworks & XCFrameworks

Guide for creating and distributing binary Swift frameworks.

## Creating XCFramework

### Build for All Platforms

```bash
# Build for iOS device
xcodebuild archive \
  -scheme MyPackage \
  -destination "generic/platform=iOS" \
  -archivePath ./build/ios \
  SKIP_INSTALL=NO \
  BUILD_LIBRARY_FOR_DISTRIBUTION=YES

# Build for iOS simulator
xcodebuild archive \
  -scheme MyPackage \
  -destination "generic/platform=iOS Simulator" \
  -archivePath ./build/ios-sim \
  SKIP_INSTALL=NO \
  BUILD_LIBRARY_FOR_DISTRIBUTION=YES

# Build for macOS
xcodebuild archive \
  -scheme MyPackage \
  -destination "generic/platform=macOS" \
  -archivePath ./build/macos \
  SKIP_INSTALL=NO \
  BUILD_LIBRARY_FOR_DISTRIBUTION=YES
```

### Create XCFramework Bundle

```bash
xcodebuild -create-xcframework \
  -framework ./build/ios.xcarchive/Products/Library/Frameworks/MyPackage.framework \
  -framework ./build/ios-sim.xcarchive/Products/Library/Frameworks/MyPackage.framework \
  -framework ./build/macos.xcarchive/Products/Library/Frameworks/MyPackage.framework \
  -output ./MyPackage.xcframework
```

## Distributing Binary Framework

### Remote Binary Target

```swift
// Package.swift with binary target
let package = Package(
    name: "MyPackage",
    products: [
        .library(name: "MyPackage", targets: ["MyPackage"]),
    ],
    targets: [
        .binaryTarget(
            name: "MyPackage",
            url: "https://github.com/user/repo/releases/download/1.0.0/MyPackage.xcframework.zip",
            checksum: "abc123..."
        ),
    ]
)
```

### Local Binary Target

```swift
.binaryTarget(
    name: "MyPackage",
    path: "./Frameworks/MyPackage.xcframework"
)
```

### Computing Checksum

```bash
swift package compute-checksum MyPackage.xcframework.zip
```

## Module Stability

Enable module stability for binary compatibility:

```bash
xcodebuild build \
  -scheme MyPackage \
  BUILD_LIBRARY_FOR_DISTRIBUTION=YES \
  SWIFT_EMIT_MODULE_INTERFACE=YES
```

This generates `.swiftinterface` files that allow the framework to work with different Swift compiler versions.

## Troubleshooting

### "Missing required module" Error

Ensure `BUILD_LIBRARY_FOR_DISTRIBUTION=YES` is set when building.

### Architecture Mismatch

Build for all required architectures (arm64, x86_64) and combine into single XCFramework.

### Swift Version Compatibility

With module stability enabled, frameworks built with Swift 5.1+ work with later Swift versions.
