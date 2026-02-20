## Fortran Formula Patterns

> **Mapping:** Use `language: "cmake"` — most Fortran projects use CMake. For Makefile-based projects, use `language: "make"`.

### Researching a Fortran Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system | Repo root | `CMakeLists.txt` (CMake) or `Makefile` |
| Compiler | Build config | Check for `gfortran` or `ifort` requirements |
| Libraries | Build config, source | BLAS, LAPACK, MPI dependencies |
| Test command | README or Makefile | `make test` or binary `--help` |

### Dependencies

```text
depends_on "cmake" => :build
depends_on "gcc"  # for gfortran
```

### Install Block

```text
def install
  args = std_cmake_args + %w[-DCMAKE_Fortran_COMPILER=#{Formula["gcc"].opt_bin}/gfortran]
  system "cmake", "-S", ".", "-B", "build", *args
  system "cmake", "--build", "build"
  system "cmake", "--install", "build"
end
```

### Common Issues

- **gfortran:** Homebrew provides gfortran via the `gcc` formula
- **BLAS/LAPACK:** Use Accelerate framework on macOS or `openblas` formula
- **MPI:** Add `depends_on "open-mpi"` if MPI is required
