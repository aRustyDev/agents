---
name: lang-cpp-dev
description: Foundational C++ patterns covering core syntax, classes, templates, RAII, move semantics, and modern C++ features (C++11/14/17/20). Use when writing C++ code, understanding the type system, memory management, or needing guidance on which specialized C++ skill to use. This is the entry point for C++ development.
---

# C++ Fundamentals

Foundational C++ patterns and core language features. This skill serves as both a reference for common patterns and an index to specialized C++ skills.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      C++ Skill Hierarchy                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌───────────────────┐                        │
│                    │   lang-cpp-dev    │ ◄── You are here       │
│                    │   (foundation)    │                        │
│                    └─────────┬─────────┘                        │
│                              │                                  │
│     ┌────────────┬───────────┼───────────┬────────────┐        │
│     │            │           │           │            │        │
│     ▼            ▼           ▼           ▼            ▼        │
│ ┌────────┐ ┌──────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐   │
│ │patterns│ │  cmake   │ │library │ │ memory  │ │profiling │   │
│ │  -dev  │ │   -dev   │ │  -dev  │ │  -eng   │ │   -eng   │   │
│ └────────┘ └──────────┘ └────────┘ └─────────┘ └──────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Core syntax (classes, structs, enums, namespaces)
- Type system and templates
- RAII and smart pointers
- Move semantics and perfect forwarding
- STL containers and algorithms
- Modern C++ features (C++11/14/17/20)
- Common idioms and patterns

**This skill does NOT cover (see specialized skills):**
- Design patterns and best practices → `lang-cpp-patterns-dev`
- CMake and build configuration → `lang-cpp-cmake-dev`
- Library/package development → `lang-cpp-library-dev`
- Advanced memory management → `lang-cpp-memory-eng`
- Profiling and optimization → `lang-cpp-profiling-eng`

---

## Quick Reference

| Task | Pattern |
|------|---------|
| Create class | `class Name { public: ... };` |
| Constructor | `Name() : member(value) {}` |
| Template function | `template<typename T> T func(T x)` |
| Template class | `template<typename T> class Container` |
| Smart pointer | `std::unique_ptr<T>`, `std::shared_ptr<T>` |
| Lambda | `[capture](params) { body }` |
| Range-based for | `for (auto& item : container)` |
| Move semantics | `std::move(value)` |
| Perfect forward | `std::forward<T>(arg)` |
| Concepts (C++20) | `template<typename T> concept Name = ...` |

---

## Skill Routing

Use this table to find the right specialized skill:

| When you need to... | Use this skill |
|---------------------|----------------|
| Implement design patterns (RAII, factory, singleton) | `lang-cpp-patterns-dev` |
| Configure CMake, manage dependencies | `lang-cpp-cmake-dev` |
| Create libraries, package for distribution | `lang-cpp-library-dev` |
| Optimize memory usage, custom allocators | `lang-cpp-memory-eng` |
| Profile performance, find bottlenecks | `lang-cpp-profiling-eng` |

---

## Core Types and Classes

### Classes and Structs

```cpp
// Class with private members by default
class User {
private:
    std::string name;
    int age;

public:
    // Constructor
    User(std::string n, int a) : name(std::move(n)), age(a) {}

    // Getter
    std::string getName() const { return name; }

    // Setter
    void setAge(int a) { age = a; }

    // Member function
    void greet() const {
        std::cout << "Hello, I'm " << name << "\n";
    }
};

// Struct with public members by default
struct Point {
    double x;
    double y;

    // Can have methods too
    double distance() const {
        return std::sqrt(x * x + y * y);
    }
};

// Creating instances
User user("Alice", 30);
Point p{3.0, 4.0};  // Aggregate initialization
```

### Constructors and Destructors

