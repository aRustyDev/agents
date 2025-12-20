---
name: Make and Makefile Guide
module_type: guide
scope: temporary
priority: low
triggers: ["make", "makefile", "build automation", "make target", "gnu make"]
dependencies: []
conflicts: []
version: 1.0.0
---

# Make and Makefile Guide

## Purpose
Master GNU Make for build automation, task management, and creating reproducible development workflows across different platforms and languages.

## Makefile Basics

### Simple Makefile
```makefile
# Basic structure
target: dependencies
	command

# Example
hello: hello.c
	gcc -o hello hello.c

clean:
	rm -f hello

# Run with: make hello
# Clean with: make clean
```

### Variables and Rules
```makefile
# Variables
CC = gcc
CFLAGS = -Wall -O2
TARGET = myapp
SOURCES = main.c utils.c
OBJECTS = $(SOURCES:.c=.o)

# Rules
$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(TARGET) $(OBJECTS)

# Special variables:
# $@ = target name
# $< = first dependency
# $^ = all dependencies
# $? = dependencies newer than target
```

## Common Patterns

### Python Project
```makefile
# Python project Makefile
.PHONY: help install test lint format clean

PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
FLAKE8 := $(PYTHON) -m flake8
MYPY := $(PYTHON) -m mypy

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

test:  ## Run tests
	$(PYTEST) tests/ -v --cov=src --cov-report=html

lint:  ## Run linters
	$(FLAKE8) src/ tests/
	$(MYPY) src/

format:  ## Format code
	$(BLACK) src/ tests/

clean:  ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov/ dist/ build/

run:  ## Run application
	$(PYTHON) -m src.main

docker-build:  ## Build Docker image
	docker build -t myapp .

docker-run: docker-build  ## Run in Docker
	docker run -p 8000:8000 myapp
```

### Node.js Project
```makefile
# Node.js project Makefile
.PHONY: help install test lint build clean

NPM := npm
YARN := yarn
NODE := node

# Detect package manager
ifneq (,$(wildcard yarn.lock))
	PKG_MANAGER := $(YARN)
else
	PKG_MANAGER := $(NPM)
endif

help:
	@echo "Available targets:"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run tests"
	@echo "  lint       - Run ESLint"
	@echo "  build      - Build project"
	@echo "  dev        - Run development server"
	@echo "  clean      - Clean build artifacts"

install:
	$(PKG_MANAGER) install

test:
	$(PKG_MANAGER) test

test-watch:
	$(PKG_MANAGER) test -- --watch

lint:
	$(PKG_MANAGER) run lint

lint-fix:
	$(PKG_MANAGER) run lint -- --fix

build:
	$(PKG_MANAGER) run build

dev:
	$(PKG_MANAGER) run dev

clean:
	rm -rf node_modules dist coverage .cache

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

# Combined targets
check: lint test  ## Run all checks
ci: install check build  ## CI pipeline
```

### Go Project
```makefile
# Go project Makefile
.PHONY: all build test lint clean

# Variables
BINARY_NAME := myapp
GO := go
GOFLAGS := -v
LDFLAGS := -w -s
PLATFORMS := linux/amd64 darwin/amd64 darwin/arm64 windows/amd64

# Version info
VERSION := $(shell git describe --tags --always --dirty)
BUILD_TIME := $(shell date -u '+%Y-%m-%d_%H:%M:%S')
COMMIT := $(shell git rev-parse --short HEAD)

# Build flags
BUILD_FLAGS := -ldflags "\
	-X main.Version=$(VERSION) \
	-X main.BuildTime=$(BUILD_TIME) \
	-X main.Commit=$(COMMIT) \
	$(LDFLAGS)"

all: clean lint test build

build:
	$(GO) build $(GOFLAGS) $(BUILD_FLAGS) -o $(BINARY_NAME) ./cmd/main.go

build-all:
	@for platform in $(PLATFORMS); do \
		GOOS=$${platform%/*} GOARCH=$${platform#*/} \
		$(GO) build $(BUILD_FLAGS) \
		-o $(BINARY_NAME)-$${platform%/*}-$${platform#*/} \
		./cmd/main.go; \
	done

test:
	$(GO) test $(GOFLAGS) ./...

test-coverage:
	$(GO) test -coverprofile=coverage.out ./...
	$(GO) tool cover -html=coverage.out -o coverage.html

lint:
	golangci-lint run

fmt:
	$(GO) fmt ./...

clean:
	$(GO) clean
	rm -f $(BINARY_NAME) $(BINARY_NAME)-*
	rm -f coverage.out coverage.html

run: build
	./$(BINARY_NAME)

install:
	$(GO) install $(BUILD_FLAGS) ./cmd/main.go
```

