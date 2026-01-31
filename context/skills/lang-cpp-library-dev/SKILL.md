---
name: lang-cpp-library-dev
description: C++-specific library development patterns. Use when creating C++ libraries, designing header-only vs compiled libraries, configuring CMake for library targets, managing ABI stability and versioning, integrating with Conan/vcpkg, documenting with Doxygen, or testing with GoogleTest/Catch2. Extends meta-library-dev with C++ tooling and idioms.
---

# C++ Library Development

C++-specific patterns for library development. This skill extends `meta-library-dev` with C++ tooling, modern C++ idioms (C++17/20/23), and ecosystem practices.

## This Skill Extends

- `meta-library-dev` - Foundational library patterns (API design, versioning, testing strategies)
- `lang-cpp-dev` - Core C++ language features and patterns

For general concepts like semantic versioning, module organization principles, and testing pyramids, see the meta-skill first.

## This Skill Adds

- **Library architecture**: Header-only vs compiled libraries, template libraries
- **CMake tooling**: Library targets, installation, package configuration
- **ABI stability**: Version management, symbol visibility, compatibility
- **Package managers**: Conan, vcpkg integration
- **Documentation**: Doxygen patterns for libraries
- **Testing**: GoogleTest, Catch2 patterns for library testing

## This Skill Does NOT Cover

- General library patterns - see `meta-library-dev`
- Core C++ syntax and features - see `lang-cpp-dev`
- CMake basics - see `lang-cpp-cmake-dev`
- Memory optimization - see `lang-cpp-memory-eng`
- Performance profiling - see `lang-cpp-profiling-eng`

---

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| CMake library target | `add_library(mylib src/mylib.cpp)` |
| Header-only library | `add_library(mylib INTERFACE)` |
| Build library | `cmake --build build` |
| Install library | `cmake --install build` |
| Run tests | `ctest --test-dir build` |
| Generate docs | `doxygen Doxyfile` |
| Conan install | `conan install . --build=missing` |
| vcpkg install | `vcpkg install mylib` |

---

## Library Architecture

### Header-Only vs Compiled Libraries

**Header-Only Libraries:**

```cpp
// my_library.hpp
#ifndef MY_LIBRARY_HPP
#define MY_LIBRARY_HPP

#include <string>
#include <vector>

namespace mylib {

// All code in headers - no .cpp files
template<typename T>
class Container {
public:
    void add(const T& item) {
        items_.push_back(item);
    }

    size_t size() const {
        return items_.size();
    }

private:
    std::vector<T> items_;
};

// Non-template functions must be inline
inline std::string version() {
    return "1.0.0";
}

} // namespace mylib

#endif
```

**Compiled Libraries:**

```cpp
// include/mylib/mylib.hpp
#ifndef MYLIB_HPP
#define MYLIB_HPP

#include <string>
#include <memory>

namespace mylib {

class Parser {
public:
    Parser();
    ~Parser();

    // Public interface only
    bool parse(const std::string& input);
    std::string result() const;

private:
    struct Impl;  // PIMPL pattern
    std::unique_ptr<Impl> impl_;
};

} // namespace mylib

#endif

// src/mylib.cpp
#include "mylib/mylib.hpp"

namespace mylib {

struct Parser::Impl {
    std::string result;
    // Implementation details hidden
};

Parser::Parser() : impl_(std::make_unique<Impl>()) {}
Parser::~Parser() = default;

bool Parser::parse(const std::string& input) {
    // Implementation
    impl_->result = "parsed: " + input;
    return true;
}

std::string Parser::result() const {
    return impl_->result;
}

} // namespace mylib
```

### When to Use Each

| Pattern | Use When | Pros | Cons |
|---------|----------|------|------|
| Header-only | Templates, small utilities | No linking, easy distribution | Longer compile times, code bloat |
| Compiled | Large implementations, ABI stability | Fast compilation, smaller binaries | Requires linking, distribution complexity |
| Hybrid | Mix of both | Best of both worlds | More complex build setup |

---

## CMake Library Configuration

### Basic Library Target

