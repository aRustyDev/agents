---
name: lang-haskell-library-dev
description: Haskell-specific library development patterns. Use when creating Haskell libraries, designing type-safe public APIs, organizing Cabal/Stack projects, writing property-based tests with QuickCheck, generating Haddock documentation, or publishing to Hackage. Extends meta-library-dev with Haskell tooling and idioms.
---

# Haskell Library Development

Haskell-specific patterns for library development. This skill extends `meta-library-dev` with Haskell tooling, type-driven design principles, and ecosystem practices.

## This Skill Extends

- `meta-library-dev` - Foundational library patterns (API design, versioning, testing strategies)
- `lang-haskell-dev` - Core Haskell language patterns and idioms

For general library concepts like semantic versioning and testing pyramids, see `meta-library-dev`. For Haskell fundamentals like type classes and monads, see `lang-haskell-dev`.

## This Skill Adds

- **Build tooling**: Cabal, Stack, package.yaml configuration
- **Type-driven API design**: Leveraging Haskell's type system for library interfaces
- **Module organization**: Best practices for exposing clean public APIs
- **Property-based testing**: QuickCheck patterns for library validation
- **Haddock documentation**: API documentation standards
- **Hackage publishing**: Package distribution and maintenance

## This Skill Does NOT Cover

- General library patterns - see `meta-library-dev`
- Core Haskell language features - see `lang-haskell-dev`
- Advanced type system features (GADTs, Type Families) - see `lang-haskell-advanced-dev`
- Web frameworks (Servant, Yesod) - see framework-specific skills
- Application development - see `lang-haskell-app-dev`

---

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| New library (Cabal) | `cabal init --lib <name>` |
| New library (Stack) | `stack new <name> simple-library` |
| Build | `cabal build` / `stack build` |
| Test | `cabal test` / `stack test` |
| Documentation | `cabal haddock` / `stack haddock` |
| REPL with library | `cabal repl` / `stack ghci` |
| Publish (dry run) | `cabal sdist` / `stack sdist` |
| Upload to Hackage | `cabal upload <tarball>` |
| Check package | `cabal check` |
| Format code | `fourmolu` or `ormolu` |

---

## Project Structure

### Standard Library Layout

```
my-library/
├── my-library.cabal          # Cabal package description
├── stack.yaml                # Stack configuration (optional)
├── package.yaml              # hpack configuration (Stack alternative)
├── LICENSE
├── README.md
├── CHANGELOG.md
├── src/
│   ├── MyLibrary.hs          # Main module (re-exports public API)
│   ├── MyLibrary/
│   │   ├── Types.hs          # Public types
│   │   ├── Core.hs           # Core functionality
│   │   └── Internal.hs       # Internal implementation
│   └── MyLibrary/Internal/   # Private modules
│       └── Helpers.hs
├── test/
│   ├── Spec.hs               # Test entry point
│   ├── MyLibrary/
│   │   ├── TypesSpec.hs      # Unit tests
│   │   └── CoreSpec.hs
│   └── Properties.hs         # QuickCheck properties
├── benchmark/
│   └── Main.hs               # Criterion benchmarks
└── examples/
    └── Basic.hs              # Usage examples

```

### Module Visibility

```haskell
-- src/MyLibrary.hs (main entry point)
module MyLibrary
  ( -- * Core Types
    Config(..)
  , Document
  , ParseResult

    -- * Construction
  , defaultConfig
  , mkDocument

    -- * Operations
  , parse
  , render
  , validate

    -- * Error Types
  , ParseError(..)
  , ValidationError(..)

    -- * Re-export specific modules for advanced use
  , module MyLibrary.Types
  ) where

import MyLibrary.Types
import MyLibrary.Core
import qualified MyLibrary.Internal as Internal

-- Re-export selected functions
parse = Internal.parseImpl
render = Internal.renderImpl
```

---

## Cabal Configuration

### Required Fields (.cabal file)

```cabal
cabal-version:      3.0
name:               my-library
version:            0.1.0.0
synopsis:           A brief one-line description
description:
    A longer description of what this library does.
    .
    Multiple paragraphs are separated by a single dot line.

homepage:           https://github.com/username/my-library
bug-reports:        https://github.com/username/my-library/issues
license:            BSD-3-Clause
license-file:       LICENSE
author:             Your Name
maintainer:         you@example.com
copyright:          2025 Your Name
category:           Data
build-type:         Simple
tested-with:        GHC == 9.4.8
                  , GHC == 9.6.3
                  , GHC == 9.8.1

extra-doc-files:
    CHANGELOG.md
    README.md

extra-source-files:
    examples/*.hs
```

