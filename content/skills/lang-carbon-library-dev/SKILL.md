---
name: lang-carbon-library-dev
description: Carbon language library development patterns including interoperability with C++, memory safety patterns, generic programming, build system integration, testing approaches, and documentation standards. Use when creating Carbon libraries, designing public APIs with safety and interoperability in mind, or porting C++ libraries to Carbon.
---

# Carbon Library Development

Patterns for developing libraries in the Carbon language, with emphasis on C++ interoperability, memory safety, and modern design patterns.

## Overview

**This skill covers:**
- Carbon language fundamentals for library authors
- Interoperability with C++ codebases
- Memory safety patterns and ownership
- Generic programming with Carbon's type system
- Build system integration (Bazel)
- Testing approaches and documentation standards
- API design for both Carbon and C++ consumers

**This skill does NOT cover:**
- General library patterns - see `meta-library-dev`
- Application development - see `lang-carbon-dev` (if exists)
- Deep C++ interop details - see `lang-cpp-library-dev`

---

## Quick Reference

| Task | Pattern/Command |
|------|-----------------|
| Create library | Define in BUILD file with `carbon_library()` |
| Import C++ | `import Cpp library "path/to/header.h"` |
| Export to C++ | Use `api` access modifier |
| Generic type | `fn GenericFunc[T:! Type](x: T) -> T` |
| Interface | `interface Comparable { ... }` |
| Memory safety | Use move semantics and ownership |
| Build | `bazel build //path/to:target` |
| Test | `bazel test //path/to:target_test` |

---

## Carbon Language Fundamentals

### Package and API Structure

```carbon
// my_library/types.carbon
package MyLibrary;

// Public API (visible to other packages)
api class PublicType {
  var value: i32;

  // Public constructor
  fn Create(v: i32) -> Self {
    return {.value = v};
  }

  // Public method
  fn GetValue[self: Self]() -> i32 {
    return self.value;
  }
}

// Internal type (package-private)
class InternalHelper {
  var data: String;
}

// Public function
api fn ProcessData(input: String) -> PublicType {
  var helper: InternalHelper = {.data = input};
  return PublicType.Create(helper.data.Length());
}
```

### Access Control

```carbon
// api - Visible outside the package (public API)
api class PublicClass { ... }

// private - Visible only in current file (default)
private class FilePrivateClass { ... }

// Default (no modifier) is private
class DefaultPrivateClass { ... }
```

---

## Memory Safety and Ownership

### Move Semantics

```carbon
// Move-only type
class UniqueResource {
  var handle: i64;

  // Destructor called when value goes out of scope
  destructor {
    ReleaseHandle(handle);
  }

  // Explicitly deleted copy constructor
  fn Copy[self: Self]() -> Self = delete;

  // Move constructor (transfer ownership)
  fn Move[self: Self*]() -> Self {
    var result: Self = {.handle = self->handle};
    self->handle = -1; // Invalidate source
    return result;
  }
}

// Usage
fn UseResource() {
  var resource: UniqueResource = AcquireResource();
  // resource is automatically destroyed here
}
```

### Reference Types and Borrowing

```carbon
// Immutable reference (borrow)
fn ReadData[data: String*]() -> i32 {
  return data->Length();
}

// Mutable reference
fn ModifyData[data: String*]() {
  data->Append(" modified");
}

// Pointer parameters for optional references
fn OptionalData[data: Optional(String*)]() {
  if (data) {
    Print(data.Value()->Length());
  }
}
```

### Safety Patterns

```carbon
// Use Option type for nullable values
api fn FindElement[T:! Type](vec: Vector(T), predicate: fn(T) -> Bool)
    -> Option(T) {
  for (item: T in vec) {
    if (predicate(item)) {
      return Option(T).Some(item);
    }
  }
  return Option(T).None();
}

// Result type for error handling
api fn ParseInteger(input: String) -> Result(i32, ParseError) {
  if (input.IsEmpty()) {
    return Result(i32, ParseError).Err(
      ParseError.EmptyInput()
    );
  }

  var value: i32 = ConvertToInt(input);
  return Result(i32, ParseError).Ok(value);
}
```

