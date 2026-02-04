# C

> Low-level systems programming language providing direct hardware access and manual memory management.

## Overview

C is a general-purpose systems programming language developed by Dennis Ritchie at Bell Labs between 1969 and 1973. It was designed for system programming, particularly the Unix operating system, and remains fundamental to systems programming, embedded systems, and operating systems development.

C provides low-level access to memory, minimal runtime overhead, and a simple set of keywords that map efficiently to machine instructions. The language serves as the common denominator for foreign function interfaces (FFI) across most programming languages.

Despite its age, C continues to be essential for operating systems, embedded systems, drivers, and performance-critical applications where direct hardware control is required.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Systems | Direct hardware access |
| Secondary Family | — | Minimal abstraction |
| Subtype | procedural | Structured programming |

See: [Systems Family](../language-families/systems.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| K&R C | 1978 | Original, implicit int |
| ANSI C (C89) | 1989 | Function prototypes, const, void |
| C99 | 1999 | Inline, designated initializers, // comments, bool |
| C11 | 2011 | _Generic, _Static_assert, threading |
| C17 | 2018 | Bug fixes, deprecations |
| C23 | 2023 | typeof, constexpr, #embed, improved Unicode |

## Feature Profile

### Type System

- **Strength:** weak (implicit conversions, pointer arithmetic)
- **Inference:** none (explicit declarations required)
- **Generics:** none (void*, macros)
- **Nullability:** nullable (NULL pointer, no enforcement)

### Memory Model

- **Management:** manual (malloc/free)
- **Mutability:** default-mutable (const for immutability)
- **Allocation:** explicit (stack, heap, static)
- **Pointers:** unrestricted (pointer arithmetic allowed)

### Control Flow

- **Structured:** if-else, for, while, do-while, switch, goto
- **Effects:** return codes (no exceptions)
- **Async:** none (pthreads for threading)

### Data Types

- **Primitives:** char, short, int, long, float, double, _Bool
- **Composites:** struct, union, arrays
- **Collections:** arrays (fixed size)
- **Abstraction:** header files, opaque pointers

### Metaprogramming

- **Macros:** preprocessor (#define, #if)
- **Reflection:** none
- **Code generation:** preprocessor, external tools

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | none (system-level) | vcpkg, Conan (third-party) |
| Build System | Make, CMake, Meson | CMake dominant |
| LSP | clangd | Excellent |
| Formatter | clang-format | Standard |
| Linter | clang-tidy, cppcheck | Static analysis |
| REPL | none | Interactive debuggers |
| Test Framework | Unity, Check, CUnit | No built-in |

## Syntax Patterns

```c
// Function definition
char* greet(const char* name, int times) {
    size_t len = strlen("Hello, ") + strlen(name) + 2;
    char* result = malloc(len * times + 1);
    result[0] = '\0';
    for (int i = 0; i < times; i++) {
        strcat(result, "Hello, ");
        strcat(result, name);
        strcat(result, "! ");
    }
    return result;
}

// Generic-like pattern with void*
void swap(void* a, void* b, size_t size) {
    char temp[size];
    memcpy(temp, a, size);
    memcpy(a, b, size);
    memcpy(b, temp, size);
}

// Struct definition
typedef struct {
    char* id;
    char* name;
    char* email;  // NULL if not set
} User;

// Union (tagged)
typedef enum { CIRCLE, RECTANGLE } ShapeType;

typedef struct {
    ShapeType type;
    union {
        struct { double radius; } circle;
        struct { double width, height; } rectangle;
    };
} Shape;

// Pattern-like with switch
double area(const Shape* shape) {
    switch (shape->type) {
        case CIRCLE:
            return 3.14159 * shape->circle.radius * shape->circle.radius;
        case RECTANGLE:
            return shape->rectangle.width * shape->rectangle.height;
        default:
            return 0;
    }
}

// Error handling with return codes
typedef enum { OK = 0, ERR_DIVZERO = 1 } DivResult;

DivResult divide(int a, int b, int* result) {
    if (b == 0) {
        return ERR_DIVZERO;
    }
    *result = a / b;
    return OK;
}

// Resource management pattern
FILE* open_file(const char* path) {
    FILE* f = fopen(path, "r");
    if (!f) {
        perror("Failed to open file");
        return NULL;
    }
    return f;
}

void process_file(const char* path) {
    FILE* f = open_file(path);
    if (!f) return;

    // Process file...

    fclose(f);  // Manual cleanup
}

// Macro for generic-like behavior
#define MAX(a, b) ((a) > (b) ? (a) : (b))

// Function pointer
typedef int (*Comparator)(const void*, const void*);

void sort(void* arr, size_t n, size_t size, Comparator cmp) {
    qsort(arr, n, size, cmp);
}

// Opaque pointer pattern (information hiding)
// header.h
typedef struct Context Context;
Context* context_create(void);
void context_destroy(Context* ctx);
int context_process(Context* ctx, const char* data);

// Memory allocation
User* create_user(const char* id, const char* name) {
    User* user = malloc(sizeof(User));
    if (!user) return NULL;

    user->id = strdup(id);
    user->name = strdup(name);
    user->email = NULL;

    if (!user->id || !user->name) {
        free(user->id);
        free(user->name);
        free(user);
        return NULL;
    }

    return user;
}

void free_user(User* user) {
    if (user) {
        free(user->id);
        free(user->name);
        free(user->email);
        free(user);
    }
}
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| No memory safety | critical | Static analyzers, sanitizers, careful review |
| No bounds checking | critical | Manual checks, secure functions |
| NULL pointer risks | high | Defensive programming, static analysis |
| No namespaces | moderate | Prefix conventions (lib_function) |
| No generics | moderate | void*, macros, code generation |
| Manual memory management | moderate | RAII-like patterns, arena allocators |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 2 | c-cpp, c-rust |
| As Target | 1 | java-c |

**Note:** FFI baseline - most languages interface with C. Conversions focus on safety improvements.

## Idiomatic Patterns

### Opaque Pointers → Encapsulation

```c
// C: opaque pointer
typedef struct Impl Impl;
Impl* impl_new(void);
void impl_free(Impl* impl);

// IR equivalent: private struct/class
// class Impl { private fields... }
```

### Error Codes → Result Types

```c
// C: return code with output parameter
int parse(const char* s, int* out);

// IR equivalent: Result type
// fn parse(s: &str) -> Result<int, Error>
```

### Preprocessor → Generics/Const

```c
// C: macro constant
#define MAX_SIZE 1024

// IR equivalent: const
// const MAX_SIZE: usize = 1024;

// C: type-generic macro
#define ABS(x) ((x) < 0 ? -(x) : (x))

// IR equivalent: generic function
// fn abs<T: Num>(x: T) -> T
```

## Related Languages

- **Influenced by:** B, BCPL, ALGOL
- **Influenced:** C++, Java, C#, Rust, Go, virtually all modern languages
- **Compiles to:** Native machine code
- **FFI compatible:** Universal (de facto standard ABI)

## Sources

- [C17 Standard (Draft)](https://www.open-std.org/jtc1/sc22/wg14/)
- [cppreference C](https://en.cppreference.com/w/c)
- [The C Programming Language (K&R)](https://en.wikipedia.org/wiki/The_C_Programming_Language)
- [SEI CERT C Coding Standard](https://wiki.sei.cmu.edu/confluence/display/c)

## See Also

- [Systems Family](../language-families/systems.md)
- [C++](cpp.md) - Direct successor
- [Rust](rust.md) - Safe systems alternative
- [Go](golang.md) - Simplified systems language