```cmake
cmake_minimum_required(VERSION 3.15)
project(MyLibrary VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiled library
add_library(mylib
    src/parser.cpp
    src/serializer.cpp
)

# Include directories
target_include_directories(mylib
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Link dependencies
target_link_libraries(mylib
    PUBLIC
        fmt::fmt
    PRIVATE
        nlohmann_json::nlohmann_json
)

# Set library properties
set_target_properties(mylib PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR}
    PUBLIC_HEADER include/mylib/mylib.hpp
)
```

### Header-Only Library

```cmake
# Interface library (header-only)
add_library(mylib INTERFACE)

target_include_directories(mylib
    INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_compile_features(mylib INTERFACE cxx_std_17)

# Header-only dependencies
target_link_libraries(mylib
    INTERFACE
        range-v3::range-v3
)
```

### Static vs Shared Library

```cmake
# Option for library type
option(BUILD_SHARED_LIBS "Build shared libraries" OFF)

add_library(mylib
    src/parser.cpp
    src/serializer.cpp
)

# Or explicitly
add_library(mylib_static STATIC src/parser.cpp)
add_library(mylib_shared SHARED src/parser.cpp)

# Symbol visibility for shared libraries
include(GenerateExportHeader)
generate_export_header(mylib
    EXPORT_FILE_NAME ${CMAKE_BINARY_DIR}/include/mylib/export.hpp
)

target_compile_definitions(mylib
    PRIVATE
        MYLIB_EXPORTS  # When building the library
)
```

### Installation Configuration

```cmake
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

# Install targets
install(TARGETS mylib
    EXPORT mylibTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/mylib
)

# Install headers
install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Export targets
install(EXPORT mylibTargets
    FILE mylibTargets.cmake
    NAMESPACE mylib::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/mylib
)

# Generate package config
configure_package_config_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/mylibConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/mylibConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/mylib
)

# Generate version file
write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/mylibConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

# Install package config files
install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/mylibConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/mylibConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/mylib
)
```

### Package Config Template

```cmake
# cmake/mylibConfig.cmake.in
@PACKAGE_INIT@

include(CMakeFindDependencyMacro)

# Find dependencies
find_dependency(fmt)

# Include targets
include("${CMAKE_CURRENT_LIST_DIR}/mylibTargets.cmake")

check_required_components(mylib)
```

---

## Symbol Visibility and ABI Stability

### Export Macros

```cpp
// include/mylib/export.hpp
#ifndef MYLIB_EXPORT_HPP
#define MYLIB_EXPORT_HPP

#ifdef _WIN32
    #ifdef MYLIB_EXPORTS
        #define MYLIB_API __declspec(dllexport)
    #else
        #define MYLIB_API __declspec(dllimport)
    #endif
#else
    #define MYLIB_API __attribute__((visibility("default")))
#endif

#endif

// Usage in headers
#include "mylib/export.hpp"

namespace mylib {

class MYLIB_API Parser {
public:
    Parser();
    ~Parser();
    bool parse(const std::string& input);
};

} // namespace mylib
```

### CMake Visibility Configuration

```cmake
# Set default symbol visibility to hidden
set_target_properties(mylib PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON
)

# Generate export header
include(GenerateExportHeader)
generate_export_header(mylib
    BASE_NAME MYLIB
    EXPORT_FILE_NAME ${CMAKE_BINARY_DIR}/include/mylib/export.hpp
)
```

### ABI Versioning

```cpp
// Use inline namespaces for ABI versioning
namespace mylib {
inline namespace v1 {

class Parser {
    // v1 implementation
};

} // namespace v1

// When breaking ABI in next major version:
// inline namespace v2 {
//     class Parser { /* new implementation */ };
// }

} // namespace mylib

// Users automatically get latest inline namespace
mylib::Parser p;  // Uses mylib::v1::Parser
```

### PIMPL Pattern for ABI Stability

