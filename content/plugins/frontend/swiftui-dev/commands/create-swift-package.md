# Create Swift Package

Initialize a new Swift Package with proper structure and configuration.

## Arguments

- `<name>` - Package name in PascalCase
- `--path <path>` - Target directory (default: current directory)
- `--type <type>` - Package type: `library` (default), `executable`, `plugin`
- `--platforms <platforms>` - Supported platforms (e.g., `macOS14,iOS17`)
- `--dependencies <deps>` - Comma-separated dependencies

## Output

Creates package directory with:

- `Package.swift` manifest
- `Sources/<Name>/` directory
- `Tests/<Name>Tests/` directory
- `.gitignore`

## Examples

```bash
# Basic library
/create-swift-package MyLibrary

# macOS executable
/create-swift-package MyTool --type executable --platforms macOS14

# With dependencies
/create-swift-package MyApp --dependencies "swift-argument-parser,swift-collections"

# Specify path
/create-swift-package DataKit --path Packages/DataKit --platforms "macOS14,iOS17"
```

## Generated Package.swift

```swift
// swift-tools-version: 5.10

import PackageDescription

let package = Package(
    name: "<Name>",
    platforms: [
        .macOS(.v14),
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "<Name>",
            targets: ["<Name>"]
        ),
    ],
    dependencies: [
        // Dependencies here
    ],
    targets: [
        .target(
            name: "<Name>",
            dependencies: []
        ),
        .testTarget(
            name: "<Name>Tests",
            dependencies: ["<Name>"]
        ),
    ]
)
```

## Directory Structure

```text
<Name>/
├── Package.swift
├── Sources/
│   └── <Name>/
│       └── <Name>.swift
├── Tests/
│   └── <Name>Tests/
│       └── <Name>Tests.swift
└── .gitignore
```

## Common Dependencies

| Package | URL | Use Case |
|---------|-----|----------|
| swift-argument-parser | apple/swift-argument-parser | CLI tools |
| swift-collections | apple/swift-collections | Data structures |
| swift-algorithms | apple/swift-algorithms | Sequence algorithms |
| swift-async-algorithms | apple/swift-async-algorithms | Async sequences |
| GRDB.swift | groue/GRDB.swift | SQLite |
| duckdb-swift | duckdb/duckdb-swift | Analytics SQL |