---

## Generic Programming

### Generic Functions

```carbon
// Simple generic function
api fn Swap[T:! Type](a: T*, b: T*) {
  var temp: T = a->Move();
  a = b->Move();
  b = temp.Move();
}

// Constrained generics with interfaces
interface Comparable {
  fn Compare[self: Self](other: Self) -> i32;
}

api fn Max[T:! Comparable](a: T, b: T) -> T {
  if (a.Compare(b) > 0) {
    return a;
  }
  return b;
}
```

### Generic Types

```carbon
// Generic container
api class Container[T:! Type] {
  var data: Vector(T);

  fn Create() -> Self {
    return {.data = Vector(T).Create()};
  }

  fn Add[self: Self*](item: T) {
    self->data.Push(item);
  }

  fn Get[self: Self*](index: i32) -> T* {
    return self->data.At(index);
  }

  fn Size[self: Self]() -> i32 {
    return self.data.Size();
  }
}

// Usage
var intContainer: Container(i32) = Container(i32).Create();
intContainer.Add(42);
```

### Interface-Based Generics

```carbon
// Define interface
interface Serializable {
  fn Serialize[self: Self]() -> String;
  fn Deserialize(data: String) -> Self;
}

// Implement for custom type
class MyData {
  var value: i32;
  var name: String;
}

impl MyData as Serializable {
  fn Serialize[self: Self]() -> String {
    return String.Format("{value: {0}, name: {1}}",
                         self.value, self.name);
  }

  fn Deserialize(data: String) -> Self {
    // Parse and construct
    return {.value = 0, .name = data};
  }
}

// Generic function using interface
api fn SaveToFile[T:! Serializable](object: T, path: String) {
  var data: String = object.Serialize();
  WriteFile(path, data);
}
```

---

## C++ Interoperability

### Importing C++ Libraries

```carbon
// Import C++ header
import Cpp library "vector";
import Cpp library "string";
import Cpp library "memory";

// Use C++ types
fn UseCppVector() {
  var vec: Cpp.std.vector(i32) = Cpp.std.vector(i32).new();
  vec.push_back(1);
  vec.push_back(2);
  vec.push_back(3);
}
```

### Wrapping C++ APIs

```carbon
// Wrap C++ API with Carbon-friendly interface
import Cpp library "legacy_api.h";

api class LegacyWrapper {
  private var cppHandle: Cpp.LegacyHandle*;

  fn Create(config: String) -> Self {
    var handle: Cpp.LegacyHandle* =
      Cpp.CreateLegacyHandle(config.ToCppString());
    return {.cppHandle = handle};
  }

  destructor {
    Cpp.DestroyLegacyHandle(cppHandle);
  }

  // Safe Carbon API
  fn ProcessData[self: Self*](input: String) -> Result(String, Error) {
    var cppResult: Cpp.std.string =
      Cpp.ProcessWithHandle(self->cppHandle, input.ToCppString());

    if (Cpp.HasError(self->cppHandle)) {
      return Result(String, Error).Err(Error.ProcessingFailed());
    }

    return Result(String, Error).Ok(
      String.FromCppString(cppResult)
    );
  }
}
```

### Exporting to C++

```carbon
// Carbon API that can be called from C++
api class CarbonLibrary {
  // Use simple types for C++ compatibility
  api fn ComputeHash(input: String) -> i64 {
    var hash: i64 = 0;
    for (ch: i8 in input) {
      hash = hash * 31 + ch;
    }
    return hash;
  }

  // Complex types require wrapping
  api fn ProcessVector(vec: Vector(i32)) -> i32 {
    var sum: i32 = 0;
    for (val: i32 in vec) {
      sum += val;
    }
    return sum;
  }
}
```