```cpp
// Public header - ABI stable
// include/mylib/database.hpp
#ifndef MYLIB_DATABASE_HPP
#define MYLIB_DATABASE_HPP

#include <memory>
#include <string>

namespace mylib {

class Database {
public:
    Database(const std::string& path);
    ~Database();

    // Copyable/movable
    Database(const Database&);
    Database& operator=(const Database&);
    Database(Database&&) noexcept;
    Database& operator=(Database&&) noexcept;

    void execute(const std::string& query);

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace mylib

#endif

// Implementation - can change without breaking ABI
// src/database.cpp
#include "mylib/database.hpp"
#include <vector>
#include <map>

namespace mylib {

struct Database::Impl {
    std::string path;
    std::vector<std::string> cache;
    std::map<std::string, int> indices;

    // Private implementation details
};

Database::Database(const std::string& path)
    : impl_(std::make_unique<Impl>()) {
    impl_->path = path;
}

Database::~Database() = default;

Database::Database(const Database& other)
    : impl_(std::make_unique<Impl>(*other.impl_)) {}

Database& Database::operator=(const Database& other) {
    if (this != &other) {
        impl_ = std::make_unique<Impl>(*other.impl_);
    }
    return *this;
}

Database::Database(Database&&) noexcept = default;
Database& Database::operator=(Database&&) noexcept = default;

void Database::execute(const std::string& query) {
    // Implementation
}

} // namespace mylib
```

---

## Template Library Patterns

### Header Organization

```
include/
└── mylib/
    ├── mylib.hpp           # Main public header
    ├── container.hpp       # Template class
    └── detail/
        └── impl.hpp        # Implementation details

// include/mylib/container.hpp
#ifndef MYLIB_CONTAINER_HPP
#define MYLIB_CONTAINER_HPP

#include <vector>
#include <algorithm>

namespace mylib {

template<typename T>
class Container {
public:
    void add(const T& item);
    void add(T&& item);

    template<typename Predicate>
    void remove_if(Predicate pred);

    size_t size() const { return items_.size(); }

private:
    std::vector<T> items_;
};

// Template implementations in same header
template<typename T>
void Container<T>::add(const T& item) {
    items_.push_back(item);
}

template<typename T>
void Container<T>::add(T&& item) {
    items_.push_back(std::move(item));
}

template<typename T>
template<typename Predicate>
void Container<T>::remove_if(Predicate pred) {
    items_.erase(
        std::remove_if(items_.begin(), items_.end(), pred),
        items_.end()
    );
}

} // namespace mylib

#endif
```

### Extern Templates (Reduce Compile Time)

```cpp
// mylib.hpp - Declaration
template<typename T>
class Container {
    void add(const T& item);
};

// mylib_extern.hpp - Extern template declarations
extern template class Container<int>;
extern template class Container<std::string>;

// mylib.cpp - Explicit instantiation
#include "mylib.hpp"

template class Container<int>;
template class Container<std::string>;
```

### Concepts for Template Constraints (C++20)

```cpp
#include <concepts>

namespace mylib {

// Define concepts
template<typename T>
concept Serializable = requires(T t) {
    { t.serialize() } -> std::convertible_to<std::string>;
};

template<typename T>
concept Numeric = std::is_arithmetic_v<T>;

// Use in templates
template<Serializable T>
class DataStore {
public:
    void save(const T& data) {
        std::string serialized = data.serialize();
        // Save serialized data
    }
};

// Multiple constraints
template<typename T>
concept Container = requires(T t) {
    typename T::value_type;
    { t.size() } -> std::convertible_to<size_t>;
    { t.begin() } -> std::input_iterator;
    { t.end() } -> std::input_iterator;
};

template<Container C>
void process(const C& container) {
    for (const auto& item : container) {
        // Process item
    }
}

} // namespace mylib
```

---

## Package Manager Integration

### Conan Configuration

```python
# conanfile.py
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout

class MyLibConan(ConanFile):
    name = "mylib"
    version = "1.0.0"
    license = "MIT"
    author = "Your Name <your.email@example.com>"
    url = "https://github.com/username/mylib"
    description = "A C++ library for parsing"
    topics = ("parsing", "cpp", "library")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def requirements(self):
        self.requires("fmt/9.1.0")
        self.requires("nlohmann_json/3.11.2")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["mylib"]
        self.cpp_info.includedirs = ["include"]
```

