---
name: patterns-serialization-dev
description: Cross-cutting patterns for serialization and validation across languages. Use when translating JSON handling between languages, converting struct tags to derive macros, mapping validation libraries, or designing schema-based serialization for language conversions.
---

# Serialization Patterns

Cross-language reference for serialization, deserialization, and validation patterns. This skill helps translate data handling patterns between languages during code conversion.

## Overview

**This skill covers:**
- JSON/YAML/TOML serialization comparison
- Struct tags, derive macros, dataclasses
- Validation library mappings
- Schema generation and enforcement
- Custom serializer/deserializer patterns

**This skill does NOT cover:**
- Building applications with serialization (see `lang-*-dev` skills)
- Protocol buffers/gRPC (see dedicated skills)
- Database ORM mapping (see database-specific skills)

---

## Serialization Mechanism Comparison

| Language | Primary Approach | Configuration | Validation |
|----------|------------------|---------------|------------|
| TypeScript | Class decorators | `class-transformer` | `class-validator`, `zod` |
| Python | Dataclasses/Pydantic | Type hints + decorators | Built into Pydantic |
| Rust | Derive macros | `#[serde(...)]` attributes | `validator` crate |
| Go | Struct tags | `` `json:"name"` `` | `validator` package |
| Java/Kotlin | Annotations | `@JsonProperty` | Bean Validation |
| C# | Attributes | `[JsonPropertyName]` | Data Annotations |

---

## JSON Serialization by Language

### TypeScript

```typescript
// class-transformer + class-validator
import { Type, Expose, Transform } from 'class-transformer';
import { IsEmail, Length, IsOptional } from 'class-validator';

class User {
  @Expose({ name: 'user_id' })
  id: string;

  @Length(1, 100)
  name: string;

  @IsEmail()
  @IsOptional()
  email?: string;

  @Type(() => Date)
  @Transform(({ value }) => new Date(value), { toClassOnly: true })
  createdAt: Date;
}

// Usage
const user = plainToInstance(User, jsonData);
const errors = await validate(user);
```

### Python (Pydantic)

```python
from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: str = Field(alias='user_id')
    name: str = Field(min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    created_at: datetime

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('name cannot be empty')
        return v

    class Config:
        populate_by_name = True  # Allow both 'id' and 'user_id'

# Usage
user = User.model_validate(json_data)
json_str = user.model_dump_json()
```

### Python (dataclasses + dacite)

```python
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from dacite import from_dict, Config

@dataclass
class User:
    id: str
    name: str
    email: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

# Usage
user = from_dict(User, json_data, config=Config(
    cast=[datetime],
    strict=True
))
```

### Rust (Serde)

```rust
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use validator::Validate;

#[derive(Debug, Serialize, Deserialize, Validate)]
#[serde(rename_all = "snake_case")]
struct User {
    #[serde(rename = "user_id")]
    id: String,

    #[validate(length(min = 1, max = 100))]
    name: String,

    #[serde(skip_serializing_if = "Option::is_none")]
    #[validate(email)]
    email: Option<String>,

    #[serde(with = "chrono::serde::ts_seconds")]
    created_at: DateTime<Utc>,
}

// Usage
let user: User = serde_json::from_str(&json_str)?;
user.validate()?;
let json = serde_json::to_string(&user)?;
```

### Go

```go
import (
    "encoding/json"
    "time"

    "github.com/go-playground/validator/v10"
)

type User struct {
    ID        string    `json:"user_id"`
    Name      string    `json:"name" validate:"required,min=1,max=100"`
    Email     *string   `json:"email,omitempty" validate:"omitempty,email"`
    CreatedAt time.Time `json:"created_at"`
}

// Usage
var user User
err := json.Unmarshal(jsonData, &user)

validate := validator.New()
err = validate.Struct(user)
```

### Java (Jackson)

```java
import com.fasterxml.jackson.annotation.*;
import jakarta.validation.constraints.*;
import java.time.Instant;

public class User {
    @JsonProperty("user_id")
    private String id;

    @NotBlank
    @Size(min = 1, max = 100)
    private String name;

    @Email
    private String email;

    @JsonFormat(shape = JsonFormat.Shape.STRING)
    private Instant createdAt;

    // getters, setters...
}

// Usage
ObjectMapper mapper = new ObjectMapper();
User user = mapper.readValue(jsonStr, User.class);
```

---

## Field Mapping Translation

### Rename Fields

| Language | Syntax | Example |
|----------|--------|---------|
| TypeScript | `@Expose({ name: 'x' })` | `@Expose({ name: 'user_id' })` |
| Python | `Field(alias='x')` | `id: str = Field(alias='user_id')` |
| Rust | `#[serde(rename = "x")]` | `#[serde(rename = "user_id")]` |
| Go | `` `json:"x"` `` | `` `json:"user_id"` `` |
| Java | `@JsonProperty("x")` | `@JsonProperty("user_id")` |

