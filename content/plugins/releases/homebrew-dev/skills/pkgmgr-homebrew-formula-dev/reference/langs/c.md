## C Formula Patterns

> **Mapping:** Use `language: "cmake"` — most C projects use CMake. For autotools-based projects, use `language: "autotools"`. For simple Makefiles, use `language: "make"`.

### Researching a C Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system | Repo root | `CMakeLists.txt` (CMake), `configure.ac` (Autotools), `Makefile` (Make) |
| Compiler flags | Build config, README | Check for required `CFLAGS` or preprocessor defines |
| Library dependencies | `#include` directives, build config | System libraries like `zlib`, `openssl`, `libcurl` |
| Shared vs static | Build config | Check for `-DBUILD_SHARED_LIBS` or `--enable-shared` |
| Test command | Makefile or CTest | `make test`, `ctest`, or `--help` |

### Dependencies

```text
depends_on "cmake" => :build  # or autotools, make
depends_on "pkg-config" => :build
```

### Install Block (CMake)

```text
def install
  args = std_cmake_args + %w[-DBUILD_SHARED_LIBS=ON]
  system "cmake", "-S", ".", "-B", "build", *args
  system "cmake", "--build", "build"
  system "cmake", "--install", "build"
end
```

### Common Issues

- **pkg-config:** Many C projects use pkg-config — add as a build dependency
- **System libraries:** Use `uses_from_macos` for libraries provided by macOS (zlib, libxml2, etc.)
- **Compiler selection:** Homebrew uses Apple Clang on macOS — check for GCC-specific code