### Type Compatibility

```carbon
// Carbon to C++ type mapping
// i8, i16, i32, i64 -> int8_t, int16_t, int32_t, int64_t
// u8, u16, u32, u64 -> uint8_t, uint16_t, uint32_t, uint64_t
// f32, f64 -> float, double
// bool -> bool
// String -> std::string (with conversion)

// Conversion helpers
fn ToCppString(s: String) -> Cpp.std.string {
  return Cpp.std.string.new(s.Data(), s.Length());
}

fn FromCppString(cpp: Cpp.std.string) -> String {
  return String.FromBytes(cpp.data(), cpp.size());
}
```

---

## Build System Integration

### Bazel BUILD File

```python
# BUILD file for Carbon library
load("@rules_carbon//carbon:defs.bzl", "carbon_library", "carbon_test")

carbon_library(
    name = "my_library",
    srcs = [
        "types.carbon",
        "functions.carbon",
    ],
    hdrs = [
        "api.carbon",
    ],
    deps = [
        ":internal_lib",
        "@carbon_lang//common:string",
    ],
    visibility = ["//visibility:public"],
)

carbon_library(
    name = "internal_lib",
    srcs = ["internal.carbon"],
    visibility = ["//visibility:private"],
)

# With C++ interop
carbon_library(
    name = "cpp_wrapper",
    srcs = ["wrapper.carbon"],
    deps = [
        "@legacy_cpp_lib//:library",
    ],
    cpp_deps = True,
)
```

### Project Structure

```
my_carbon_library/
├── BUILD                  # Bazel build configuration
├── WORKSPACE             # Bazel workspace
├── README.md
├── LICENSE
├── api/                  # Public API
│   ├── BUILD
│   └── public_types.carbon
├── src/                  # Implementation
│   ├── BUILD
│   ├── impl.carbon
│   └── internal/
│       ├── BUILD
│       └── helpers.carbon
├── tests/                # Tests
│   ├── BUILD
│   └── api_test.carbon
└── examples/             # Example usage
    ├── BUILD
    └── basic_usage.carbon
```

---

## Testing

### Unit Tests

```carbon
// tests/my_library_test.carbon
package MyLibraryTest;

import MyLibrary;
import Testing;

@Test
fn TestPublicType() {
  var obj: MyLibrary.PublicType = MyLibrary.PublicType.Create(42);
  Testing.ExpectEq(obj.GetValue(), 42);
}

@Test
fn TestProcessData() {
  var result: MyLibrary.PublicType =
    MyLibrary.ProcessData("hello");
  Testing.ExpectEq(result.GetValue(), 5);
}

@Test
fn TestErrorHandling() {
  var result: Result(i32, ParseError) =
    MyLibrary.ParseInteger("");
  Testing.ExpectTrue(result.IsErr());
}
```

### Test BUILD Configuration

```python
carbon_test(
    name = "my_library_test",
    srcs = ["my_library_test.carbon"],
    deps = [
        "//my_library:my_library",
    ],
    size = "small",
)
```

### Property-Based Testing

```carbon
// Advanced testing patterns
@Test
fn TestRoundtrip() {
  var inputs: Vector(String) = GenerateTestStrings();

  for (input: String in inputs) {
    var encoded: String = Encode(input);
    var decoded: Result(String, Error) = Decode(encoded);

    Testing.ExpectTrue(decoded.IsOk());
    Testing.ExpectEq(decoded.Unwrap(), input);
  }
}
```

---

## Documentation

### Doc Comments

