## C++ Formula Patterns

> **Mapping:** Use `language: "cmake"` — most C++ projects use CMake. For autotools-based projects, use `language: "autotools"`. For Meson, use `language: "meson"`.

### Researching a C++ Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system | Repo root | `CMakeLists.txt` (CMake), `meson.build` (Meson), `configure.ac` (Autotools) |
| C++ standard | Build config | Check for `-std=c++17`, `-std=c++20`, etc. |
| Library dependencies | `#include` directives, build config | Boost, Qt, protobuf, etc. |
| Shared vs static | Build config | Check for `BUILD_SHARED_LIBS` or library type |
| Test command | Build config or README | `ctest`, `make test`, or binary `--help` |

### Dependencies

```text
depends_on "cmake" => :build
depends_on "pkg-config" => :build
```

### Install Block (CMake)

```text
def install
  args = std_cmake_args + %w[-DBUILD_SHARED_LIBS=ON -DCMAKE_CXX_STANDARD=17]
  system "cmake", "-S", ".", "-B", "build", *args
  system "cmake", "--build", "build"
  system "cmake", "--install", "build"
end
```

### Common Issues

- **C++ standard:** Ensure the correct standard is passed to CMake
- **Boost dependency:** Many C++ projects use Boost — `depends_on "boost"`
- **ABI compatibility:** C++ ABI can vary between compilers — test on both macOS and Linux