### Library Stanza

```cabal
library
  exposed-modules:
      MyLibrary
      MyLibrary.Types
      MyLibrary.Core

  other-modules:
      MyLibrary.Internal
      MyLibrary.Internal.Helpers

  -- Modules included but not exposed
  reexported-modules:
      Data.Text as MyLibrary.Text

  hs-source-dirs:      src
  default-language:    Haskell2010
  default-extensions:
      OverloadedStrings
      DeriveGeneric
      LambdaCase

  ghc-options:
      -Wall
      -Wcompat
      -Widentities
      -Wincomplete-record-updates
      -Wincomplete-uni-patterns
      -Wmissing-home-modules
      -Wpartial-fields
      -Wredundant-constraints

  build-depends:
      base              >= 4.14 && < 5
    , text              >= 1.2  && < 2.2
    , containers        >= 0.6  && < 0.8
    , bytestring        >= 0.10 && < 0.13
```

### Test Suite Stanza

```cabal
test-suite my-library-test
  type:                exitcode-stdio-1.0
  hs-source-dirs:      test
  main-is:             Spec.hs
  other-modules:
      MyLibrary.TypesSpec
      MyLibrary.CoreSpec
      Properties

  default-language:    Haskell2010
  ghc-options:         -Wall -threaded -rtsopts -with-rtsopts=-N

  build-depends:
      base
    , my-library
    , hspec             >= 2.7  && < 3
    , QuickCheck        >= 2.14 && < 3
    , hspec-discover    >= 2.7  && < 3

  build-tool-depends:
      hspec-discover:hspec-discover
```

### Benchmark Stanza

```cabal
benchmark my-library-bench
  type:                exitcode-stdio-1.0
  hs-source-dirs:      benchmark
  main-is:             Main.hs
  default-language:    Haskell2010
  ghc-options:         -Wall -O2 -threaded -rtsopts -with-rtsopts=-N

  build-depends:
      base
    , my-library
    , criterion         >= 1.5 && < 2
```

---

## Stack Configuration

### stack.yaml

```yaml
resolver: lts-22.7  # GHC 9.6.3

packages:
  - .

extra-deps: []

# Recommended flags
flags: {}

# Build options
ghc-options:
  "$locals": -Wall -Werror=incomplete-patterns

# Testing options
test:
  arguments:
    additional-args:
      - --color
      - --format=progress
```

### package.yaml (hpack alternative to .cabal)

```yaml
name: my-library
version: 0.1.0.0
synopsis: A brief one-line description
description: |
  A longer description of what this library does.

  Multiple paragraphs are supported.

github: username/my-library
license: BSD-3-Clause
author: Your Name
maintainer: you@example.com
copyright: 2025 Your Name
category: Data

extra-source-files:
  - README.md
  - CHANGELOG.md

dependencies:
  - base >= 4.14 && < 5
  - text >= 1.2 && < 2.2
  - containers >= 0.6 && < 0.8

ghc-options:
  - -Wall
  - -Wcompat
  - -Widentities
  - -Wincomplete-record-updates

default-extensions:
  - OverloadedStrings
  - DeriveGeneric
  - LambdaCase

library:
  source-dirs: src
  exposed-modules:
    - MyLibrary
    - MyLibrary.Types
    - MyLibrary.Core

tests:
  my-library-test:
    main: Spec.hs
    source-dirs: test
    ghc-options:
      - -threaded
      - -rtsopts
      - -with-rtsopts=-N
    dependencies:
      - my-library
      - hspec
      - QuickCheck
    build-tools:
      - hspec-discover

benchmarks:
  my-library-bench:
    main: Main.hs
    source-dirs: benchmark
    ghc-options:
      - -O2
      - -threaded
      - -rtsopts
    dependencies:
      - my-library
      - criterion
```

---

## Type-Driven API Design

### Smart Constructors