```cpp
class Resource {
private:
    int* data;
    size_t size;

public:
    // Default constructor
    Resource() : data(nullptr), size(0) {}

    // Parameterized constructor
    Resource(size_t n) : data(new int[n]), size(n) {}

    // Copy constructor
    Resource(const Resource& other)
        : data(new int[other.size]), size(other.size) {
        std::copy(other.data, other.data + size, data);
    }

    // Move constructor
    Resource(Resource&& other) noexcept
        : data(other.data), size(other.size) {
        other.data = nullptr;
        other.size = 0;
    }

    // Copy assignment
    Resource& operator=(const Resource& other) {
        if (this != &other) {
            delete[] data;
            size = other.size;
            data = new int[size];
            std::copy(other.data, other.data + size, data);
        }
        return *this;
    }

    // Move assignment
    Resource& operator=(Resource&& other) noexcept {
        if (this != &other) {
            delete[] data;
            data = other.data;
            size = other.size;
            other.data = nullptr;
            other.size = 0;
        }
        return *this;
    }

    // Destructor
    ~Resource() {
        delete[] data;
    }
};
```

### Rule of Five

```cpp
// If you define any of these, consider defining all:
// 1. Destructor
// 2. Copy constructor
// 3. Copy assignment operator
// 4. Move constructor
// 5. Move assignment operator

// Or explicitly delete them:
class NonCopyable {
public:
    NonCopyable() = default;
    NonCopyable(const NonCopyable&) = delete;
    NonCopyable& operator=(const NonCopyable&) = delete;
    NonCopyable(NonCopyable&&) = default;
    NonCopyable& operator=(NonCopyable&&) = default;
};
```

---

## RAII and Smart Pointers

### RAII Pattern

```cpp
// Resource Acquisition Is Initialization
class FileHandle {
private:
    FILE* file;

public:
    FileHandle(const char* filename, const char* mode)
        : file(fopen(filename, mode)) {
        if (!file) {
            throw std::runtime_error("Failed to open file");
        }
    }

    ~FileHandle() {
        if (file) {
            fclose(file);
        }
    }

    // Delete copy, allow move
    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
    FileHandle(FileHandle&& other) noexcept : file(other.file) {
        other.file = nullptr;
    }

    FILE* get() { return file; }
};

// Usage - automatic cleanup
void processFile(const char* filename) {
    FileHandle file(filename, "r");
    // Use file.get()
    // Automatically closed when function exits
}
```

### Smart Pointers

```cpp
#include <memory>

// unique_ptr - Single ownership
std::unique_ptr<User> createUser() {
    return std::make_unique<User>("Alice", 30);
}

auto user = createUser();
// auto user2 = user;  // Error: cannot copy
auto user2 = std::move(user);  // OK: transfer ownership
// user is now nullptr

// shared_ptr - Shared ownership with reference counting
std::shared_ptr<User> shared1 = std::make_shared<User>("Bob", 25);
std::shared_ptr<User> shared2 = shared1;  // OK: both own the object
// Object deleted when last shared_ptr is destroyed

// weak_ptr - Non-owning reference (breaks circular references)
std::weak_ptr<User> weak = shared1;
if (auto locked = weak.lock()) {
    // Use locked as shared_ptr
    locked->greet();
}

// Custom deleters
auto deleter = [](User* p) {
    std::cout << "Custom delete\n";
    delete p;
};
std::unique_ptr<User, decltype(deleter)> custom(new User("Eve", 28), deleter);
```

### RAII for Locks

```cpp
#include <mutex>

std::mutex mtx;
std::vector<int> shared_data;

void addData(int value) {
    std::lock_guard<std::mutex> lock(mtx);  // RAII lock
    shared_data.push_back(value);
    // Automatically unlocked when lock goes out of scope
}

// For more control
void complexOperation() {
    std::unique_lock<std::mutex> lock(mtx);
    // Can unlock/lock manually
    lock.unlock();
    // Do non-critical work
    lock.lock();
    // Critical section
}
```

---

## Templates

### Function Templates

```cpp
// Basic template
template<typename T>
T maximum(T a, T b) {
    return a > b ? a : b;
}

// Multiple type parameters
template<typename T, typename U>
auto add(T a, U b) -> decltype(a + b) {
    return a + b;
}

// Template specialization
template<typename T>
void print(T value) {
    std::cout << value << "\n";
}

// Specialization for const char*
template<>
void print<const char*>(const char* value) {
    std::cout << "String: " << value << "\n";
}

// With constraints (C++20 concepts)
template<typename T>
concept Numeric = std::is_arithmetic_v<T>;

template<Numeric T>
T multiply(T a, T b) {
    return a * b;
}
```

