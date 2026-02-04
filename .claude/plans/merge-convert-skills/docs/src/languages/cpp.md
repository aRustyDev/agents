# C++

> Multi-paradigm systems programming language with zero-overhead abstractions and comprehensive standard library.

## Overview

C++ is a general-purpose programming language developed by Bjarne Stroustrup starting in 1979 as "C with Classes." It extends C with object-oriented features, generic programming through templates, and increasingly functional programming capabilities.

Modern C++ (C++11 onwards) has evolved significantly, adding features like move semantics, smart pointers, lambdas, constexpr, and concepts. The language emphasizes zero-overhead abstractions: you don't pay for what you don't use, and what you do use, you couldn't hand-code any better.

C++ dominates in game engines, high-frequency trading, embedded systems, browsers, and performance-critical applications where both high-level abstractions and low-level control are needed.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Systems | Low-level control, deterministic destruction |
| Secondary Family | OOP | Classes, inheritance, virtual functions |
| Subtype | multi-paradigm | OOP, generic, procedural, (limited) functional |

See: [Systems Family](../language-families/systems.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| C++98 | 1998 | Original ISO standard, STL |
| C++11 | 2011 | Move semantics, auto, lambdas, smart pointers |
| C++14 | 2014 | Generic lambdas, relaxed constexpr |
| C++17 | 2017 | Structured bindings, if constexpr, std::optional |
| C++20 | 2020 | Concepts, ranges, coroutines, modules |
| C++23 | 2023 | std::expected, deducing this, import std |

## Feature Profile

### Type System

- **Strength:** strong (static, but with C compatibility holes)
- **Inference:** auto (since C++11), template deduction
- **Generics:** templates (Turing-complete metaprogramming, concepts)
- **Nullability:** nullable (nullptr, std::optional for explicit)

### Memory Model

- **Management:** manual + RAII (deterministic destruction)
- **Mutability:** default-mutable (const for immutability)
- **Allocation:** flexible (stack, heap, custom allocators)
- **Smart pointers:** unique_ptr, shared_ptr, weak_ptr

### Control Flow

- **Structured:** if-else, for, while, switch, try-catch, range-for
- **Effects:** exceptions (can be disabled)
- **Async:** coroutines (C++20), std::async, threads

### Data Types

- **Primitives:** bool, char, int types, float, double
- **Composites:** classes, structs, unions, arrays, std::tuple
- **Collections:** vector, map, set, unordered_map, array
- **Abstraction:** classes, templates, namespaces, concepts

### Metaprogramming

- **Macros:** preprocessor (C-style)
- **Reflection:** limited (RTTI, type_traits)
- **Code generation:** templates (compile-time), constexpr/consteval

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | vcpkg, Conan | vcpkg gaining ground |
| Build System | CMake, Meson, Bazel | CMake dominant |
| LSP | clangd | Excellent |
| Formatter | clang-format | Standard |
| Linter | clang-tidy | Extensive checks |
| REPL | Cling | Clang-based |
| Test Framework | Google Test, Catch2 | Catch2 is modern |

## Syntax Patterns

```cpp
// Function definition
std::string greet(std::string_view name, int times = 1) {
    std::string result;
    for (int i = 0; i < times; ++i) {
        result += "Hello, " + std::string(name) + "! ";
    }
    return result;
}

// Generic function with concepts (C++20)
template<typename T>
T identity(T value) {
    return value;
}

template<std::integral T>
T increment(T value) {
    return value + 1;
}

// Async function (coroutine)
Task<Response> fetchData(std::string url) {
    auto response = co_await httpGet(url);
    if (response.status() != 200) {
        throw HttpError(response.status());
    }
    co_return response;
}

// Class definition
class User {
public:
    User(std::string id, std::string name)
        : id_(std::move(id)), name_(std::move(name)) {}

    const std::string& id() const { return id_; }
    const std::string& name() const { return name_; }
    const std::optional<std::string>& email() const { return email_; }

    void setEmail(std::string email) { email_ = std::move(email); }

private:
    std::string id_;
    std::string name_;
    std::optional<std::string> email_;
};

// Variant (sum type, C++17)
using Shape = std::variant<Circle, Rectangle>;

struct Circle { double radius; };
struct Rectangle { double width, height; };

double area(const Shape& shape) {
    return std::visit([](auto&& s) -> double {
        using T = std::decay_t<decltype(s)>;
        if constexpr (std::is_same_v<T, Circle>) {
            return std::numbers::pi * s.radius * s.radius;
        } else {
            return s.width * s.height;
        }
    }, shape);
}

// Error handling with std::expected (C++23)
std::expected<int, std::string> divide(int a, int b) {
    if (b == 0) {
        return std::unexpected("Division by zero");
    }
    return a / b;
}

// RAII resource management
class FileHandle {
public:
    explicit FileHandle(const char* path) : file_(fopen(path, "r")) {
        if (!file_) throw std::runtime_error("Failed to open file");
    }
    ~FileHandle() { if (file_) fclose(file_); }

    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;

    FileHandle(FileHandle&& other) noexcept : file_(other.file_) {
        other.file_ = nullptr;
    }

    FILE* get() { return file_; }

private:
    FILE* file_;
};

// Smart pointers
auto user = std::make_unique<User>("1", "Alice");
auto shared = std::make_shared<User>("2", "Bob");

// Lambda
auto add = [](int a, int b) { return a + b; };
auto multiplier = [factor = 2](int x) { return x * factor; };

// Range-based algorithms (C++20)
std::vector<int> numbers = {1, 2, 3, 4, 5};
auto result = numbers
    | std::views::filter([](int x) { return x % 2 == 0; })
    | std::views::transform([](int x) { return x * 2; });

// Structured bindings
auto [x, y, z] = std::make_tuple(1, 2.0, "three");
for (const auto& [key, value] : map) { /* ... */ }

// Concept definition (C++20)
template<typename T>
concept Printable = requires(T t) {
    { std::cout << t } -> std::same_as<std::ostream&>;
};

template<Printable T>
void print(const T& value) {
    std::cout << value << std::endl;
}
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| Complex syntax and feature interactions | high | Follow modern C++ guidelines (C++ Core Guidelines) |
| Long compile times (templates) | moderate | Precompiled headers, modules, explicit instantiation |
| ABI stability issues | moderate | Pimpl idiom, C ABI wrappers |
| Undefined behavior risks | moderate | Sanitizers, static analysis, avoid raw pointers |
| Exception safety complexity | moderate | RAII, noexcept specifications |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 1 | cpp-rust |
| As Target | 2 | c-cpp, java-cpp |

**Note:** Complex template metaprogramming may not translate directly to target languages.

## Idiomatic Patterns

### RAII → Destructors/Drop

```cpp
// C++: RAII with destructor
class Lock {
    Mutex& m_;
public:
    Lock(Mutex& m) : m_(m) { m_.lock(); }
    ~Lock() { m_.unlock(); }
};

// IR equivalent: Drop trait / context manager
// impl Drop for Lock { fn drop(&mut self) { self.m.unlock(); } }
```

### Templates → Generics

```cpp
// C++: template
template<typename T>
T max(T a, T b) { return a > b ? a : b; }

// IR equivalent: generic with trait bound
// fn max<T: Ord>(a: T, b: T) -> T
```

### std::optional → Option/Maybe

```cpp
// C++: std::optional
std::optional<int> find(int key);
if (auto val = find(key)) { use(*val); }

// IR equivalent: Option type
// fn find(key: i32) -> Option<i32>
```

### std::variant → Sum Types

```cpp
// C++: std::variant with std::visit
std::variant<int, std::string> value;
std::visit([](auto&& v) { /* ... */ }, value);

// IR equivalent: enum with pattern matching
// match value { Int(i) => ..., String(s) => ... }
```

## Related Languages

- **Influenced by:** C, Simula, ALGOL 68, Ada, ML
- **Influenced:** Java, C#, Rust, D, Carbon
- **Compiles to:** Native machine code
- **FFI compatible:** C (extern "C"), platform-specific C++ ABI

## Sources

- [C++ Reference](https://en.cppreference.com/w/cpp)
- [isocpp.org](https://isocpp.org/)
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/)
- [C++ Draft Standard](https://eel.is/c++draft/)

## See Also

- [Systems Family](../language-families/systems.md)
- [C](c.md) - Predecessor
- [Rust](rust.md) - Modern alternative
- [Java](java.md) - Managed alternative
