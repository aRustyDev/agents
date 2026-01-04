# Language-Specific Workflow Examples

Comprehensive GitHub Actions workflow examples for different programming languages, following best practices for each ecosystem.

## Node.js / JavaScript

### Basic Node.js CI

```yaml
name: Node.js CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18, 20, 22]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test

      - name: Generate coverage
        run: npm run test:coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage/lcov.info
```

### Node.js with Matrix Testing

```yaml
name: Node.js Matrix CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}

    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [18, 20]
        include:
          # Test LTS versions on Linux only
          - os: ubuntu-latest
            node-version: 16
          # Test latest on all platforms
          - os: ubuntu-latest
            node-version: 22
          - os: windows-latest
            node-version: 22
          - os: macos-latest
            node-version: 22

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build project
        run: npm run build
```

## Rust

### Basic Rust CI

```yaml
name: Rust CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  CARGO_TERM_COLOR: always

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Rust toolchain
        uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy

      - name: Setup Rust cache
        uses: Swatinem/rust-cache@v2

      - name: Check formatting
        run: cargo fmt -- --check

      - name: Run clippy
        run: cargo clippy -- -D warnings

      - name: Run tests
        run: cargo test --verbose

      - name: Build release
        run: cargo build --release --verbose
```

### Rust Cross-Platform

```yaml
name: Rust Cross-Platform

on: [push, pull_request]

jobs:
  test:
    name: Test on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        rust: [stable, beta]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Rust ${{ matrix.rust }}
        uses: dtolnay/rust-toolchain@master
        with:
          toolchain: ${{ matrix.rust }}
          components: rustfmt, clippy

      - name: Setup cache
        uses: Swatinem/rust-cache@v2

      - name: Run tests
        run: cargo test --all-features

  coverage:
    name: Code Coverage
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Install tarpaulin
        run: cargo install cargo-tarpaulin

      - name: Generate coverage
        run: cargo tarpaulin --verbose --all-features --workspace --timeout 120 --out xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

## Python

### Basic Python CI

```yaml
name: Python CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache pip packages
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          black --check .
          isort --check-only .
          flake8 .

      - name: Run type checking
        run: mypy .

      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

### Python with Poetry

```yaml
name: Python with Poetry

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Load cached Poetry installation
        id: cached-poetry
        uses: actions/cache@v4
        with:
          path: ~/.local
          key: poetry-0

      - name: Install Poetry
        if: steps.cached-poetry.outputs.cache-hit != 'true'
        uses: snok/install-poetry@v1
        with:
          installer: pip
          virtualenvs-in-project: true

      - name: Load cached venv
        id: cached-poetry-dependencies
        uses: actions/cache@v4
        with:
          path: .venv
          key: venv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}

      - name: Install dependencies
        if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
        run: poetry install --no-interaction --no-root

      - name: Install project
        run: poetry install --no-interaction

      - name: Run tests
        run: |
          source .venv/bin/activate
          pytest --cov=src --cov-report=xml
```

## Go

### Basic Go CI

```yaml
name: Go CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        go-version: ["1.20", "1.21", "1.22"]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Go ${{ matrix.go-version }}
        uses: actions/setup-go@v4
        with:
          go-version: ${{ matrix.go-version }}

      - name: Cache Go modules
        uses: actions/cache@v4
        with:
          path: ~/go/pkg/mod
          key: ${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}
          restore-keys: |
            ${{ runner.os }}-go-

      - name: Download dependencies
        run: go mod download

      - name: Verify dependencies
        run: go mod verify

      - name: Run vet
        run: go vet ./...

      - name: Run tests
        run: go test -race -coverprofile=coverage.out -covermode=atomic ./...

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.out
```

### Go with Build Matrix

```yaml
name: Go Build Matrix

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        go-version: ["1.21", "1.22"]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Go
        uses: actions/setup-go@v4
        with:
          go-version: ${{ matrix.go-version }}

      - name: Build
        run: go build -v ./...

      - name: Test
        run: go test -v ./...

  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Go
        uses: actions/setup-go@v4
        with:
          go-version: "1.22"

      - name: golangci-lint
        uses: golangci/golangci-lint-action@v3
        with:
          version: latest
```

## Java

### Basic Java CI with Maven

```yaml
name: Java CI with Maven

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        java: [11, 17, 21]

    steps:
      - uses: actions/checkout@v4

      - name: Setup JDK ${{ matrix.java }}
        uses: actions/setup-java@v4
        with:
          java-version: ${{ matrix.java }}
          distribution: 'temurin'

      - name: Cache Maven packages
        uses: actions/cache@v4
        with:
          path: ~/.m2
          key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
          restore-keys: ${{ runner.os }}-m2

      - name: Run tests
        run: mvn clean verify

      - name: Generate test report
        uses: dorny/test-reporter@v1
        if: success() || failure()
        with:
          name: Maven Tests
          path: target/surefire-reports/*.xml
          reporter: java-junit
```