### Class Templates

```cpp
// Basic class template
template<typename T>
class Container {
private:
    T* data;
    size_t size;

public:
    Container(size_t n) : data(new T[n]), size(n) {}
    ~Container() { delete[] data; }

    T& operator[](size_t i) { return data[i]; }
    const T& operator[](size_t i) const { return data[i]; }

    size_t getSize() const { return size; }
};

// Usage
Container<int> intContainer(10);
Container<std::string> strContainer(5);

// Template with multiple parameters
template<typename T, size_t N>
class FixedArray {
private:
    T data[N];

public:
    constexpr size_t size() const { return N; }
    T& operator[](size_t i) { return data[i]; }
};

FixedArray<int, 10> arr;
```

### Variadic Templates

```cpp
// Base case
void print() {
    std::cout << "\n";
}

// Recursive case
template<typename T, typename... Args>
void print(T first, Args... args) {
    std::cout << first << " ";
    print(args...);  // Recursive call
}

// Usage
print(1, 2.5, "hello", 'c');  // Prints: 1 2.5 hello c

// Fold expressions (C++17)
template<typename... Args>
auto sum(Args... args) {
    return (args + ...);  // Fold over +
}

auto total = sum(1, 2, 3, 4, 5);  // 15
```

---

## Move Semantics and Perfect Forwarding

### Move Semantics

```cpp
#include <vector>
#include <string>

// Lvalue vs Rvalue
std::string str = "hello";      // str is lvalue
std::string copy = str;         // Copy
std::string moved = std::move(str);  // Move (str is now empty)

// Move with containers
std::vector<int> vec1 = {1, 2, 3, 4, 5};
std::vector<int> vec2 = std::move(vec1);  // vec1 is now empty, vec2 has data

// Implementing move
class Buffer {
private:
    char* data;
    size_t size;

public:
    // Move constructor
    Buffer(Buffer&& other) noexcept
        : data(other.data), size(other.size) {
        other.data = nullptr;
        other.size = 0;
    }

    // Move assignment
    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            delete[] data;
            data = other.data;
            size = other.size;
            other.data = nullptr;
            other.size = 0;
        }
        return *this;
    }
};
```

### Perfect Forwarding

```cpp
// Forward arguments preserving their value category
template<typename T, typename... Args>
std::unique_ptr<T> make_unique(Args&&... args) {
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
}

// Universal references (T&&) in templates
template<typename T>
void wrapper(T&& arg) {
    // arg is universal reference
    // Forwards as lvalue or rvalue depending on what was passed
    process(std::forward<T>(arg));
}

int x = 5;
wrapper(x);           // T deduced as int&, forwards as lvalue
wrapper(10);          // T deduced as int, forwards as rvalue
wrapper(std::move(x)); // Forwards as rvalue
```

### Return Value Optimization

```cpp
// RVO (Return Value Optimization)
std::vector<int> createVector() {
    std::vector<int> result;
    result.push_back(1);
    result.push_back(2);
    return result;  // No copy/move, constructed in place
}

// NRVO (Named Return Value Optimization)
std::string buildString(bool flag) {
    std::string result;
    if (flag) {
        result = "yes";
    } else {
        result = "no";
    }
    return result;  // Usually optimized
}

// Don't use std::move on return - prevents RVO
std::vector<int> bad() {
    std::vector<int> result;
    return std::move(result);  // BAD: prevents RVO
}
```

---

## STL Containers

### Sequence Containers

```cpp
#include <vector>
#include <deque>
#include <list>
#include <array>

// vector - Dynamic array
std::vector<int> vec = {1, 2, 3};
vec.push_back(4);
vec.emplace_back(5);  // Construct in place
vec.pop_back();
vec.resize(10);
vec.reserve(100);  // Pre-allocate capacity

// array - Fixed-size array (C++11)
std::array<int, 5> arr = {1, 2, 3, 4, 5};
arr.fill(0);

// deque - Double-ended queue
std::deque<int> deq = {1, 2, 3};
deq.push_front(0);
deq.push_back(4);

// list - Doubly-linked list
std::list<int> lst = {1, 2, 3};
lst.push_front(0);
lst.push_back(4);
lst.remove(2);  // Remove all elements with value 2
```