```haskell
-- Hide constructor, export smart constructor
module MyLibrary.Types
  ( Email       -- Type exported without constructor
  , mkEmail     -- Smart constructor
  , emailText   -- Accessor
  ) where

import Data.Text (Text)
import qualified Data.Text as T

-- Opaque type
newtype Email = Email Text
  deriving (Show, Eq)

-- Smart constructor with validation
mkEmail :: Text -> Either String Email
mkEmail input
  | T.null input = Left "Email cannot be empty"
  | '@' `T.elem` input = Right (Email input)
  | otherwise = Left "Invalid email format"

-- Safe accessor
emailText :: Email -> Text
emailText (Email txt) = txt
```

### Phantom Types for Type Safety

```haskell
{-# LANGUAGE DataKinds #-}
{-# LANGUAGE KindSignatures #-}

-- State machine encoded in types
data State = Draft | Published

newtype Document (s :: State) = Document Text

-- Only drafts can be edited
editDocument :: Text -> Document 'Draft -> Document 'Draft
editDocument newText _ = Document newText

-- Only drafts can be published
publishDocument :: Document 'Draft -> Document 'Published
publishDocument (Document txt) = Document txt

-- Published documents can be rendered
renderDocument :: Document 'Published -> Html
renderDocument (Document txt) = toHtml txt

-- Type-safe workflow
workflow :: Html
workflow =
  renderDocument $
    publishDocument $
      editDocument "Updated content" initialDraft
```

### Builder Pattern with Phantom Types

```haskell
data Incomplete
data Complete

data ConfigBuilder (s :: Type) = ConfigBuilder
  { _timeout :: Maybe Int
  , _retries :: Maybe Int
  , _endpoint :: Maybe String
  }

-- Start with incomplete config
emptyConfig :: ConfigBuilder Incomplete
emptyConfig = ConfigBuilder Nothing Nothing Nothing

-- Builder functions return incomplete
setTimeout :: Int -> ConfigBuilder s -> ConfigBuilder Incomplete
setTimeout t cfg = cfg { _timeout = Just t }

setRetries :: Int -> ConfigBuilder s -> ConfigBuilder Incomplete
setRetries r cfg = cfg { _retries = Just r }

-- Only setEndpoint returns Complete
setEndpoint :: String -> ConfigBuilder s -> ConfigBuilder Complete
setEndpoint e cfg = cfg { _endpoint = Just e }

-- Can only build from Complete
build :: ConfigBuilder Complete -> Config
build (ConfigBuilder (Just t) (Just r) (Just e)) =
  Config t r e
build _ = error "Impossible: Complete builder guarantees all fields set"

-- Usage: Type system enforces all fields are set
config = build $ setEndpoint "https://api.example.com"
              $ setTimeout 30
              $ setRetries 3 emptyConfig
```

### Leveraging Type Classes for Polymorphism

```haskell
-- Generic serialization interface
class Serialize a where
  serialize :: a -> ByteString
  deserialize :: ByteString -> Either String a

-- Provide instances for your types
instance Serialize Document where
  serialize = encodeDocument
  deserialize = decodeDocument

-- Functions polymorphic over Serialize
saveToFile :: Serialize a => FilePath -> a -> IO ()
saveToFile path value = BS.writeFile path (serialize value)

loadFromFile :: Serialize a => FilePath -> IO (Either String a)
loadFromFile path = deserialize <$> BS.readFile path
```

---

## Module Organization Patterns

### Internal Modules

```haskell
-- MyLibrary/Internal.hs
-- This module is in other-modules, not exposed-modules
module MyLibrary.Internal where

-- Internal functions used across the library
-- but not part of public API
internalHelper :: Text -> Result
internalHelper = ...
```

### Hierarchical Re-exports

```haskell
-- MyLibrary.hs (main entry point)
module MyLibrary
  ( -- * Re-export everything from Types
    module MyLibrary.Types
    -- * Re-export selected functions from Core
  , parse
  , validate
  , render
  ) where

import MyLibrary.Types
import MyLibrary.Core (parse, validate, render)
```

### Qualified Re-exports

```haskell
-- For users who want namespaced access
import qualified MyLibrary as ML
import qualified MyLibrary.Advanced as ML.Advanced

document = ML.parse input
result = ML.Advanced.complexOperation document
```

---

## Property-Based Testing with QuickCheck

### Arbitrary Instances

