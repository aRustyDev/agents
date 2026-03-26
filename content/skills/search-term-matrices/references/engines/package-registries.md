# Package Registries

Operators and tips for language-specific package registries.

## Table of Contents

- [npm](#npm)
- [crates.io](#cratesio)
- [docs.rs](#docsrs)
- [PyPI](#pypi)
- [GoDocs (pkg.go.dev)](#godocs-pkggodev)
- [HexDocs](#hexdocs)

---

## npm

The Node.js / JavaScript package registry. Largest registry by package count.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `crdt collaborative` |
| Exact package | (package name) | `yjs` |
| Scope filter | `@scope/` | `@automerge/automerge` |
| Author filter | `author:name` | `author:mafintosh` |
| Keywords filter | `keywords:tag` | `keywords:crdt` |
| Maintainer filter | `maintainer:name` | `maintainer:dmonad` |

### Sorting Options

- Optimal (default): npm's relevance algorithm
- Popularity: based on download counts
- Quality: based on maintenance, tests, documentation
- Maintenance: based on recent activity

### Tips

- The `keywords` field in package.json is indexed; use `keywords:` to search it directly
- Check weekly download counts as a rough proxy for adoption
- Look at the "Dependencies" and "Dependents" tabs to gauge ecosystem integration
- npm search results include a quality/popularity/maintenance score breakdown
- For TypeScript projects, also check if `@types/package` exists for type definitions
- The npm API (`registry.npmjs.org`) supports programmatic search

---

## crates.io

The Rust package registry.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `crdt collaborative` |
| Exact crate | (crate name) | `automerge` |
| Category filter | (UI sidebar) | Filter by category (e.g., "Data structures", "Algorithms") |

### Sorting Options

- Relevance (default)
- All-Time Downloads
- Recent Downloads
- Recent Updates
- Newly Added

### Special Features

- **Categories:** Curated category taxonomy (Algorithms, Data structures, Concurrency, etc.)
- **Feature flags:** Crates list their Cargo features for conditional compilation
- **Version history:** Full version history with yanked version indicators
- **Owner/team info:** Shows who maintains the crate

### Tips

- Sort by "Recent Downloads" to find actively-used crates (not just historically popular ones)
- Check the "Versions" tab for release cadence; frequent releases suggest active maintenance
- The category taxonomy is curated and reliable for narrowing searches
- Cross-reference with docs.rs for API documentation quality
- Look at the `#[cfg(feature = "...")]` flags to understand optional capabilities

---

## docs.rs

Automatically generated API documentation for every crate published on crates.io.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text in search bar) | `crdt text` |
| Crate docs | (URL path) | `docs.rs/automerge/latest` |
| Version-specific | (URL path) | `docs.rs/automerge/0.5.0` |
| Feature-flag docs | (URL query) | `docs.rs/crate/version/features` |
| Platform docs | (URL path) | `docs.rs/crate/version/platform` |

### Special Features

- **Automatic builds:** Every crate version published to crates.io gets docs built automatically
- **Source links:** Every type, function, and method links back to its source code
- **Feature flag toggle:** View docs with specific feature flags enabled/disabled
- **Cross-crate links:** `#[doc]` links resolve across crate boundaries

### Tips

- docs.rs is the canonical documentation source for Rust crates; prefer it over READMEs
- Use the search bar within a crate's docs to find specific types, traits, or functions
- Check which feature flags are available and how they change the API surface
- The "All Items" page gives a complete index of everything a crate exports
- Build failures on docs.rs sometimes indicate portability or dependency issues

---

## PyPI

The Python Package Index. Primary registry for Python packages.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `crdt collaborative` |
| Exact package | (package name) | `automerge` |
| Classifier filter | (UI sidebar) | Filter by topic, license, Python version, etc. |

### Classifiers (Selected)

| Classifier | Example |
|------------|---------|
| Topic | `Topic :: Software Development :: Libraries` |
| License | `License :: OSI Approved :: MIT License` |
| Python version | `Programming Language :: Python :: 3.12` |
| Development status | `Development Status :: 5 - Production/Stable` |
| Framework | `Framework :: Django` |

### Tips

- PyPI classifiers are self-reported by package authors; not all packages use them accurately
- Check the "Project links" section for source repo, documentation, and changelog URLs
- The "Release history" tab shows release cadence and latest version date
- Use `pip index versions package-name` to list available versions from the CLI
- For data science packages, also check conda-forge as some packages are conda-only
- The PyPI JSON API (`pypi.org/pypi/package/json`) is useful for programmatic queries

---

## GoDocs (pkg.go.dev)

Official documentation site for Go packages and modules.

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text) | `crdt collaborative` |
| Module path | (URL path) | `pkg.go.dev/github.com/automerge/automerge-go` |
| Symbol search | `#SymbolName` | `pkg.go.dev/package#TypeName` |

### Special Features

- **Import graph:** Shows which packages import a given module
- **License detection:** Automatically detects and displays license information
- **Version list:** All tagged versions with their documentation
- **Vulnerability reports:** Integrated Go vulnerability database checks
- **Unit page:** Shows documentation for individual packages within a module

### Tips

- pkg.go.dev indexes all publicly-accessible Go modules, not just those in a registry
- The "Imported by" count is a strong signal of adoption in the Go ecosystem
- Check the "Versions" tab to see if the module follows semantic versioning properly
- The vulnerability database integration highlights known CVEs in dependencies
- Use the symbol search (`#Name`) to jump directly to a type, function, or method

---

## HexDocs

Documentation hosting for Hex packages (Elixir, Erlang ecosystem).

### Operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Keyword search | (free text on hex.pm) | `crdt distributed` |
| Package docs | (URL path) | `hexdocs.pm/package_name` |
| Version-specific | (URL path) | `hexdocs.pm/package_name/0.1.0` |
| Module search | (within package docs) | Search bar within HexDocs pages |
| Function search | (within package docs) | `hexdocs.pm/package/Module.html#function/arity` |

### Special Features

- **ExDoc integration:** Documentation generated from Elixir's ExDoc tool with typespecs and examples
- **Search within package:** Full-text search across a package's documentation
- **Typespec rendering:** Function signatures include @spec type annotations
- **Guides section:** Many packages include long-form guides alongside API docs

### Tips

- HexDocs is the canonical documentation source for the Elixir/Erlang ecosystem
- Search on hex.pm (the registry) to find packages, then read docs on hexdocs.pm
- The "Guides" section often contains tutorials and conceptual documentation beyond the API reference
- Check the "Dependencies" tab on hex.pm to understand what a package pulls in
- Hex download counts are smaller than npm/PyPI but still useful for relative popularity within the ecosystem