```carbon
/// Represents a configuration for the library.
///
/// # Example
/// ```
/// var config: Config = Config.Default();
/// config.SetTimeout(30);
/// ```
api class Config {
  private var timeout: i32;

  /// Creates a configuration with default values.
  ///
  /// Returns: A Config with timeout set to 10 seconds.
  fn Default() -> Self {
    return {.timeout = 10};
  }

  /// Sets the timeout value.
  ///
  /// Parameters:
  ///   - seconds: The timeout in seconds (must be positive)
  ///
  /// Note: Values greater than 300 will be capped at 300.
  fn SetTimeout[self: Self*](seconds: i32) {
    if (seconds > 300) {
      self->timeout = 300;
    } else if (seconds > 0) {
      self->timeout = seconds;
    }
  }
}
```

### Package Documentation

```carbon
/// # MyLibrary
///
/// A Carbon library for efficient data processing with C++ interoperability.
///
/// ## Features
///
/// - Type-safe generic containers
/// - Zero-cost C++ interop
/// - Memory-safe by default
/// - High-performance processing
///
/// ## Quick Start
///
/// ```carbon
/// import MyLibrary;
///
/// fn main() -> i32 {
///   var processor: MyLibrary.Processor = MyLibrary.Processor.Create();
///   var result: String = processor.Process("input data");
///   Print(result);
///   return 0;
/// }
/// ```
package MyLibrary;
```

---

## API Design Best Practices

### 1. Use Strong Types

```carbon
// Good: Type-safe ID
api class UserId {
  private var id: i64;

  fn Create(id: i64) -> Self {
    return {.id = id};
  }

  fn ToInt[self: Self]() -> i64 {
    return self.id;
  }
}

// Avoid: Primitive obsession
api fn GetUser(userId: i64) -> User; // Can confuse with other IDs
```

### 2. Prefer Immutability

```carbon
// Good: Immutable by default
api class ImmutableConfig {
  let timeout: i32;
  let retries: i32;

  fn WithTimeout[self: Self](newTimeout: i32) -> Self {
    return {.timeout = newTimeout, .retries = self.retries};
  }
}

// Mutable when needed
api class MutableBuffer {
  var data: Vector(u8);

  fn Append[self: Self*](bytes: Vector(u8)) {
    self->data.Extend(bytes);
  }
}
```

### 3. Clear Error Handling

```carbon
// Good: Explicit error types
api class FileError {
  choice {
    NotFound,
    PermissionDenied,
    IoError(String),
  }
}

api fn ReadFile(path: String) -> Result(String, FileError) {
  // Implementation
}

// Usage encourages error handling
var content: Result(String, FileError) = ReadFile("data.txt");
match (content) {
  case Ok(text: String) => {
    Process(text);
  }
  case Err(FileError.NotFound) => {
    Print("File not found");
  }
  case Err(error: FileError) => {
    Print("Error: {0}", error);
  }
}
```

### 4. Leverage Generics

```carbon
// Good: Generic and reusable
api fn Map[T:! Type, U:! Type](
    vec: Vector(T),
    transform: fn(T) -> U
) -> Vector(U) {
  var result: Vector(U) = Vector(U).Create();
  for (item: T in vec) {
    result.Push(transform(item));
  }
  return result;
}
```

---

## Performance Considerations

### Move Semantics

```carbon
// Efficient: Move instead of copy
api fn ProcessLargeData(data: LargeBuffer) -> LargeBuffer {
  var result: LargeBuffer = Transform(data.Move());
  return result.Move(); // Return by move
}
```

### Inline Functions

```carbon
// Hot path functions should be small and inline
@Inline
fn FastHash[self: String]() -> i64 {
  var hash: i64 = 0;
  for (ch: i8 in self) {
    hash = (hash << 5) - hash + ch;
  }
  return hash;
}
```

### Zero-Cost Abstractions

```carbon
// Iterator abstraction with no runtime cost
api class RangeIterator {
  var current: i32;
  var end: i32;

  @Inline
  fn Next[self: Self*]() -> Option(i32) {
    if (self->current < self->end) {
      var value: i32 = self->current;
      self->current += 1;
      return Option(i32).Some(value);
    }
    return Option(i32).None();
  }
}
```

---

## Migration from C++

### Gradual Migration Strategy

```carbon
// 1. Start by wrapping C++ APIs
import Cpp library "legacy.h";