```haskell
{-# LANGUAGE DeriveGeneric #-}

import Test.QuickCheck
import Test.QuickCheck.Arbitrary.Generic

data Document = Document
  { docTitle :: Text
  , docContent :: Text
  , docTags :: [Text]
  } deriving (Show, Eq, Generic)

-- Automatic Arbitrary instance
instance Arbitrary Document where
  arbitrary = genericArbitrary

-- Or custom generators
instance Arbitrary Document where
  arbitrary = Document
    <$> genTitle
    <*> genContent
    <*> listOf genTag
    where
      genTitle = T.pack <$> listOf1 (choose ('a', 'z'))
      genContent = T.pack <$> listOf (choose ('a', 'z'))
      genTag = elements ["haskell", "library", "testing"]

-- Constrained generators
genValidEmail :: Gen Email
genValidEmail = do
  user <- listOf1 (choose ('a', 'z'))
  domain <- elements ["example.com", "test.org"]
  return $ Email (T.pack $ user ++ "@" ++ domain)
```

### Properties

```haskell
-- test/Properties.hs
import Test.Hspec
import Test.QuickCheck
import MyLibrary

spec :: Spec
spec = describe "Document properties" $ do

  describe "parse . render = id" $
    it "roundtrips successfully" $
      property $ \doc ->
        parse (render doc) === Right doc

  describe "parse validates input" $
    it "rejects empty titles" $
      property $ \content tags ->
        let doc = Document "" content tags
        in parse (render doc) `shouldSatisfy` isLeft

  describe "tag operations are idempotent" $
    it "adding same tag twice = adding once" $
      property $ \doc tag ->
        addTag tag (addTag tag doc) === addTag tag doc

  describe "parsing is total (never throws)" $
    it "handles arbitrary input" $
      property $ \(input :: Text) ->
        case parse input of
          Left _ -> True
          Right _ -> True
```

### Conditional Properties

```haskell
prop_sortedListHead :: [Int] -> Property
prop_sortedListHead xs =
  not (null xs) ==>  -- Precondition
  head (sort xs) === minimum xs

-- Better: Use forAll with constrained generator
prop_sortedListHead' :: Property
prop_sortedListHead' =
  forAll (listOf1 arbitrary) $ \xs ->
    head (sort xs) === minimum xs
```

### Invariants

```haskell
-- Check invariants hold after operations
prop_balancedAfterInsert :: Key -> Value -> Tree -> Bool
prop_balancedAfterInsert k v tree =
  isBalanced (insert k v tree)

prop_sizeAfterInsert :: Key -> Value -> Tree -> Property
prop_sizeAfterInsert k v tree =
  k `notMember` tree ==>
  size (insert k v tree) === size tree + 1
```

---

## Haddock Documentation

### Module Documentation

```haskell
{-|
Module      : MyLibrary
Description : Brief description of module purpose
Copyright   : (c) Your Name, 2025
License     : BSD-3-Clause
Maintainer  : you@example.com
Stability   : experimental
Portability : POSIX

Longer description of what this module provides.

= Usage

Basic usage example:

>>> import MyLibrary
>>> let doc = mkDocument "Hello"
>>> render doc
"<document>Hello</document>"

= Advanced Usage

More complex patterns and use cases.
-}
module MyLibrary where
```

### Function Documentation

```haskell
-- | Parse a document from text.
--
-- This function validates the input and returns either
-- a parse error or a valid document.
--
-- ==== Examples
--
-- Basic usage:
--
-- >>> parse "title: Hello\ncontent: World"
-- Right (Document {docTitle = "Hello", docContent = "World"})
--
-- Invalid input:
--
-- >>> parse ""
-- Left "Empty input"
--
-- ==== Notes
--
-- * Input must be UTF-8 encoded
-- * Title is required
-- * Content may be empty
--
parse :: Text -> Either ParseError Document
parse = ...

-- | Render a document to text.
--
-- The output format is compatible with 'parse':
--
-- prop> parse (render doc) == Right doc
--
render :: Document -> Text
render = ...
```

### Documenting Types

```haskell
-- | Configuration for the parser.
--
-- Use 'defaultConfig' or the builder pattern to construct.
data Config = Config
  { configTimeout :: Int
    -- ^ Timeout in seconds (must be positive)
  , configStrict :: Bool
    -- ^ Enable strict parsing mode
  , configEncoding :: Encoding
    -- ^ Character encoding to use
  } deriving (Show, Eq)

-- | Default configuration.
--
-- Equivalent to:
--
-- @
-- Config
--   { configTimeout = 30
--   , configStrict = False
--   , configEncoding = UTF8
--   }
-- @
defaultConfig :: Config
defaultConfig = Config 30 False UTF8
```

### Sections and Organization

