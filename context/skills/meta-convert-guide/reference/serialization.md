# Serialization Reference

Comprehensive reference for serialization patterns across languages.

---

## Library Mapping

| Language   | JSON                          | Validation            | Schema Gen            | Binary                 |
| ---------- | ----------------------------- | --------------------- | --------------------- | ---------------------- |
| TypeScript | built-in, `class-transformer` | Zod, Joi, Yup         | TypeBox, Zod          | protobuf, msgpack      |
| Python     | `json` stdlib, Pydantic       | Pydantic, marshmallow | Pydantic, dataclasses | protobuf, msgpack      |
| Rust       | serde_json                    | validator crate       | schemars              | serde + bincode, rmp   |
| Go         | `encoding/json`               | validator, ozzo       | go-jsonschema         | protobuf, gob          |
| Elixir     | Jason, Poison                 | Ecto changesets       | -                     | :erlang.term_to_binary |
| Clojure    | cheshire, jsonista            | spec, malli           | spec                  | nippy, transit         |
| Haskell    | aeson                         | -                     | -                     | binary, cereal         |

---

## Attribute / Annotation Mapping

### Field Renaming

| Language   | Pattern                    | Example                          |
| ---------- | -------------------------- | -------------------------------- |
| TypeScript | `@Expose({ name: "..." })` | `@Expose({ name: "full_name" })` |
| Python     | `Field(alias="...")`       | `Field(alias="fullName")`        |
| Rust       | `#[serde(rename = "...")]` | `#[serde(rename = "full_name")]` |
| Go         | Struct tag                 | `` `json:"full_name"` ``         |

### Field Exclusion

| Language   | Pattern               | Example                               |
| ---------- | --------------------- | ------------------------------------- |
| TypeScript | `@Exclude()`          | `@Exclude() password: string`         |
| Python     | `Field(exclude=True)` | `password: str = Field(exclude=True)` |
| Rust       | `#[serde(skip)]`      | `#[serde(skip)] password: String`     |
| Go         | Tag with `-`          | `` `json:"-"` ``                      |

### Default Values

| Language   | Pattern                    | Example                              |
| ---------- | -------------------------- | ------------------------------------ |
| TypeScript | Default in class           | `port: number = 8080`                |
| Python     | `Field(default=...)`       | `port: int = Field(default=8080)`    |
| Rust       | `#[serde(default = "fn")]` | `#[serde(default = "default_port")]` |
| Go         | Constructor                | Initialize in `NewConfig()`          |

---

## Validation Patterns

### Schema Definition Comparison

```typescript
// TypeScript: Zod
const UserSchema = z.object({
  email: z.string().email(),
  age: z.number().min(0).max(150),
  role: z.enum(["admin", "user", "guest"]),
});
```

```rust
// Rust: validator crate
#[derive(Validate, Deserialize)]
struct User {
    #[validate(email)]
    email: String,

    #[validate(range(min = 0, max = 150))]
    age: u8,

    role: Role,
}

#[derive(Deserialize)]
#[serde(rename_all = "lowercase")]
enum Role { Admin, User, Guest }
```

```python
# Python: Pydantic
from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class Role(str, Enum):
    admin = "admin"
    user = "user"
    guest = "guest"

class User(BaseModel):
    email: EmailStr
    age: int = Field(ge=0, le=150)
    role: Role
```

```go
// Go: validator
type User struct {
    Email string `json:"email" validate:"required,email"`
    Age   int    `json:"age" validate:"gte=0,lte=150"`
    Role  string `json:"role" validate:"oneof=admin user guest"`
}
```

---

## Polymorphic / Tagged Union

### Discriminated Union Pattern

```typescript
// TypeScript
type Shape =
  | { type: "circle"; radius: number }
  | { type: "rectangle"; width: number; height: number };
```

```rust
// Rust: serde tag
#[derive(Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
enum Shape {
    Circle { radius: f64 },
    Rectangle { width: f64, height: f64 },
}
```

```python
# Python: Pydantic discriminated union
from typing import Literal, Union, Annotated
from pydantic import BaseModel, Discriminator

class Circle(BaseModel):
    type: Literal["circle"] = "circle"
    radius: float

class Rectangle(BaseModel):
    type: Literal["rectangle"] = "rectangle"
    width: float
    height: float

Shape = Annotated[Union[Circle, Rectangle], Discriminator("type")]
```

---

## Custom Serializers

### Date/Time Handling

```typescript
// TypeScript: class-transformer
class Event {
  @Transform(({ value }) => new Date(value), { toClassOnly: true })
  @Transform(({ value }) => value.toISOString(), { toPlainOnly: true })
  timestamp: Date;
}
```

```rust
// Rust: serde custom module
mod iso_date {
    use chrono::{DateTime, Utc};
    use serde::{Deserialize, Deserializer, Serializer};

    pub fn serialize<S>(date: &DateTime<Utc>, s: S) -> Result<S::Ok, S::Error>
    where S: Serializer {
        s.serialize_str(&date.to_rfc3339())
    }

    pub fn deserialize<'de, D>(d: D) -> Result<DateTime<Utc>, D::Error>
    where D: Deserializer<'de> {
        let s = String::deserialize(d)?;
        DateTime::parse_from_rfc3339(&s)
            .map(|dt| dt.with_timezone(&Utc))
            .map_err(serde::de::Error::custom)
    }
}

#[derive(Serialize, Deserialize)]
struct Event {
    #[serde(with = "iso_date")]
    timestamp: DateTime<Utc>,
}
```

---

## Nested Objects

### Flat vs Nested

```rust
// Rust: Flatten nested fields
#[derive(Serialize, Deserialize)]
struct Config {
    name: String,
    #[serde(flatten)]
    settings: Settings,  // Fields merged into parent
}

#[derive(Serialize, Deserialize)]
struct Settings {
    timeout: u32,
    retries: u32,
}

// JSON: {"name": "test", "timeout": 30, "retries": 3}
```

### Optional Nested

```rust
#[derive(Serialize, Deserialize)]
struct User {
    name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    address: Option<Address>,  // Omitted if None
}
```

---

## Schema Versioning

### Migration Pattern

```rust
#[derive(Serialize, Deserialize)]
#[serde(tag = "version")]
enum UserRecord {
    #[serde(rename = "1")]
    V1(UserV1),
    #[serde(rename = "2")]
    V2(UserV2),
}

impl UserRecord {
    fn to_latest(self) -> UserV2 {
        match self {
            UserRecord::V1(v1) => v1.migrate(),
            UserRecord::V2(v2) => v2,
        }
    }
}
```

### Migration Strategies

| Strategy           | When to Use                          | Risk Level |
| ------------------ | ------------------------------------ | ---------- |
| Dual-write         | New field added, old readers exist   | Low        |
| Schema versioning  | Breaking changes needed              | Medium     |
| Envelope pattern   | Mixed versions in same system        | Medium     |
| Big-bang migration | All readers/writers updated together | High       |

---

## Performance Considerations

| Format           | Speed     | Size       | Human Readable |
| ---------------- | --------- | ---------- | -------------- |
| JSON             | Medium    | Large      | Yes            |
| MessagePack      | Fast      | Small      | No             |
| CBOR             | Fast      | Small      | No             |
| Protocol Buffers | Very Fast | Very Small | No             |
| Bincode (Rust)   | Very Fast | Small      | No             |

### Choosing a Format

- **JSON**: Default for APIs, debugging, configs
- **MessagePack/CBOR**: JSON-like but smaller/faster
- **Protocol Buffers**: Cross-language, schema-first
- **Bincode**: Rust-only, maximum speed