### Associative Containers

```cpp
#include <set>
#include <map>
#include <unordered_set>
#include <unordered_map>

// set - Ordered unique elements
std::set<int> s = {3, 1, 2};  // Stored as {1, 2, 3}
s.insert(4);
s.erase(2);
bool has = s.count(3) > 0;

// map - Key-value pairs, ordered by key
std::map<std::string, int> ages;
ages["Alice"] = 30;
ages["Bob"] = 25;
ages.insert({"Charlie", 35});

// Check if key exists
if (ages.count("Alice")) {
    std::cout << ages["Alice"] << "\n";
}

// Iterate
for (const auto& [name, age] : ages) {
    std::cout << name << ": " << age << "\n";
}

// unordered_set - Hash set
std::unordered_set<std::string> names = {"Alice", "Bob"};
names.insert("Charlie");

// unordered_map - Hash map (faster lookup)
std::unordered_map<std::string, int> scores;
scores["player1"] = 100;
```

### Container Adaptors

```cpp
#include <stack>
#include <queue>

// stack - LIFO
std::stack<int> st;
st.push(1);
st.push(2);
int top = st.top();  // 2
st.pop();

// queue - FIFO
std::queue<int> q;
q.push(1);
q.push(2);
int front = q.front();  // 1
q.pop();

// priority_queue - Heap
std::priority_queue<int> pq;
pq.push(3);
pq.push(1);
pq.push(2);
int max = pq.top();  // 3 (max heap by default)
pq.pop();
```

---

## STL Algorithms

### Iterating and Transforming

```cpp
#include <algorithm>
#include <numeric>

std::vector<int> vec = {1, 2, 3, 4, 5};

// for_each
std::for_each(vec.begin(), vec.end(), [](int& x) {
    x *= 2;
});

// transform
std::vector<int> squared(vec.size());
std::transform(vec.begin(), vec.end(), squared.begin(), [](int x) {
    return x * x;
});

// accumulate
int sum = std::accumulate(vec.begin(), vec.end(), 0);
int product = std::accumulate(vec.begin(), vec.end(), 1, std::multiplies<>());

// Range-based for (modern C++)
for (auto& item : vec) {
    item += 1;
}

for (const auto& item : vec) {  // const reference for read-only
    std::cout << item << " ";
}
```

### Searching and Filtering

```cpp
std::vector<int> vec = {1, 2, 3, 4, 5, 6, 7, 8};

// find
auto it = std::find(vec.begin(), vec.end(), 5);
if (it != vec.end()) {
    std::cout << "Found: " << *it << "\n";
}

// find_if with predicate
auto even = std::find_if(vec.begin(), vec.end(), [](int x) {
    return x % 2 == 0;
});

// count_if
int evenCount = std::count_if(vec.begin(), vec.end(), [](int x) {
    return x % 2 == 0;
});

// copy_if (filter)
std::vector<int> evens;
std::copy_if(vec.begin(), vec.end(), std::back_inserter(evens), [](int x) {
    return x % 2 == 0;
});

// remove_if (doesn't actually remove, returns new end)
auto newEnd = std::remove_if(vec.begin(), vec.end(), [](int x) {
    return x % 2 == 0;
});
vec.erase(newEnd, vec.end());  // Actually remove

// Or use erase-remove idiom in one line
vec.erase(std::remove_if(vec.begin(), vec.end(), [](int x) {
    return x % 2 == 0;
}), vec.end());
```

### Sorting and Ordering