```haskell
module MyLibrary
  ( -- * Types
    Document(..)
  , ParseError(..)

    -- * Construction
  , mkDocument
  , defaultDocument

    -- * Operations
    -- ** Parsing
  , parse
  , parseStrict
    -- ** Rendering
  , render
  , renderPretty

    -- * Utilities
  , validate
  , normalize
  ) where
```

### Code Examples in Documentation

```haskell
-- | Batch process multiple documents.
--
-- >>> let docs = [mkDocument "A", mkDocument "B"]
-- >>> mapM_ (print . render) docs
-- "<document>A</document>"
-- "<document>B</document>"
--
-- __Warning:__ This loads all documents into memory.
-- For large batches, use 'streamProcess' instead.
processBatch :: [Document] -> IO ()
processBatch = ...
```

---

## Publishing to Hackage

### Pre-publish Checklist

- [ ] Version bumped in .cabal (follow PVP)
- [ ] CHANGELOG.md updated
- [ ] All tests pass: `cabal test --test-show-details=direct`
- [ ] Documentation builds: `cabal haddock`
- [ ] Package builds: `cabal build all`
- [ ] No warnings: `cabal build -Wall -Werror`
- [ ] `cabal check` passes with no errors
- [ ] README.md is current and accurate
- [ ] LICENSE file included
- [ ] Tested with multiple GHC versions
- [ ] Hackage account credentials configured

### Package Versioning Policy (PVP)

Haskell uses PVP (A.B.C.D):

| Change Type | Version Update | Example |
|-------------|----------------|---------|
| Breaking API change | A.B → (A+1).0 | 1.2.0.0 → 2.0.0.0 |
| New functionality (compatible) | A.B.C → A.(B+1).0 | 1.2.3.0 → 1.3.0.0 |
| Bug fix (no API change) | A.B.C.D → A.B.C.(D+1) | 1.2.3.0 → 1.2.3.1 |

```cabal
-- Before: version 0.1.0.0
-- After adding compatible function: version 0.2.0.0
-- After breaking change: version 1.0.0.0
```

### Version Bounds

```cabal
build-depends:
    base              >= 4.14 && < 5
    -- Allow major version 4.14 through 4.x, but not 5.x

  , text              >= 1.2  && < 1.3
    -- Allow 1.2.x versions only

  , containers        >= 0.6  && < 0.8
    -- Allow 0.6.x and 0.7.x
```

### Building Distribution Tarball

```bash
# Check package is ready
cabal check

# Build source distribution
cabal sdist

# Check the tarball builds
cabal upload --publish <dist-newstyle/sdist/my-library-0.1.0.0.tar.gz> --dry-run

# Extract and test the tarball
cd /tmp
tar xzf my-library-0.1.0.0.tar.gz
cd my-library-0.1.0.0
cabal build
cabal test
```

### Uploading to Hackage

```bash
# First-time setup: Create ~/.cabal/config with Hackage credentials
# Or use environment variable
export HACKAGE_USERNAME=yourusername
export HACKAGE_PASSWORD=yourpassword

# Upload as candidate (test on Hackage but not published)
cabal upload path/to/my-library-0.1.0.0.tar.gz

# Publish from candidate
cabal upload --publish path/to/my-library-0.1.0.0.tar.gz

# Check package page
open https://hackage.haskell.org/package/my-library
```

### Documentation Upload

```bash
# Build documentation
cabal haddock --haddock-for-hackage

# Upload to Hackage
cabal upload -d <dist-newstyle/.../my-library-0.1.0.0-docs.tar.gz>
```

### Deprecating Packages

```cabal
-- In .cabal file
x-deprecated: Please use better-library instead
```

---

## Testing Patterns

### Unit Tests with HSpec

```haskell
-- test/MyLibrary/CoreSpec.hs
module MyLibrary.CoreSpec (spec) where

import Test.Hspec
import MyLibrary

spec :: Spec
spec = describe "Core functionality" $ do

  describe "parse" $ do
    it "parses valid input" $ do
      parse "title: Hello" `shouldBe` Right expectedDoc

    it "rejects empty input" $ do
      parse "" `shouldSatisfy` isLeft

    it "handles unicode" $ do
      parse "title: こんにちは" `shouldSatisfy` isRight

  describe "render" $ do
    it "produces valid output" $ do
      let doc = mkDocument "Test"
      render doc `shouldContain` "Test"

    context "with empty document" $ do
      it "returns empty string" $ do
        render emptyDocument `shouldBe` ""
```