### vcpkg Configuration

```json
{
  "name": "mylib",
  "version": "1.0.0",
  "description": "A C++ library for parsing",
  "homepage": "https://github.com/username/mylib",
  "license": "MIT",
  "dependencies": [
    "fmt",
    "nlohmann-json"
  ],
  "features": {
    "tests": {
      "description": "Build tests",
      "dependencies": [
        "gtest"
      ]
    }
  }
}
```

```cmake
# ports/mylib/portfile.cmake
vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO username/mylib
    REF v1.0.0
    SHA512 <hash>
    HEAD_REF main
)

vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
    OPTIONS
        -DBUILD_TESTING=OFF
)

vcpkg_cmake_install()
vcpkg_cmake_config_fixup(CONFIG_PATH lib/cmake/mylib)

file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)
```

---

## Documentation with Doxygen

### Doxyfile Configuration

```
# Doxyfile
PROJECT_NAME           = "MyLib"
PROJECT_BRIEF          = "A modern C++ parsing library"
PROJECT_VERSION        = 1.0.0

INPUT                  = include/ src/ README.md
FILE_PATTERNS          = *.hpp *.cpp *.md
RECURSIVE              = YES
EXCLUDE_PATTERNS       = */detail/* */test/*

EXTRACT_ALL            = YES
EXTRACT_PRIVATE        = NO
EXTRACT_STATIC         = YES

GENERATE_HTML          = YES
HTML_OUTPUT            = docs/html
GENERATE_LATEX         = NO

USE_MDFILE_AS_MAINPAGE = README.md
MARKDOWN_SUPPORT       = YES

ENABLE_PREPROCESSING   = YES
MACRO_EXPANSION        = YES
EXPAND_ONLY_PREDEF     = NO

HAVE_DOT               = YES
CALL_GRAPH             = YES
CALLER_GRAPH           = YES
CLASS_DIAGRAMS         = YES
```

### Documentation Comments

```cpp
/**
 * @file parser.hpp
 * @brief Main parser interface
 * @author Your Name
 * @version 1.0.0
 */

#ifndef MYLIB_PARSER_HPP
#define MYLIB_PARSER_HPP

namespace mylib {

/**
 * @brief A parser for processing input data
 *
 * This class provides methods for parsing various input formats
 * and converting them to structured data.
 *
 * @code
 * Parser p;
 * p.parse("input data");
 * auto result = p.result();
 * @endcode
 *
 * @note The parser is not thread-safe
 * @warning Reusing the same parser instance may lead to data races
 */
class Parser {
public:
    /**
     * @brief Construct a new Parser object
     *
     * @param strict Enable strict parsing mode
     * @throw std::invalid_argument if configuration is invalid
     */
    explicit Parser(bool strict = false);

    /**
     * @brief Parse input data
     *
     * @param input The input string to parse
     * @return true if parsing succeeded
     * @return false if parsing failed
     *
     * @pre input must not be empty
     * @post result() contains parsed data if successful
     *
     * @see result()
     */
    bool parse(const std::string& input);

    /**
     * @brief Get the parsing result
     *
     * @return const std::string& Reference to the result
     *
     * @pre parse() must have been called successfully
     */
    const std::string& result() const;

private:
    bool strict_;         ///< Strict parsing mode flag
    std::string result_;  ///< Parsed result storage
};

/**
 * @brief Parse input with default settings
 *
 * @tparam T The output type
 * @param input Input string
 * @return T Parsed result
 *
 * @example
 * @code
 * auto data = parse<Data>("input");
 * @endcode
 */
template<typename T>
T parse(const std::string& input);

} // namespace mylib

#endif
```

### CMake Integration

