# Serialization Examples

Code examples showing serialization pattern translation between languages.

---

## Basic JSON Serialization

### TypeScript → Multiple Languages

```typescript
// TypeScript: class-transformer decorators
import { Expose, Exclude, Transform, Type } from "class-transformer";

class User {
  @Expose()
  id: string;

  @Expose({ name: "full_name" })
  fullName: string;

  @Type(() => Date)
  @Transform(({ value }) => new Date(value))
  createdAt: Date;

  @Exclude()
  password: string;
}
```

```rust
// Rust: serde attributes
use serde::{Serialize, Deserialize};
use chrono::{DateTime, Utc};

#[derive(Serialize, Deserialize)]
struct User {
    id: String,

    #[serde(rename = "full_name")]
    full_name: String,

    #[serde(with = "chrono::serde::ts_seconds")]
    created_at: DateTime<Utc>,

    #[serde(skip)]
    password: String,
}
```

```python
# Python: Pydantic with field configuration
from pydantic import BaseModel, Field
from datetime import datetime

class User(BaseModel):
    id: str
    full_name: str = Field(alias="fullName")
    created_at: datetime
    password: str = Field(exclude=True)

    class Config:
        populate_by_name = True
```

```go
// Go: struct tags
type User struct {
    ID        string    `json:"id"`
    FullName  string    `json:"full_name"`
    CreatedAt time.Time `json:"created_at"`
    Password  string    `json:"-"`  // excluded
}
```

```elixir
# Elixir: Jason with derived encoder
defmodule User do
  @derive {Jason.Encoder, only: [:id, :full_name, :created_at]}
  defstruct [:id, :full_name, :created_at, :password]
end

# Or with custom encoding
defimpl Jason.Encoder, for: User do
  def encode(%User{} = user, opts) do
    Jason.Encode.map(%{
      id: user.id,
      full_name: user.full_name,
      created_at: DateTime.to_iso8601(user.created_at)
    }, opts)
  end
end
```

---

## Validation

### TypeScript Zod → Rust validator

```typescript
// TypeScript: Zod schema
import { z } from "zod";

const UserSchema = z.object({
  email: z.string().email(),
  age: z.number().min(0).max(150),
  role: z.enum(["admin", "user", "guest"]),
});

type User = z.infer<typeof UserSchema>;

// Validation
const result = UserSchema.safeParse(input);
if (result.success) {
  const user = result.data;
} else {
  console.error(result.error);
}
```

```rust
// Rust: validator crate
use validator::Validate;
use serde::Deserialize;

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
enum Role {
    Admin,
    User,
    Guest,
}

// Validation
fn validate_user(input: &str) -> Result<User, Error> {
    let user: User = serde_json::from_str(input)?;
    user.validate()?;
    Ok(user)
}
```

### TypeScript Zod → Python Pydantic

```typescript
// TypeScript: Zod with custom validation
const OrderSchema = z.object({
  items: z.array(z.string()).min(1, "At least one item required"),
  total: z.number().positive(),
  discount: z.number().min(0).max(100).optional(),
});
```

```python
# Python: Pydantic with validators
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class Order(BaseModel):
    items: list[str] = Field(min_length=1)
    total: float = Field(gt=0)
    discount: Optional[float] = Field(default=None, ge=0, le=100)

    @field_validator('items')
    @classmethod
    def items_not_empty(cls, v):
        if not v:
            raise ValueError('At least one item required')
        return v
```

---

## Polymorphic / Tagged Union

### TypeScript Discriminated Union → Rust Tagged Enum

```typescript
// TypeScript: Discriminated union
type Shape =
  | { type: "circle"; radius: number }
  | { type: "rectangle"; width: number; height: number }
  | { type: "triangle"; base: number; height: number };

// Serializes as: {"type": "circle", "radius": 5}
```

```rust
// Rust: Tagged enum (serde)
#[derive(Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
enum Shape {
    Circle { radius: f64 },
    Rectangle { width: f64, height: f64 },
    Triangle { base: f64, height: f64 },
}

// Serializes as: {"type": "circle", "radius": 5}
```

```python
# Python: Pydantic with discriminator
from pydantic import BaseModel, Field
from typing import Literal, Union

class Circle(BaseModel):
    type: Literal["circle"] = "circle"
    radius: float

class Rectangle(BaseModel):
    type: Literal["rectangle"] = "rectangle"
    width: float
    height: float

class Triangle(BaseModel):
    type: Literal["triangle"] = "triangle"
    base: float
    height: float

Shape = Union[Circle, Rectangle, Triangle]

# Or with discriminated union (Pydantic v2)
from pydantic import Discriminator

Shape = Annotated[
    Union[Circle, Rectangle, Triangle],
    Discriminator("type")
]
```