```cpp
std::vector<int> vec = {5, 2, 8, 1, 9};

// sort
std::sort(vec.begin(), vec.end());  // Ascending
std::sort(vec.begin(), vec.end(), std::greater<>());  // Descending

// Custom comparator
struct Person {
    std::string name;
    int age;
};

std::vector<Person> people = {{"Alice", 30}, {"Bob", 25}, {"Charlie", 35}};
std::sort(people.begin(), people.end(), [](const Person& a, const Person& b) {
    return a.age < b.age;  // Sort by age
});

// partial_sort - Sort first N elements
std::partial_sort(vec.begin(), vec.begin() + 3, vec.end());

// nth_element - Put nth element in correct position
std::nth_element(vec.begin(), vec.begin() + vec.size()/2, vec.end());  // Median

// Binary search (requires sorted container)
std::vector<int> sorted = {1, 2, 3, 4, 5};
bool found = std::binary_search(sorted.begin(), sorted.end(), 3);
auto lower = std::lower_bound(sorted.begin(), sorted.end(), 3);  // First >= 3
auto upper = std::upper_bound(sorted.begin(), sorted.end(), 3);  // First > 3
```

---

## Lambdas and Function Objects

### Lambda Expressions

```cpp
// Basic lambda
auto add = [](int a, int b) { return a + b; };
int result = add(3, 4);  // 7

// With capture
int x = 10;
auto addX = [x](int y) { return x + y; };  // Capture x by value
auto addXRef = [&x](int y) { return x + y; };  // Capture x by reference

// Capture all by value or reference
auto captureAll = [=]() { /* use all local vars by value */ };
auto captureAllRef = [&]() { /* use all local vars by reference */ };

// Mutable lambda (can modify captured values)
int count = 0;
auto increment = [count]() mutable { return ++count; };
increment();  // count in lambda is 1, but outer count is still 0

// Generic lambda (C++14)
auto genericAdd = [](auto a, auto b) { return a + b; };
genericAdd(1, 2);      // int + int
genericAdd(1.5, 2.5);  // double + double

// Return type specification
auto divide = [](int a, int b) -> double {
    return static_cast<double>(a) / b;
};
```

### Function Objects (Functors)

```cpp
// Functor class
class Multiplier {
private:
    int factor;

public:
    Multiplier(int f) : factor(f) {}

    int operator()(int x) const {
        return x * factor;
    }
};

Multiplier times3(3);
int result = times3(5);  // 15

// Using with algorithms
std::vector<int> vec = {1, 2, 3, 4, 5};
std::transform(vec.begin(), vec.end(), vec.begin(), Multiplier(2));
// vec is now {2, 4, 6, 8, 10}
```

### std::function

```cpp
#include <functional>

// std::function can hold any callable
std::function<int(int, int)> operation;

operation = [](int a, int b) { return a + b; };
int sum = operation(3, 4);  // 7

operation = [](int a, int b) { return a * b; };
int product = operation(3, 4);  // 12

// Can hold function pointers, lambdas, functors
int subtract(int a, int b) { return a - b; }
operation = subtract;
int diff = operation(7, 3);  // 4

// With member functions
class Calculator {
public:
    int add(int a, int b) { return a + b; }
};

Calculator calc;
std::function<int(Calculator&, int, int)> method = &Calculator::add;
int result = method(calc, 3, 4);  // 7
```

---

## Modern C++ Features

### Structured Bindings (C++17)

```cpp
// With std::pair
std::pair<int, std::string> getData() {
    return {42, "answer"};
}

auto [number, text] = getData();
// number is 42, text is "answer"

// With std::tuple
std::tuple<int, double, std::string> getTuple() {
    return {1, 2.5, "hello"};
}

auto [i, d, s] = getTuple();

// With structs
struct Point {
    int x;
    int y;
};

Point p{10, 20};
auto [x, y] = p;

// Iterate maps with structured bindings
std::map<std::string, int> ages = {{"Alice", 30}, {"Bob", 25}};
for (const auto& [name, age] : ages) {
    std::cout << name << ": " << age << "\n";
}
```

### std::optional (C++17)

```cpp
#include <optional>

// Function that might not return a value
std::optional<std::string> findUser(int id) {
    if (id == 1) {
        return "Alice";
    }
    return std::nullopt;  // No value
}

// Using optional
auto user = findUser(1);
if (user) {
    std::cout << "Found: " << *user << "\n";
} else {
    std::cout << "Not found\n";
}

// value_or
std::string name = findUser(2).value_or("Anonymous");

// has_value
if (user.has_value()) {
    std::cout << user.value() << "\n";
}
```