### Test Organization

```haskell
-- test/Spec.hs
{-# OPTIONS_GHC -F -pgmF hspec-discover #-}

-- hspec-discover automatically finds all *Spec.hs files
```

### Testing with Temporary Files

```haskell
import System.IO.Temp (withSystemTempFile)

spec = describe "File operations" $
  it "saves and loads documents" $
    withSystemTempFile "test.doc" $ \path handle -> do
      hClose handle
      saveDocument path doc
      loaded <- loadDocument path
      loaded `shouldBe` Right doc
```

---

## Common Dependencies

### Core Libraries

```cabal
build-depends:
    base              >= 4.14 && < 5
  , text              >= 1.2  && < 2.2
  , bytestring        >= 0.10 && < 0.13
  , containers        >= 0.6  && < 0.8
```

### Parsing

```cabal
  , attoparsec        >= 0.13 && < 0.15
  , megaparsec        >= 9.0  && < 10
  , parser-combinators >= 1.2 && < 2
```

### Error Handling

```cabal
  , exceptions        >= 0.10 && < 0.11
  , transformers      >= 0.5  && < 0.7
```

### Testing

```cabal
  , hspec             >= 2.7  && < 3
  , QuickCheck        >= 2.14 && < 3
  , hspec-discover    >= 2.7  && < 3
```

### JSON

```cabal
  , aeson             >= 2.0  && < 2.3
```

---

## Anti-Patterns

### 1. Exposing Too Much

```haskell
-- Bad: Exposes internal implementation
module MyLibrary (module X) where
import MyLibrary.Internal as X

-- Good: Selective exports
module MyLibrary
  ( Document
  , parse
  , render
  ) where
```

### 2. Partial Functions in Public API

```haskell
-- Bad: Can throw exception
head' :: [a] -> a
head' (x:_) = x

-- Good: Total function
headMaybe :: [a] -> Maybe a
headMaybe (x:_) = Just x
headMaybe [] = Nothing
```

### 3. Over-Constrained Version Bounds

```haskell
-- Bad: Too restrictive
build-depends: text == 1.2.4.0

-- Good: PVP-compatible range
build-depends: text >= 1.2 && < 1.3
```

### 4. Missing Upper Bounds

```haskell
-- Bad: No upper bound (will break on major updates)
build-depends: aeson >= 2.0

-- Good: PVP upper bound
build-depends: aeson >= 2.0 && < 2.3
```

---

## Troubleshooting

### Cabal Hell (Dependency Conflicts)

**Problem:** Cannot satisfy dependency requirements

```
Resolving dependencies...
Error: Could not resolve dependencies
```

**Fix:** Use cabal's new-style builds (default in modern Cabal):
```bash
# Clear cache and rebuild
cabal clean
rm -rf dist-newstyle
cabal build

# Or use Stack which uses curated snapshots
stack build
```

### Haddock Fails to Build

**Problem:** Haddock parse errors

**Fix:** Check for:
- Unbalanced delimiters in documentation comments
- Invalid Haddock syntax (`>>>` for examples, `@` for code)
- Missing closing brackets in sections

```bash
# Build with verbose output
cabal haddock --haddock-options="--verbose"
```

### Package Check Errors

**Problem:** `cabal check` reports warnings/errors

**Fix:** Address each error:
- Add missing fields (synopsis, description, license)
- Fix version bounds
- Include all necessary files in extra-source-files

### Tests Pass Locally but Fail in CI

**Problem:** Different GHC versions or dependencies

**Fix:**
- Test locally with multiple GHC versions using Stack
- Use matrix builds in CI
- Pin resolver versions in stack.yaml

```yaml
# .github/workflows/ci.yml
strategy:
  matrix:
    ghc: ['9.2.8', '9.4.8', '9.6.3']
```

---

## References

- `meta-library-dev` - Foundational library patterns
- `lang-haskell-dev` - Core Haskell fundamentals
- [Haskell Package Versioning Policy](https://pvp.haskell.org/)
- [Cabal User Guide](https://cabal.readthedocs.io/)
- [Stack User Guide](https://docs.haskellstack.org/)
- [Hackage](https://hackage.haskell.org/)
- [Haddock Documentation](https://haskell-haddock.readthedocs.io/)
- [QuickCheck Manual](https://hackage.haskell.org/package/QuickCheck)