```cmake
# Find Doxygen
find_package(Doxygen)

if(DOXYGEN_FOUND)
    # Configure Doxyfile
    set(DOXYGEN_IN ${CMAKE_CURRENT_SOURCE_DIR}/docs/Doxyfile.in)
    set(DOXYGEN_OUT ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)

    configure_file(${DOXYGEN_IN} ${DOXYGEN_OUT} @ONLY)

    # Add documentation target
    add_custom_target(docs
        COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Generating API documentation with Doxygen"
        VERBATIM
    )
endif()
```

---

## Testing with GoogleTest

### CMake Test Configuration

```cmake
# Enable testing
enable_testing()

# Find GoogleTest
find_package(GTest REQUIRED)

# Test executable
add_executable(mylib_test
    tests/parser_test.cpp
    tests/serializer_test.cpp
)

target_link_libraries(mylib_test
    PRIVATE
        mylib
        GTest::gtest
        GTest::gtest_main
)

# Discover tests
include(GoogleTest)
gtest_discover_tests(mylib_test)
```

### Test Structure

```cpp
// tests/parser_test.cpp
#include <gtest/gtest.h>
#include "mylib/parser.hpp"

namespace mylib {
namespace test {

class ParserTest : public ::testing::Test {
protected:
    void SetUp() override {
        parser = std::make_unique<Parser>();
    }

    void TearDown() override {
        parser.reset();
    }

    std::unique_ptr<Parser> parser;
};

TEST_F(ParserTest, ParseValidInput) {
    ASSERT_TRUE(parser->parse("valid input"));
    EXPECT_EQ(parser->result(), "parsed: valid input");
}

TEST_F(ParserTest, ParseEmptyInput) {
    EXPECT_FALSE(parser->parse(""));
}

TEST_F(ParserTest, ParseWithStrictMode) {
    Parser strict_parser(true);
    EXPECT_THROW(strict_parser.parse("invalid"), std::runtime_error);
}

// Parameterized tests
class ParserParamTest : public ::testing::TestWithParam<std::string> {};

TEST_P(ParserParamTest, ParseMultipleInputs) {
    Parser p;
    EXPECT_TRUE(p.parse(GetParam()));
}

INSTANTIATE_TEST_SUITE_P(
    ValidInputs,
    ParserParamTest,
    ::testing::Values("input1", "input2", "input3")
);

} // namespace test
} // namespace mylib
```

---

## Testing with Catch2

### CMake Configuration

```cmake
find_package(Catch2 3 REQUIRED)

add_executable(mylib_test
    tests/parser_test.cpp
)

target_link_libraries(mylib_test
    PRIVATE
        mylib
        Catch2::Catch2WithMain
)

include(Catch)
catch_discover_tests(mylib_test)
```

### Test Structure

```cpp
// tests/parser_test.cpp
#include <catch2/catch_test_macros.hpp>
#include "mylib/parser.hpp"

TEST_CASE("Parser handles valid input", "[parser]") {
    mylib::Parser p;

    SECTION("Basic parsing") {
        REQUIRE(p.parse("test input"));
        REQUIRE(p.result() == "parsed: test input");
    }

    SECTION("Empty input fails") {
        REQUIRE_FALSE(p.parse(""));
    }
}

TEST_CASE("Parser with strict mode", "[parser][strict]") {
    mylib::Parser p(true);

    REQUIRE_THROWS_AS(p.parse("invalid"), std::runtime_error);
}

// Template tests
TEMPLATE_TEST_CASE("Container works with different types",
                   "[container][template]",
                   int, double, std::string) {
    mylib::Container<TestType> container;

    TestType value{};
    container.add(value);

    REQUIRE(container.size() == 1);
}
```

---

## Versioning Best Practices

### Semantic Versioning

```
MAJOR.MINOR.PATCH (e.g., 1.2.3)

MAJOR: Incompatible API changes (breaking changes)
MINOR: Backward-compatible functionality additions
PATCH: Backward-compatible bug fixes
```

### Version Header