### std::variant (C++17)

```cpp
#include <variant>

// Variant can hold one of several types
std::variant<int, double, std::string> value;

value = 42;           // Holds int
value = 3.14;         // Now holds double
value = "hello";      // Now holds string

// Access with std::get
try {
    int i = std::get<int>(value);  // Throws if not int
} catch (const std::bad_variant_access&) {
    std::cout << "Not an int\n";
}

// Safe access with get_if
if (auto* str = std::get_if<std::string>(&value)) {
    std::cout << *str << "\n";
}

// Visit with std::visit
std::visit([](auto&& arg) {
    using T = std::decay_t<decltype(arg)>;
    if constexpr (std::is_same_v<T, int>) {
        std::cout << "int: " << arg << "\n";
    } else if constexpr (std::is_same_v<T, double>) {
        std::cout << "double: " << arg << "\n";
    } else if constexpr (std::is_same_v<T, std::string>) {
        std::cout << "string: " << arg << "\n";
    }
}, value);
```

### Concepts (C++20)

```cpp
#include <concepts>

// Define concept
template<typename T>
concept Numeric = std::is_arithmetic_v<T>;

// Use concept as constraint
template<Numeric T>
T square(T x) {
    return x * x;
}

// Concept with requires clause
template<typename T>
concept Incrementable = requires(T x) {
    { ++x } -> std::same_as<T&>;
    { x++ } -> std::same_as<T>;
};

// Multiple constraints
template<typename T>
concept Sortable = requires(T a, T b) {
    { a < b } -> std::convertible_to<bool>;
    { a > b } -> std::convertible_to<bool>;
};

template<Sortable T>
void sort(std::vector<T>& vec) {
    std::sort(vec.begin(), vec.end());
}
```

### Ranges (C++20)

```cpp
#include <ranges>

std::vector<int> vec = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

// Filter and transform with ranges
auto evens = vec | std::views::filter([](int x) { return x % 2 == 0; })
                 | std::views::transform([](int x) { return x * 2; });

for (int x : evens) {
    std::cout << x << " ";  // 4 8 12 16 20
}

// Take first N elements
auto firstThree = vec | std::views::take(3);

// Drop first N elements
auto afterThree = vec | std::views::drop(3);

// Lazy evaluation - views don't copy
auto view = vec | std::views::filter([](int x) { return x > 5; });
// No computation yet
for (int x : view) {  // Computation happens here
    std::cout << x << " ";
}
```

---

## Common Patterns

### CRTP (Curiously Recurring Template Pattern)

```cpp
// Base class template taking derived class as parameter
template<typename Derived>
class Base {
public:
    void interface() {
        static_cast<Derived*>(this)->implementation();
    }

    void implementation() {
        std::cout << "Base implementation\n";
    }
};

class Derived : public Base<Derived> {
public:
    void implementation() {
        std::cout << "Derived implementation\n";
    }
};

// Usage
Derived d;
d.interface();  // Calls Derived::implementation()
```

### Type Erasure

```cpp
#include <memory>
#include <vector>

// Any type that has a draw() method
class Drawable {
private:
    struct Concept {
        virtual ~Concept() = default;
        virtual void draw() const = 0;
    };

    template<typename T>
    struct Model : Concept {
        T object;
        Model(T obj) : object(std::move(obj)) {}
        void draw() const override { object.draw(); }
    };

    std::unique_ptr<Concept> pimpl;

public:
    template<typename T>
    Drawable(T obj) : pimpl(std::make_unique<Model<T>>(std::move(obj))) {}

    void draw() const { pimpl->draw(); }
};

// Different types
class Circle {
public:
    void draw() const { std::cout << "Drawing circle\n"; }
};

class Square {
public:
    void draw() const { std::cout << "Drawing square\n"; }
};

// Use together
std::vector<Drawable> shapes;
shapes.push_back(Circle{});
shapes.push_back(Square{});

for (const auto& shape : shapes) {
    shape.draw();
}
```

### Policy-Based Design