## Advanced Features

### Conditional Logic
```makefile
# OS detection
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    PLATFORM := linux
    OPEN_CMD := xdg-open
endif
ifeq ($(UNAME_S),Darwin)
    PLATFORM := macos
    OPEN_CMD := open
endif

# Environment detection
ifdef CI
    TEST_ARGS := --ci-mode
else
    TEST_ARGS := --verbose
endif

# File existence check
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Variable check
ifndef VERSION
    VERSION := dev
endif

serve-docs:
	@echo "Opening docs on $(PLATFORM)..."
	$(OPEN_CMD) http://localhost:8000
```

### Functions and Macros
```makefile
# Define a function
define compile_template
	@echo "Compiling $(1)..."
	$(CC) $(CFLAGS) -c $(1) -o $(2)
endef

# Use the function
%.o: %.c
	$(call compile_template,$<,$@)

# Color output
define colorecho
	@tput setaf $(1)
	@echo $(2)
	@tput sgr0
endef

success:
	$(call colorecho,2,"✓ Build successful!")

error:
	$(call colorecho,1,"✗ Build failed!")

# Multi-line variable
define HELP_TEXT
Usage: make [target]

Targets:
  build    - Build the project
  test     - Run tests
  clean    - Clean artifacts
  help     - Show this help
endef
export HELP_TEXT

help:
	@echo "$$HELP_TEXT"
```

### Pattern Rules and Wildcards
```makefile
# Source discovery
SRCS := $(wildcard src/*.c src/**/*.c)
OBJS := $(SRCS:.c=.o)
DEPS := $(OBJS:.o=.d)

# Pattern rules
%.o: %.c
	$(CC) $(CFLAGS) -MMD -c $< -o $@

# Include dependencies
-include $(DEPS)

# Multiple pattern rule
%.pdf %.png: %.dot
	dot -Tpdf $< -o $*.pdf
	dot -Tpng $< -o $*.png

# Static pattern rules
objects = foo.o bar.o baz.o
$(objects): %.o: %.c
	$(CC) -c $(CFLAGS) $< -o $@
```

### Parallel Execution
```makefile
# Enable parallel builds
.PHONY: all
all: target1 target2 target3

# Explicitly set job count
parallel-build:
	$(MAKE) -j4 all

# Serialize specific targets
.NOTPARALLEL: database-migration

# Order-only prerequisites
build/dir:
	mkdir -p $@

output.txt: | build/dir
	echo "content" > build/dir/output.txt
```

## Real-World Examples