### Java with Gradle

```yaml
name: Java CI with Gradle

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        java: [11, 17, 21]

    steps:
      - uses: actions/checkout@v4

      - name: Setup JDK ${{ matrix.java }}
        uses: actions/setup-java@v4
        with:
          java-version: ${{ matrix.java }}
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/gradle-build-action@v2

      - name: Run tests
        run: ./gradlew test

      - name: Generate test report
        uses: dorny/test-reporter@v1
        if: success() || failure()
        with:
          name: Gradle Tests
          path: build/test-results/test/*.xml
          reporter: java-junit

      - name: Build JAR
        run: ./gradlew bootJar
```

## C/C++

### Basic C++ CI

```yaml
name: C++ CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        build_type: [Release, Debug]
        compiler: [gcc, clang]
        exclude:
          - os: windows-latest
            compiler: gcc
          - os: windows-latest
            compiler: clang

    steps:
      - uses: actions/checkout@v4

      - name: Setup CMake
        uses: jwlawson/actions-setup-cmake@v1

      - name: Setup Ninja
        uses: seanmiddleditch/gha-setup-ninja@master

      - name: Configure CMake
        run: |
          cmake -B build -G Ninja \
            -DCMAKE_BUILD_TYPE=${{ matrix.build_type }} \
            -DCMAKE_CXX_COMPILER=${{ matrix.compiler == 'clang' && 'clang++' || 'g++' }}

      - name: Build
        run: cmake --build build --config ${{ matrix.build_type }}

      - name: Test
        working-directory: build
        run: ctest -C ${{ matrix.build_type }} --output-on-failure
```

### C++ with Conan

```yaml
name: C++ with Conan

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}

    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Conan
        run: pip install conan

      - name: Setup Conan profile
        run: |
          conan profile detect --force
          conan profile show default

      - name: Install dependencies
        run: conan install . --build=missing

      - name: Configure CMake
        run: cmake --preset conan-default

      - name: Build
        run: cmake --build --preset conan-release

      - name: Test
        run: ctest --preset conan-default
```

## Docker

### Docker Build and Push

```yaml
name: Docker Build

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: myuser/myapp
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Multi-Stage Docker Build

```yaml
name: Multi-Stage Docker

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build test image
        uses: docker/build-push-action@v5
        with:
          context: .
          target: test
          load: true
          tags: myapp:test
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run tests
        run: docker run --rm myapp:test

      - name: Build production image
        if: github.ref == 'refs/heads/main'
        uses: docker/build-push-action@v5
        with:
          context: .
          target: production
          push: true
          tags: myuser/myapp:latest
```

## Cross-Language Patterns

### Monorepo with Multiple Languages

```yaml
name: Monorepo CI

on: [push, pull_request]

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      frontend: ${{ steps.changes.outputs.frontend }}
      backend: ${{ steps.changes.outputs.backend }}
      docs: ${{ steps.changes.outputs.docs }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            frontend:
              - 'frontend/**'
            backend:
              - 'backend/**'
            docs:
              - 'docs/**'

  frontend:
    needs: detect-changes
    if: ${{ needs.detect-changes.outputs.frontend == 'true' }}
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm test
      - run: npm run build

  backend:
    needs: detect-changes
    if: ${{ needs.detect-changes.outputs.backend == 'true' }}
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
          cache-dependency-path: backend/requirements.txt
      - run: pip install -r requirements.txt
      - run: python -m pytest
```

### Language-Specific Security Scanning

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  scan-js:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run npm audit
        run: npm audit --audit-level high
      - name: Run Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  scan-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run safety check
        run: |
          pip install safety
          safety check -r requirements.txt
      - name: Run bandit
        run: |
          pip install bandit
          bandit -r src/

  scan-go:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v4
      - name: Run gosec
        uses: securecodewarrior/github-action-gosec@master
      - name: Run nancy
        run: |
          go list -json -deps ./... | nancy sleuth
```

## Performance Optimizations

### Caching Strategies by Language

| Language | Cache Target | Cache Key Pattern |
|----------|-------------|------------------|
| **Node.js** | `~/.npm` | `${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}` |
| **Python** | `~/.cache/pip` | `${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}` |
| **Rust** | `~/.cargo` + `target/` | `${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}` |
| **Go** | `~/go/pkg/mod` | `${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}` |
| **Java/Maven** | `~/.m2` | `${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}` |
| **Java/Gradle** | `~/.gradle` | `${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}` |

### Parallel Testing

```yaml
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - name: Run tests (shard ${{ matrix.shard }})
        run: |
          pytest --shard-id=${{ matrix.shard }} --num-shards=4
```

## Cross-References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Actions Marketplace](https://github.com/marketplace?type=actions)
- [Setup Actions Collection](https://github.com/actions?q=setup&type=all&language=&sort=stargazers)