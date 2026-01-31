# Naming Convention Translation

Quick reference for translating naming conventions between programming languages.

## Case Style Reference

| Style | Example | Languages |
|-------|---------|-----------|
| `camelCase` | `getUserName` | JavaScript, TypeScript, Java, Go (unexported) |
| `PascalCase` | `GetUserName` | C#, Go (exported), TypeScript (types) |
| `snake_case` | `get_user_name` | Python, Rust, Ruby |
| `SCREAMING_SNAKE` | `MAX_BUFFER_SIZE` | Constants in most languages |
| `kebab-case` | `get-user-name` | Lisp, CSS, CLI flags, file names |
| `UPPERCASE` | `HTTP`, `URL` | Acronyms (varies by language) |

---

## Language-Specific Conventions

### TypeScript / JavaScript

| Element | Convention | Example |
|---------|------------|---------|
| Variables | camelCase | `userName` |
| Functions | camelCase | `getUserName()` |
| Classes | PascalCase | `UserService` |
| Interfaces | PascalCase | `IUserService` or `UserService` |
| Types | PascalCase | `UserResponse` |
| Enums | PascalCase | `UserStatus` |
| Enum values | PascalCase or SCREAMING_SNAKE | `Active` or `ACTIVE` |
| Constants | SCREAMING_SNAKE or camelCase | `MAX_RETRIES` or `maxRetries` |
| Files | kebab-case or camelCase | `user-service.ts` |
| Acronyms | Uppercase in middle | `parseJSON`, `httpClient` |

### Python

| Element | Convention | Example |
|---------|------------|---------|
| Variables | snake_case | `user_name` |
| Functions | snake_case | `get_user_name()` |
| Classes | PascalCase | `UserService` |
| Constants | SCREAMING_SNAKE | `MAX_RETRIES` |
| Modules | snake_case | `user_service.py` |
| Packages | snake_case (short) | `mypackage` |
| Private | Leading underscore | `_internal_method` |
| "Very private" | Double underscore | `__mangled_name` |
| Dunder methods | Double underscore both | `__init__`, `__str__` |

### Rust

| Element | Convention | Example |
|---------|------------|---------|
| Variables | snake_case | `user_name` |
| Functions | snake_case | `get_user_name()` |
| Structs | PascalCase | `UserService` |
| Enums | PascalCase | `UserStatus` |
| Enum variants | PascalCase | `UserStatus::Active` |
| Traits | PascalCase | `Serialize` |
| Constants | SCREAMING_SNAKE | `MAX_RETRIES` |
| Static | SCREAMING_SNAKE | `GLOBAL_CONFIG` |
| Modules | snake_case | `user_service.rs` |
| Crates | snake_case (or kebab) | `my_crate` |
| Type parameters | Single uppercase | `T`, `E`, `K`, `V` |
| Lifetimes | Short lowercase | `'a`, `'static` |
| Macros | snake_case! | `println!`, `vec!` |

### Go

| Element | Convention | Example |
|---------|------------|---------|
| Variables (exported) | PascalCase | `UserName` |
| Variables (unexported) | camelCase | `userName` |
| Functions (exported) | PascalCase | `GetUserName()` |
| Functions (unexported) | camelCase | `getUserName()` |
| Structs | PascalCase | `UserService` |
| Interfaces | PascalCase + -er suffix | `Reader`, `UserFetcher` |
| Constants | PascalCase or camelCase | `MaxRetries` |
| Packages | lowercase, short | `user`, `httputil` |
| Files | snake_case | `user_service.go` |
| Acronyms | All caps | `HTTPClient`, `XMLParser` |
| Receivers | Short (1-2 chars) | `func (u *User) Name()` |

---

## Translation Tables

### TypeScript → Python

| TypeScript | Python | Notes |
|------------|--------|-------|
| `getUserName` | `get_user_name` | camelCase → snake_case |
| `UserService` | `UserService` | PascalCase preserved |
| `MAX_RETRIES` | `MAX_RETRIES` | SCREAMING_SNAKE preserved |
| `IUserService` | `UserService` | Drop I prefix (use ABC) |
| `userService.ts` | `user_service.py` | kebab/camel → snake |

### TypeScript → Rust