```cpp
// Threading policy
class SingleThreaded {
public:
    void lock() {}
    void unlock() {}
};

class MultiThreaded {
private:
    std::mutex mtx;
public:
    void lock() { mtx.lock(); }
    void unlock() { mtx.unlock(); }
};

// Container with threading policy
template<typename T, typename ThreadingPolicy = SingleThreaded>
class Container : private ThreadingPolicy {
private:
    std::vector<T> data;

public:
    void add(T item) {
        this->lock();
        data.push_back(std::move(item));
        this->unlock();
    }

    T get(size_t index) {
        this->lock();
        T result = data[index];
        this->unlock();
        return result;
    }
};

// Single-threaded version
Container<int, SingleThreaded> single;

// Multi-threaded version
Container<int, MultiThreaded> multi;
```

---

## Troubleshooting

### Undefined Reference / Linker Errors

```cpp
// Problem: Template definitions in .cpp file
// header.h
template<typename T>
class Container {
    void add(T item);
};

// header.cpp - WRONG for templates
template<typename T>
void Container<T>::add(T item) { /* ... */ }

// Fix: Put template definitions in header
// header.h
template<typename T>
class Container {
    void add(T item) {
        // Definition here
    }
};

// Or use explicit instantiation in .cpp
template class Container<int>;  // Only works for known types
```

### Dangling Pointers

```cpp
// Problem: Returning pointer to local variable
int* bad() {
    int x = 42;
    return &x;  // DANGER: x is destroyed
}

// Fix 1: Return by value
int good() {
    int x = 42;
    return x;  // Copy or move
}

// Fix 2: Dynamic allocation (use smart pointers)
std::unique_ptr<int> better() {
    return std::make_unique<int>(42);
}

// Fix 3: Return reference to longer-lived object
class Storage {
    int value = 42;
public:
    int& get() { return value; }  // OK: value lives as long as Storage
};
```

### Iterator Invalidation

```cpp
std::vector<int> vec = {1, 2, 3, 4, 5};

// Problem: Modifying container while iterating
for (auto it = vec.begin(); it != vec.end(); ++it) {
    if (*it == 3) {
        vec.erase(it);  // DANGER: it is now invalid
    }
}

// Fix: Use return value from erase
for (auto it = vec.begin(); it != vec.end();) {
    if (*it == 3) {
        it = vec.erase(it);  // it now points to next element
    } else {
        ++it;
    }
}

// Or use erase-remove idiom
vec.erase(std::remove(vec.begin(), vec.end(), 3), vec.end());
```

### Memory Leaks

```cpp
// Problem: Forgetting to delete
void leak() {
    int* ptr = new int(42);
    // Forgot to delete
}

// Fix: Use smart pointers
void noLeak() {
    auto ptr = std::make_unique<int>(42);
    // Automatically deleted
}

// Problem: Exception before delete
void exceptionLeak() {
    int* ptr = new int(42);
    riskyOperation();  // Might throw
    delete ptr;  // Never reached if exception thrown
}

// Fix: RAII with smart pointer
void exceptionSafe() {
    auto ptr = std::make_unique<int>(42);
    riskyOperation();  // ptr deleted even if exception thrown
}
```

### Slicing Problem

```cpp
class Base {
public:
    virtual void print() { std::cout << "Base\n"; }
};

class Derived : public Base {
    int extra;
public:
    void print() override { std::cout << "Derived\n"; }
};

// Problem: Slicing when passing by value
void bad(Base obj) {  // Takes by value
    obj.print();  // Always prints "Base" (sliced)
}

Derived d;
bad(d);  // Sliced to Base

// Fix: Pass by reference or pointer
void good(Base& obj) {  // Reference
    obj.print();  // Polymorphic behavior
}

void alsoGood(Base* obj) {  // Pointer
    obj->print();  // Polymorphic behavior
}
```

---

## References

- [C++ Reference](https://en.cppreference.com/)
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/)
- [Compiler Explorer](https://godbolt.org/) - See generated assembly
- Specialized skills: `lang-cpp-patterns-dev`, `lang-cpp-cmake-dev`, `lang-cpp-library-dev`