api class CarbonFacade {
  private var cppImpl: Cpp.LegacyClass*;

  fn Create() -> Self {
    return {.cppImpl = Cpp.LegacyClass.new()};
  }

  fn Operation[self: Self*](input: String) -> String {
    return FromCppString(
      self->cppImpl->operation(ToCppString(input))
    );
  }
}

// 2. Gradually rewrite implementation in Carbon
api class CarbonNativeImpl {
  // Pure Carbon implementation
  fn Operation[self: Self*](input: String) -> String {
    // Carbon implementation
  }
}
```

### Compatibility Patterns

```carbon
// Maintain C++ compatibility during migration
api class HybridLibrary {
  choice {
    CppBackend(Cpp.LegacyImpl*),
    CarbonBackend(CarbonImpl),
  }

  fn Operation[self: Self*](input: String) -> String {
    match (self) {
      case CppBackend(impl: Cpp.LegacyImpl*) => {
        return FromCppString(impl->operation(ToCppString(input)));
      }
      case CarbonBackend(impl: CarbonImpl) => {
        return impl.Operation(input);
      }
    }
  }
}
```

---

## Common Patterns

### Builder Pattern

```carbon
api class ConfigBuilder {
  var timeout: Option(i32);
  var retries: Option(i32);
  var strictMode: bool;

  fn Create() -> Self {
    return {
      .timeout = Option(i32).None(),
      .retries = Option(i32).None(),
      .strictMode = false
    };
  }

  fn WithTimeout[self: Self](t: i32) -> Self {
    return {
      .timeout = Option(i32).Some(t),
      .retries = self.retries,
      .strictMode = self.strictMode
    };
  }

  fn Build[self: Self]() -> Config {
    return {
      .timeout = self.timeout.UnwrapOr(30),
      .retries = self.retries.UnwrapOr(3),
      .strictMode = self.strictMode
    };
  }
}
```

### Factory Pattern

```carbon
api interface Parser {
  fn Parse[self: Self*](input: String) -> Result(Document, ParseError);
}

api class ParserFactory {
  fn CreateParser(format: String) -> Option(Parser) {
    if (format == "json") {
      return Option(Parser).Some(JsonParser.Create());
    } else if (format == "xml") {
      return Option(Parser).Some(XmlParser.Create());
    }
    return Option(Parser).None();
  }
}
```

---

## Troubleshooting

### Ownership Errors

```carbon
// Problem: Using moved value
var data: String = "hello";
var moved: String = data.Move();
Print(data); // ERROR: data was moved

// Fix: Don't use after move, or use reference
var data: String = "hello";
var moved: String = data.Move();
Print(moved); // OK
```

### C++ Interop Issues

```carbon
// Problem: Memory management mismatch
import Cpp library "api.h";

fn LeakyFunction() {
  var cppPtr: Cpp.Object* = Cpp.CreateObject();
  // Forgot to delete - memory leak
}

// Fix: Use RAII wrapper
class CppObjectWrapper {
  var ptr: Cpp.Object*;

  destructor {
    Cpp.DeleteObject(ptr);
  }
}
```

### Generic Constraints

```carbon
// Problem: Missing constraint
fn Compare[T:! Type](a: T, b: T) -> bool {
  return a < b; // ERROR: T doesn't have < operator
}

// Fix: Add proper constraint
interface Ordered {
  fn Less[self: Self](other: Self) -> bool;
}

fn Compare[T:! Ordered](a: T, b: T) -> bool {
  return a.Less(b);
}
```

---

## References

- [Carbon Language Documentation](https://github.com/carbon-language/carbon-lang)
- [Carbon Language Spec](https://github.com/carbon-language/carbon-lang/tree/trunk/docs/design)
- C++ Interoperability Guide
- `meta-library-dev` - General library patterns
- `lang-cpp-library-dev` - C++ library development