### Case Conversion

| Language | Syntax | Result |
|----------|--------|--------|
| TypeScript | Manual or transformer | N/A |
| Python | `model_config = ConfigDict(alias_generator=to_camel)` | `userId` |
| Rust | `#[serde(rename_all = "camelCase")]` | `userId` |
| Go | `` `json:"userId"` `` (manual) | `userId` |
| Java | `@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)` | `user_id` |

### Skip Null/Empty

| Language | Syntax | Effect |
|----------|--------|--------|
| TypeScript | `@Exclude()` with condition | Excludes field |
| Python | `exclude_none=True` in `model_dump()` | Skips None |
| Rust | `#[serde(skip_serializing_if = "Option::is_none")]` | Skips None |
| Go | `json:",omitempty"` | Skips zero values |
| Java | `@JsonInclude(Include.NON_NULL)` | Skips null |

---

## Validation Pattern Translation

### String Validation

| Validation | TypeScript | Python | Rust | Go |
|------------|------------|--------|------|-----|
| Required | `@IsNotEmpty()` | `str` (not Optional) | Not Option | `validate:"required"` |
| Min length | `@Length(min, max)` | `Field(min_length=n)` | `#[validate(length(min = n))]` | `validate:"min=n"` |
| Max length | `@Length(min, max)` | `Field(max_length=n)` | `#[validate(length(max = n))]` | `validate:"max=n"` |
| Regex | `@Matches(regex)` | `Field(pattern=r'...')` | `#[validate(regex = "...")]` | `validate:"regexp=..."` |
| Email | `@IsEmail()` | `EmailStr` | `#[validate(email)]` | `validate:"email"` |
| URL | `@IsUrl()` | `HttpUrl` | `#[validate(url)]` | `validate:"url"` |

### Numeric Validation

| Validation | TypeScript | Python | Rust | Go |
|------------|------------|--------|------|-----|
| Min value | `@Min(n)` | `Field(ge=n)` | `#[validate(range(min = n))]` | `validate:"gte=n"` |
| Max value | `@Max(n)` | `Field(le=n)` | `#[validate(range(max = n))]` | `validate:"lte=n"` |
| Positive | `@IsPositive()` | `Field(gt=0)` | `#[validate(range(min = 1))]` | `validate:"gt=0"` |
| Negative | `@IsNegative()` | `Field(lt=0)` | `#[validate(range(max = -1))]` | `validate:"lt=0"` |

### Custom Validation

**TypeScript:**
```typescript
@ValidatorConstraint()
class IsAdultConstraint implements ValidatorConstraintInterface {
  validate(age: number) {
    return age >= 18;
  }
  defaultMessage() {
    return 'Must be 18 or older';
  }
}

@Validate(IsAdultConstraint)
age: number;
```

**Python (Pydantic):**
```python
@field_validator('age')
@classmethod
def must_be_adult(cls, v: int) -> int:
    if v < 18:
        raise ValueError('Must be 18 or older')
    return v
```

**Rust:**
```rust
fn validate_adult(age: &i32) -> Result<(), validator::ValidationError> {
    if *age < 18 {
        return Err(validator::ValidationError::new("must_be_adult"));
    }
    Ok(())
}

#[validate(custom(function = "validate_adult"))]
age: i32,
```

**Go:**
```go
func isAdult(fl validator.FieldLevel) bool {
    return fl.Field().Int() >= 18
}

validate.RegisterValidation("adult", isAdult)

type Person struct {
    Age int `validate:"adult"`
}
```

---

## Nested Object Handling

### TypeScript
```typescript
class Address {
  @IsString()
  street: string;
}

class User {
  @ValidateNested()
  @Type(() => Address)
  address: Address;

  @ValidateNested({ each: true })
  @Type(() => Address)
  addresses: Address[];
}
```

### Python
```python
class Address(BaseModel):
    street: str

class User(BaseModel):
    address: Address
    addresses: list[Address]
```

### Rust
```rust
#[derive(Serialize, Deserialize, Validate)]
struct Address {
    street: String,
}

#[derive(Serialize, Deserialize, Validate)]
struct User {
    #[validate(nested)]
    address: Address,

    #[validate(nested)]
    addresses: Vec<Address>,
}
```

### Go
```go
type Address struct {
    Street string `json:"street" validate:"required"`
}

type User struct {
    Address   Address   `json:"address" validate:"required"`
    Addresses []Address `json:"addresses" validate:"dive"`
}
```

---

## Default Values