| TypeScript | Rust | Notes |
|------------|------|-------|
| `getUserName` | `get_user_name` | camelCase → snake_case |
| `UserService` | `UserService` | PascalCase preserved |
| `MAX_RETRIES` | `MAX_RETRIES` | SCREAMING_SNAKE preserved |
| `UserStatus.Active` | `UserStatus::Active` | Enum access syntax |
| `interface User` | `struct User` or `trait User` | Depends on usage |

### TypeScript → Go

| TypeScript | Go (exported) | Go (unexported) | Notes |
|------------|---------------|-----------------|-------|
| `getUserName` | `GetUserName` | `getUserName` | Visibility by case |
| `UserService` | `UserService` | `userService` | Depends on export |
| `MAX_RETRIES` | `MaxRetries` | `maxRetries` | Go avoids SCREAMING |
| `IReader` | `Reader` | - | -er suffix for interfaces |

### Python → Rust

| Python | Rust | Notes |
|--------|------|-------|
| `get_user_name` | `get_user_name` | snake_case preserved |
| `UserService` | `UserService` | PascalCase preserved |
| `MAX_RETRIES` | `MAX_RETRIES` | Constants preserved |
| `_private` | `fn private()` (mod private) | Visibility via module |
| `__init__` | `fn new()` | Convention: new() for constructors |

### Go → Rust

| Go | Rust | Notes |
|----|------|-------|
| `GetUserName` | `get_user_name` | PascalCase → snake_case |
| `userName` | `user_name` | camelCase → snake_case |
| `UserService` | `UserService` | PascalCase preserved |
| `MaxRetries` | `MAX_RETRIES` | Constants to SCREAMING |
| `Reader` | `Read` trait | Similar pattern |

---

## Acronym Handling

### General Rules

| Language | Acronym Handling | Example |
|----------|------------------|---------|
| TypeScript | Lowercase after first | `parseJson`, `httpClient` |
| Python | Lowercase in snake_case | `parse_json`, `http_client` |
| Rust | Lowercase in snake_case | `parse_json`, `http_client` |
| Go | ALL CAPS | `ParseJSON`, `HTTPClient` |

### Common Acronyms

| Acronym | TypeScript | Python | Rust | Go |
|---------|------------|--------|------|-----|
| HTTP | `httpClient` | `http_client` | `http_client` | `HTTPClient` |
| JSON | `parseJson` | `parse_json` | `parse_json` | `ParseJSON` |
| URL | `getUrl` | `get_url` | `get_url` | `GetURL` |
| ID | `userId` | `user_id` | `user_id` | `UserID` |
| API | `apiKey` | `api_key` | `api_key` | `APIKey` |
| SQL | `sqlQuery` | `sql_query` | `sql_query` | `SQLQuery` |
| XML | `parseXml` | `parse_xml` | `parse_xml` | `ParseXML` |
| IO | `ioError` | `io_error` | `io_error` | `IOError` |

---

## File and Module Naming

| Language | Files | Modules/Packages |
|----------|-------|------------------|
| TypeScript | `kebab-case.ts` or `camelCase.ts` | N/A (file = module) |
| Python | `snake_case.py` | `snake_case` |
| Rust | `snake_case.rs` | `snake_case` |
| Go | `snake_case.go` | `lowercase` (short) |

### Special Files

| Purpose | TypeScript | Python | Rust | Go |
|---------|------------|--------|------|-----|
| Entry point | `index.ts`, `main.ts` | `__main__.py` | `main.rs`, `lib.rs` | `main.go` |
| Package init | N/A | `__init__.py` | `mod.rs` or `lib.rs` | Any file in package |
| Tests | `*.test.ts`, `*.spec.ts` | `test_*.py` | `*_test.rs` (inline or file) | `*_test.go` |

---

## Automated Conversion

### Tools

| Conversion | Tool/Approach |
|------------|---------------|
| camelCase → snake_case | `inflection`, regex |
| PascalCase → snake_case | `inflection`, regex |
| Any → Any | `case-converter` libraries |

### Regex Patterns

```python
# camelCase → snake_case
import re
def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# snake_case → camelCase
def to_camel_case(name):
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
```

---

## Related

- `meta-convert-dev` - Core conversion patterns
- Language-specific `lang-*-dev` skills for detailed conventions