```go
// Go: Interface with type field
type Shape interface {
    ShapeType() string
}

type Circle struct {
    Type   string  `json:"type"`
    Radius float64 `json:"radius"`
}
func (c Circle) ShapeType() string { return "circle" }

type Rectangle struct {
    Type   string  `json:"type"`
    Width  float64 `json:"width"`
    Height float64 `json:"height"`
}
func (r Rectangle) ShapeType() string { return "rectangle" }

// Custom unmarshaling needed for polymorphic JSON
func UnmarshalShape(data []byte) (Shape, error) {
    var raw struct { Type string `json:"type"` }
    json.Unmarshal(data, &raw)

    switch raw.Type {
    case "circle":
        var c Circle
        err := json.Unmarshal(data, &c)
        return c, err
    case "rectangle":
        var r Rectangle
        err := json.Unmarshal(data, &r)
        return r, err
    default:
        return nil, errors.New("unknown shape type")
    }
}
```

---

## Custom Serializers

### TypeScript Custom Transformer → Rust Serde

```typescript
// TypeScript: Custom transformer
class DateTransformer implements ValueTransformer {
  to(value: Date): string {
    return value.toISOString();
  }
  from(value: string): Date {
    return new Date(value);
  }
}

class Event {
  @Transform(({ value }) => new Date(value), { toClassOnly: true })
  @Transform(({ value }) => value.toISOString(), { toPlainOnly: true })
  timestamp: Date;
}
```

```rust
// Rust: Custom serde serializer
mod iso_date {
    use chrono::{DateTime, Utc};
    use serde::{self, Deserialize, Deserializer, Serializer};

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

## Optional / Default Fields

```typescript
// TypeScript: Optional with defaults
interface Config {
  host: string;
  port?: number; // Optional
  timeout?: number;
}

const defaults: Config = {
  host: "localhost",
  port: 8080,
  timeout: 30,
};

function loadConfig(input: Partial<Config>): Config {
  return { ...defaults, ...input };
}
```

```rust
// Rust: serde defaults
#[derive(Serialize, Deserialize)]
struct Config {
    host: String,

    #[serde(default = "default_port")]
    port: u16,

    #[serde(default)]  // Uses Default::default() -> 0
    timeout: u32,
}

fn default_port() -> u16 { 8080 }

// Or with Default derive
#[derive(Serialize, Deserialize, Default)]
#[serde(default)]  // Use defaults for all missing fields
struct Config {
    #[serde(default = "default_host")]
    host: String,
    #[serde(default = "default_port")]
    port: u16,
    timeout: u32,  // defaults to 0
}
```

```python
# Python: Pydantic defaults
from pydantic import BaseModel

class Config(BaseModel):
    host: str = "localhost"
    port: int = 8080
    timeout: int = 30
```

```go
// Go: Defaults via constructor or post-unmarshal
type Config struct {
    Host    string `json:"host"`
    Port    int    `json:"port"`
    Timeout int    `json:"timeout"`
}

func NewConfig() Config {
    return Config{
        Host:    "localhost",
        Port:    8080,
        Timeout: 30,
    }
}

func LoadConfig(data []byte) (Config, error) {
    config := NewConfig()  // Start with defaults
    err := json.Unmarshal(data, &config)  // Override with provided values
    return config, err
}
```

---

## Nested Objects

```typescript
// TypeScript: Nested types
interface Address {
  street: string;
  city: string;
  country: string;
}

interface User {
  name: string;
  address: Address;
  tags: string[];
}
```

```rust
// Rust: Nested structs
#[derive(Serialize, Deserialize)]
struct Address {
    street: String,
    city: String,
    country: String,
}

#[derive(Serialize, Deserialize)]
struct User {
    name: String,
    address: Address,
    tags: Vec<String>,
}
```

```python
# Python: Nested models
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    country: str

class User(BaseModel):
    name: str
    address: Address
    tags: list[str]
```

---

## Schema Versioning

```typescript
// TypeScript: Version handling
interface UserV1 {
  version: 1;
  name: string;
}

interface UserV2 {
  version: 2;
  firstName: string;
  lastName: string;
}

type User = UserV1 | UserV2;

function migrateToLatest(user: User): UserV2 {
  if (user.version === 1) {
    const [firstName, ...rest] = user.name.split(" ");
    return {
      version: 2,
      firstName,
      lastName: rest.join(" "),
    };
  }
  return user;
}
```

```rust
// Rust: Versioned schema pattern
#[derive(Serialize, Deserialize)]
#[serde(tag = "version")]
enum UserRecord {
    #[serde(rename = "1")]
    V1(UserV1),
    #[serde(rename = "2")]
    V2(UserV2),
}

#[derive(Serialize, Deserialize)]
struct UserV1 {
    name: String,
}

#[derive(Serialize, Deserialize)]
struct UserV2 {
    first_name: String,
    last_name: String,
}

impl UserRecord {
    fn to_latest(self) -> UserV2 {
        match self {
            UserRecord::V1(v1) => {
                let parts: Vec<&str> = v1.name.splitn(2, ' ').collect();
                UserV2 {
                    first_name: parts.get(0).unwrap_or(&"").to_string(),
                    last_name: parts.get(1).unwrap_or(&"").to_string(),
                }
            }
            UserRecord::V2(v2) => v2,
        }
    }
}
```