| Language | Syntax | Example |
|----------|--------|---------|
| TypeScript | Property initializer | `status: string = 'pending'` |
| Python | `Field(default=...)` | `status: str = Field(default='pending')` |
| Rust | `#[serde(default)]` | `#[serde(default = "default_status")]` |
| Go | Not in struct tags | Manual in constructor |
| Java | Field initializer | `private String status = "pending";` |

**Rust default function:**
```rust
fn default_status() -> String {
    "pending".to_string()
}

#[derive(Deserialize)]
struct Order {
    #[serde(default = "default_status")]
    status: String,
}
```

---

## Library Mapping

### Serialization Libraries

| Category | TypeScript | Python | Rust | Go |
|----------|------------|--------|------|-----|
| JSON | Built-in | `json` | `serde_json` | `encoding/json` |
| YAML | `js-yaml` | `pyyaml` | `serde_yaml` | `gopkg.in/yaml.v3` |
| TOML | `@iarna/toml` | `tomli`/`tomllib` | `toml` | `github.com/BurntSushi/toml` |
| MessagePack | `@msgpack/msgpack` | `msgpack` | `rmp-serde` | `github.com/vmihailenco/msgpack` |

### Validation Libraries

| TypeScript | Python | Rust | Go | Java |
|------------|--------|------|-----|------|
| `class-validator` | Pydantic (built-in) | `validator` | `go-playground/validator` | Bean Validation |
| `zod` | `pydantic` | `garde` | `ozzo-validation` | Hibernate Validator |
| `yup` | `cerberus` | - | - | - |
| `joi` | `marshmallow` | - | - | - |

### Schema Generation

| TypeScript | Python | Rust | Go |
|------------|--------|------|-----|
| `typescript-json-schema` | `pydantic` (built-in) | `schemars` | `github.com/invopop/jsonschema` |
| `zod-to-json-schema` | `datamodel-code-generator` | - | - |

---

## Common Patterns

### Optional vs Required

```
TypeScript:  name?: string          → Optional
Python:      name: Optional[str]    → Optional
Rust:        name: Option<String>   → Optional
Go:          Name *string           → Optional (pointer)
```

### Date/Time Handling

| Language | Type | JSON Format | Custom Format |
|----------|------|-------------|---------------|
| TypeScript | `Date` | ISO string | `@Transform()` |
| Python | `datetime` | ISO string | `@field_serializer()` |
| Rust | `DateTime<Utc>` | ISO string | `#[serde(with = "...")]` |
| Go | `time.Time` | RFC3339 | Custom `MarshalJSON` |

### Enums

**TypeScript:**
```typescript
enum Status { Pending = 'pending', Active = 'active' }

class Order {
  @IsEnum(Status)
  status: Status;
}
```

**Python:**
```python
from enum import Enum

class Status(str, Enum):
    pending = 'pending'
    active = 'active'

class Order(BaseModel):
    status: Status
```

**Rust:**
```rust
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
enum Status {
    Pending,
    Active,
}
```

**Go:**
```go
type Status string

const (
    StatusPending Status = "pending"
    StatusActive  Status = "active"
)
```

---

## Anti-Patterns

### 1. Mixing Validation and Business Logic

```python
# ❌ Business logic in validator
@field_validator('age')
def check_age(cls, v):
    if v < 18:
        send_notification("underage user attempted")  # Side effect!
        raise ValueError('underage')
    return v

# ✓ Separate concerns
@field_validator('age')
def check_age(cls, v):
    if v < 18:
        raise ValueError('underage')
    return v

# Business logic elsewhere
if not user.is_adult():
    send_notification(...)
```

### 2. Over-validation

```python
# ❌ Validating internal types
class InternalData(BaseModel):
    # This is only used internally, no need for extensive validation
    temp_id: str = Field(regex=r'^[a-f0-9]{32}$')

# ✓ Validate at boundaries only
class UserInput(BaseModel):  # External input
    email: EmailStr  # Validate here

class InternalData:  # Internal use
    temp_id: str  # Trust internal code
```

### 3. Ignoring Serialization Errors

```go
// ❌ Ignoring errors
json.Unmarshal(data, &user)  // Error ignored!

// ✓ Handle errors
if err := json.Unmarshal(data, &user); err != nil {
    return fmt.Errorf("invalid user data: %w", err)
}
```

---

## Best Practices

1. **Validate at boundaries** - Only validate external input, trust internal types
2. **Use schema-first** when possible for API contracts
3. **Prefer declarative** over imperative validation
4. **Keep serialization pure** - No side effects in serializers
5. **Document format expectations** in struct/class comments
6. **Test edge cases** - Empty strings, nulls, malformed dates
7. **Version your schemas** for backward compatibility

---

## Related Skills

- `meta-convert-dev` - Code conversion patterns
- `patterns-metaprogramming-dev` - Decorators/macros used for serialization
- `lang-*-dev` skills - Language-specific serialization details
