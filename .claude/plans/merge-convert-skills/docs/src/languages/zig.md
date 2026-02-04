# Zig

> Systems programming language emphasizing explicit behavior, no hidden control flow, and C interoperability.

## Overview

Zig is a systems programming language created by Andrew Kelley, first released in 2016. It aims to be a modern replacement for C, addressing many of its footguns while maintaining the ability to interface with C code and not hiding what the machine is really doing.

Zig emphasizes explicit behavior: there are no hidden memory allocations, no hidden control flow (no exceptions, no operator overloading), and the language itself has no runtime. This makes Zig suitable for high-performance systems programming, embedded development, and replacing C in existing codebases.

The language's compile-time execution (comptime) provides powerful metaprogramming without macros, and its built-in cross-compilation makes targeting multiple platforms straightforward.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Systems | No hidden control flow, manual memory |
| Secondary Family | — | Minimal abstraction |
| Subtype | explicit | No hidden costs |

See: [Systems Family](../language-families/systems.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 0.6.0 | 2020-04 | Async/await, stage2 compiler |
| 0.9.0 | 2021-12 | Self-hosted compiler improvements |
| 0.10.0 | 2022-02 | Package manager |
| 0.11.0 | 2023-08 | Build system improvements |

**Note:** Zig has not reached 1.0 yet. API may change.

## Feature Profile

### Type System

- **Strength:** strong (static, strict)
- **Inference:** limited (types in expressions, not function signatures)
- **Generics:** comptime (compile-time duck typing)
- **Nullability:** explicit (optional types with `?T`)

### Memory Model

- **Management:** manual (allocators as first-class)
- **Mutability:** default-immutable (const), explicit mutability (var)
- **Allocation:** explicit (allocators passed to functions)
- **Pointers:** controlled (no null by default, explicit null with optionals)

### Control Flow

- **Structured:** if-else, for, while, switch
- **Effects:** error unions (`!T`), no exceptions
- **Async:** stackless coroutines (not in current stable)

### Data Types

- **Primitives:** i8-i128, u8-u128, f16, f32, f64, f128, bool, void, noreturn
- **Composites:** struct, enum, union, array, slice
- **Collections:** arrays, slices (standard library for dynamic)
- **Abstraction:** comptime functions, opaque types

### Metaprogramming

- **Macros:** none (comptime replaces)
- **Reflection:** comptime (@typeInfo, @typeName)
- **Code generation:** comptime execution

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | zig (built-in) | URL-based |
| Build System | zig build (built-in) | Zig-based build scripts |
| LSP | zls | Community, good support |
| Formatter | zig fmt (built-in) | Built-in |
| Linter | none (compiler is strict) | — |
| REPL | none | — |
| Test Framework | built-in | `test` blocks |

## Syntax Patterns

```zig
const std = @import("std");

// Function definition
fn greet(name: []const u8, times: usize) []const u8 {
    var result: []u8 = undefined;
    // In practice, would use allocator
    return result;
}

// Generic function (comptime)
fn identity(comptime T: type, value: T) T {
    return value;
}

fn max(comptime T: type, a: T, b: T) T {
    return if (a > b) a else b;
}

// Struct definition
const User = struct {
    id: []const u8,
    name: []const u8,
    email: ?[]const u8 = null,

    pub fn init(id: []const u8, name: []const u8) User {
        return .{ .id = id, .name = name };
    }

    pub fn display(self: User) void {
        std.debug.print("User({s})\n", .{self.name});
    }
};

// Tagged union (ADT)
const Shape = union(enum) {
    circle: struct { radius: f64 },
    rectangle: struct { width: f64, height: f64 },

    pub fn area(self: Shape) f64 {
        return switch (self) {
            .circle => |c| std.math.pi * c.radius * c.radius,
            .rectangle => |r| r.width * r.height,
        };
    }
};

// Error handling with error union
const DivError = error{DivisionByZero};

fn divide(a: i64, b: i64) DivError!i64 {
    if (b == 0) {
        return error.DivisionByZero;
    }
    return @divTrunc(a, b);
}

// Using error union
pub fn main() !void {
    const result = divide(10, 2) catch |err| {
        std.debug.print("Error: {}\n", .{err});
        return err;
    };
    std.debug.print("Result: {}\n", .{result});
}

// Error propagation with try
fn process() !void {
    const value = try divide(10, 2);
    std.debug.print("Value: {}\n", .{value});
}

// Optional handling
fn getEmail(user: User) []const u8 {
    return user.email orelse "no-email@example.com";
}

fn processEmail(user: User) void {
    if (user.email) |email| {
        std.debug.print("Email: {s}\n", .{email});
    } else {
        std.debug.print("No email\n", .{});
    }
}

// Comptime (compile-time execution)
fn fibonacci(n: u64) u64 {
    if (n < 2) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

const fib_10 = comptime fibonacci(10);  // Computed at compile time

// Comptime type generation
fn Matrix(comptime T: type, comptime rows: usize, comptime cols: usize) type {
    return struct {
        data: [rows][cols]T,

        pub fn init() @This() {
            return .{ .data = std.mem.zeroes([rows][cols]T) };
        }
    };
}

const Mat3x3 = Matrix(f32, 3, 3);

// Allocators
pub fn createUsers(allocator: std.mem.Allocator, count: usize) ![]User {
    return try allocator.alloc(User, count);
}

// defer for cleanup
fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    const file = try std.fs.cwd().openFile(path, .{});
    defer file.close();

    return try file.readToEndAlloc(allocator, std.math.maxInt(usize));
}

// Slices
fn sum(numbers: []const i32) i32 {
    var total: i32 = 0;
    for (numbers) |n| {
        total += n;
    }
    return total;
}

// Packed structs for binary data
const Header = packed struct {
    version: u8,
    flags: u8,
    length: u16,
};

// C interoperability
const c = @cImport({
    @cInclude("stdio.h");
});

pub fn printHello() void {
    _ = c.printf("Hello from C!\n");
}

// Test
test "divide" {
    try std.testing.expectEqual(@as(i64, 5), try divide(10, 2));
    try std.testing.expectError(error.DivisionByZero, divide(10, 0));
}

// Inline assembly
fn rdtsc() u64 {
    var low: u32 = undefined;
    var high: u32 = undefined;
    asm volatile ("rdtsc"
        : "={eax}" (low),
          "={edx}" (high)
    );
    return (@as(u64, high) << 32) | low;
}
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| Pre-1.0, API changes | high | Track releases, pin versions |
| Smaller ecosystem | moderate | Use C libraries, build own |
| No runtime polymorphism | minor | Use tagged unions, comptime |
| Manual memory management | moderate | Use arena allocators, defer |
| Learning curve | moderate | Good documentation, small language |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 0 | — |
| As Target | 0 | — |

**Note:** Not in current convert-* skills. Natural target for C code modernization.

## Idiomatic Patterns

### Error Unions → Result Types

```zig
// Zig: error union
fn parse(input: []const u8) ParseError!Value {
    if (invalid) return error.InvalidInput;
    return value;
}

// IR equivalent: Result type
// fn parse(input: &str) -> Result<Value, ParseError>
```

### Comptime → Generics/Const

```zig
// Zig: comptime generic
fn List(comptime T: type) type {
    return struct { items: []T };
}

// IR equivalent: generic type
// struct List<T> { items: Vec<T> }
```

### Optionals → Maybe/Option

```zig
// Zig: optional
const email: ?[]const u8 = null;
const display = email orelse "default";

// IR equivalent: Option type
// let display = email.unwrap_or("default")
```

### Tagged Union → ADT

```zig
// Zig: tagged union
const Shape = union(enum) { circle: f64, rectangle: struct { w: f64, h: f64 } };

// IR equivalent: enum ADT
// enum Shape { Circle(f64), Rectangle { w: f64, h: f64 } }
```

## Related Languages

- **Influenced by:** C, C++, Rust, D
- **Influenced:** (New language, influence TBD)
- **Compiles to:** Native (LLVM), C (bootstrapping)
- **FFI compatible:** C (native, seamless)

## Sources

- [Zig Language Reference](https://ziglang.org/documentation/master/)
- [Zig Standard Library](https://ziglang.org/documentation/master/std/)
- [Zig Guide](https://zig.guide/)
- [Zig Learn](https://ziglearn.org/)

## See Also

- [Systems Family](../language-families/systems.md)
- [C](c.md) - Target for modernization
- [Rust](rust.md) - Alternative systems language
- [Go](golang.md) - Simplicity comparison