```cpp
// include/mylib/version.hpp
#ifndef MYLIB_VERSION_HPP
#define MYLIB_VERSION_HPP

#define MYLIB_VERSION_MAJOR 1
#define MYLIB_VERSION_MINOR 0
#define MYLIB_VERSION_PATCH 0

#define MYLIB_VERSION \
    (MYLIB_VERSION_MAJOR * 10000 + \
     MYLIB_VERSION_MINOR * 100 + \
     MYLIB_VERSION_PATCH)

#define MYLIB_VERSION_STRING "1.0.0"

namespace mylib {

struct Version {
    static constexpr int major = MYLIB_VERSION_MAJOR;
    static constexpr int minor = MYLIB_VERSION_MINOR;
    static constexpr int patch = MYLIB_VERSION_PATCH;
    static constexpr const char* string = MYLIB_VERSION_STRING;
};

} // namespace mylib

#endif
```

### CMake Version Configuration

```cmake
# CMakeLists.txt
project(MyLib VERSION 1.0.0)

# Generate version header
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/include/mylib/version.hpp.in
    ${CMAKE_CURRENT_BINARY_DIR}/include/mylib/version.hpp
)
```

```cpp
// include/mylib/version.hpp.in
#ifndef MYLIB_VERSION_HPP
#define MYLIB_VERSION_HPP

#define MYLIB_VERSION_MAJOR @PROJECT_VERSION_MAJOR@
#define MYLIB_VERSION_MINOR @PROJECT_VERSION_MINOR@
#define MYLIB_VERSION_PATCH @PROJECT_VERSION_PATCH@

#define MYLIB_VERSION_STRING "@PROJECT_VERSION@"

#endif
```

---

## Example: Complete Library Structure

```
mylib/
├── CMakeLists.txt
├── conanfile.py
├── vcpkg.json
├── README.md
├── LICENSE
├── CHANGELOG.md
├── Doxyfile
├── .clang-format
├── include/
│   └── mylib/
│       ├── mylib.hpp          # Main public header
│       ├── parser.hpp
│       ├── serializer.hpp
│       ├── version.hpp
│       └── export.hpp
├── src/
│   ├── parser.cpp
│   └── serializer.cpp
├── tests/
│   ├── CMakeLists.txt
│   ├── parser_test.cpp
│   └── serializer_test.cpp
├── examples/
│   ├── CMakeLists.txt
│   ├── basic_usage.cpp
│   └── advanced_usage.cpp
├── docs/
│   └── Doxyfile.in
└── cmake/
    ├── mylibConfig.cmake.in
    └── FindMyLibDeps.cmake
```

---

## Anti-Patterns

### 1. Exposing Implementation Details

```cpp
// Bad: Exposing internal types
class Parser {
public:
    std::shared_ptr<InternalNode> parse(const std::string& input);
};

// Good: Return opaque type or public interface
class Parser {
public:
    Document parse(const std::string& input);
};
```

### 2. Using `using namespace` in Headers

```cpp
// Bad: Pollutes namespace for users
// mylib.hpp
using namespace std;

class Parser {
    string parse(const string& input);
};

// Good: Fully qualified names
// mylib.hpp
class Parser {
    std::string parse(const std::string& input);
};
```

### 3. Inline Everything

```cpp
// Bad: Large inline functions
class Parser {
    void parse(const std::string& input) {
        // 100 lines of code...
    }
};

// Good: Separate declaration and definition
class Parser {
    void parse(const std::string& input);
};
```

### 4. Breaking ABI Without Major Version Bump

```cpp
// v1.0.0
class Data {
    int value;
};

// v1.1.0 - WRONG! This breaks ABI
class Data {
    int value;
    int newValue;  // Changes size/layout
};

// Correct: Create new type or bump major version
```

---

## References

- `meta-library-dev` - Foundational library patterns
- `lang-cpp-dev` - Core C++ features
- `lang-cpp-cmake-dev` - CMake configuration
- [CMake Documentation](https://cmake.org/documentation/)
- [Conan Documentation](https://docs.conan.io/)
- [vcpkg Documentation](https://vcpkg.io/)
- [GoogleTest Documentation](https://google.github.io/googletest/)
- [Catch2 Documentation](https://github.com/catchorg/Catch2)
- [Doxygen Documentation](https://www.doxygen.nl/)
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/)