### Full-Stack Application
```makefile
.PHONY: all build test deploy

# Variables
FRONTEND_DIR := frontend
BACKEND_DIR := backend
API_PORT := 8080
UI_PORT := 3000

# Default target
all: deps build test

# Install all dependencies
deps: frontend-deps backend-deps

frontend-deps:
	cd $(FRONTEND_DIR) && npm install

backend-deps:
	cd $(BACKEND_DIR) && go mod download

# Build targets
build: build-frontend build-backend

build-frontend:
	cd $(FRONTEND_DIR) && npm run build

build-backend:
	cd $(BACKEND_DIR) && go build -o ../bin/api ./cmd/api

# Test targets
test: test-unit test-integration

test-unit: test-frontend test-backend

test-frontend:
	cd $(FRONTEND_DIR) && npm test

test-backend:
	cd $(BACKEND_DIR) && go test ./...

test-integration:
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Development
dev:
	@echo "Starting development servers..."
	@make -j2 dev-backend dev-frontend

dev-backend:
	cd $(BACKEND_DIR) && air -c .air.toml

dev-frontend:
	cd $(FRONTEND_DIR) && npm run dev

# Docker operations
docker-build:
	docker build -f $(FRONTEND_DIR)/Dockerfile -t myapp-frontend $(FRONTEND_DIR)
	docker build -f $(BACKEND_DIR)/Dockerfile -t myapp-backend $(BACKEND_DIR)

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Database operations
db-migrate:
	cd $(BACKEND_DIR) && migrate -path ./migrations -database $(DATABASE_URL) up

db-rollback:
	cd $(BACKEND_DIR) && migrate -path ./migrations -database $(DATABASE_URL) down 1

db-seed:
	cd $(BACKEND_DIR) && go run cmd/seed/main.go

# Deployment
deploy-staging:
	./scripts/deploy.sh staging

deploy-production:
	@echo "Deploying to production..."
	@read -p "Are you sure? [y/N] " confirm && \
	[ "$$confirm" = "y" ] && ./scripts/deploy.sh production

# Utilities
lint:
	cd $(FRONTEND_DIR) && npm run lint
	cd $(BACKEND_DIR) && golangci-lint run

format:
	cd $(FRONTEND_DIR) && npm run format
	cd $(BACKEND_DIR) && go fmt ./...

clean:
	rm -rf bin/
	rm -rf $(FRONTEND_DIR)/dist
	rm -rf $(BACKEND_DIR)/tmp
	docker-compose down -v

# Help target
help:
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
```

### CI/CD Integration
```makefile
# CI/CD Makefile
.PHONY: ci cd verify

# CI pipeline
ci: verify build test

verify:
	@echo "Verifying environment..."
	@which docker || (echo "Docker not found" && exit 1)
	@which kubectl || (echo "kubectl not found" && exit 1)

# CD pipeline
cd: ci docker-push deploy

VERSION ?= $(shell git describe --tags --always)
REGISTRY := gcr.io/myproject

docker-push:
	docker tag myapp:latest $(REGISTRY)/myapp:$(VERSION)
	docker push $(REGISTRY)/myapp:$(VERSION)

deploy:
	kubectl set image deployment/myapp myapp=$(REGISTRY)/myapp:$(VERSION)
	kubectl rollout status deployment/myapp

# Environment-specific deployments
deploy-%:
	kubectl config use-context $*
	$(MAKE) deploy
	kubectl config use-context default
```

## Best Practices

### Makefile Organization
```makefile
# 1. Variables at the top
SHELL := /bin/bash
.DEFAULT_GOAL := help

# 2. Includes
-include .env

# 3. .PHONY declarations
.PHONY: all build test clean

# 4. Default target
all: build test

# 5. Grouped targets
## Build Commands ##
build: ...

## Test Commands ##
test: ...

## Utility Commands ##
clean: ...
```

### Error Handling
```makefile
# Exit on error
.SHELLFLAGS := -eu -o pipefail -c

# Check prerequisites
check-env:
ifndef REQUIRED_VAR
	$(error REQUIRED_VAR is not set)
endif

# Guard targets
production-deploy: guard-CONFIRM
guard-%:
	@if [ -z '${${*}}' ]; then \
		echo 'Variable $* not set'; \
		exit 1; \
	fi
```

### Performance Tips
```makefile
# Use := for immediate evaluation
EXPENSIVE_VAR := $(shell find . -name "*.c")

# Cache results
VERSION_FILE := .version
VERSION := $(shell cat $(VERSION_FILE) 2>/dev/null || echo "dev")

# Minimize shell calls
# Bad:
FILES := $(shell find src -name "*.go")
COUNT := $(shell echo $(FILES) | wc -w)

# Good:
FILES := $(shell find src -name "*.go" | tee .files.tmp)
COUNT := $(shell wc -w < .files.tmp)
```

## Debugging

### Debug Techniques
```makefile
# Print variables
debug:
	@echo "SOURCES: $(SOURCES)"
	@echo "OBJECTS: $(OBJECTS)"
	$(info Building $(TARGET)...)

# Trace execution
trace:
	$(MAKE) SHELL="sh -x" build

# Dry run
dry-run:
	$(MAKE) -n build

# Debug specific rule
%.o: %.c
	@echo "Building $@ from $<"
	$(CC) $(CFLAGS) -c $< -o $@
```

---
*Make provides a powerful, portable way to automate builds and manage complex workflows, making it an essential tool for any development project.*