# Metaprogramming Examples

Code examples showing metaprogramming pattern translation between languages.

---

## Decorator → Attribute Translation

### TypeScript Decorators → Rust Attributes

```typescript
// TypeScript: Decorators (class/method/property)
@Controller("/users")
class UserController {
  @Get("/:id")
  @Authenticate
  async getUser(@Param("id") id: string): Promise<User> {
    return this.userService.find(id);
  }
}
```

```rust
// Rust: Attributes + Proc Macros (axum style)
#[derive(Clone)]
struct UserController {
    user_service: Arc<UserService>,
}

impl UserController {
    async fn get_user(
        State(controller): State<Self>,
        Path(id): Path<String>,
        _auth: AuthenticatedUser,  // extractor handles auth
    ) -> Result<Json<User>, AppError> {
        let user = controller.user_service.find(&id).await?;
        Ok(Json(user))
    }
}

// Router setup
let app = Router::new()
    .route("/users/:id", get(UserController::get_user))
    .with_state(controller);
```

### TypeScript → Python

```typescript
// TypeScript: Method decorator
function Log(target: any, key: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${key} with`, args);
    return original.apply(this, args);
  };
}

class Service {
  @Log
  process(data: string): string {
    return data.toUpperCase();
  }
}
```

```python
# Python: Decorator function
from functools import wraps

def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with {args}, {kwargs}")
        return func(*args, **kwargs)
    return wrapper

class Service:
    @log
    def process(self, data: str) -> str:
        return data.upper()
```

### TypeScript → Go

```typescript
// TypeScript: Decorator for metadata
@Controller("/users")
class UserController {
  @Get("/:id")
  getUser(@Param("id") id: string): User {
    // ...
  }
}
```

```go
// Go: No decorators - use struct tags + code generation
// go:generate annotations or explicit registration

type UserController struct{}

type GetUserRequest struct {
    ID string `path:"id" validate:"required"`
}

func (c *UserController) GetUser(ctx context.Context, req GetUserRequest) (*User, error) {
    return c.userService.Find(ctx, req.ID)
}

// Manual route registration
func RegisterRoutes(r *mux.Router, c *UserController) {
    r.HandleFunc("/users/{id}", c.handleGetUser).Methods("GET")
}
```

---

## Macro Translation

### Clojure Macro → Rust Macro

```clojure
;; Clojure: Macro for compile-time transformation
(defmacro unless [pred & body]
  `(if (not ~pred)
     (do ~@body)))

(unless (empty? items)
  (process items))
```

```rust
// Rust: Declarative macro equivalent
macro_rules! unless {
    ($pred:expr, $body:block) => {
        if !$pred $body
    };
}

unless!(items.is_empty(), {
    process(&items);
});
```

### Elixir Macro → Rust Macro

```elixir
# Elixir: Hygienic macro
defmacro unless(pred, do: body) do
  quote do
    if !unquote(pred), do: unquote(body)
  end
end

unless Enum.empty?(items) do
  process(items)
end
```

```rust
// Rust: Declarative macro (hygienic by default)
macro_rules! unless {
    ($pred:expr, $body:expr) => {
        if !$pred { $body }
    };
}

unless!(items.is_empty(), process(&items));
```

---

## Mixin / Trait Composition

### TypeScript Mixin → Rust Derive

```typescript
// TypeScript: Mixin pattern
type Constructor<T = {}> = new (...args: any[]) => T;

function Timestamped<TBase extends Constructor>(Base: TBase) {
  return class extends Base {
    createdAt = new Date();
    updatedAt = new Date();
  };
}

class User extends Timestamped(BaseModel) {
  name: string;
}
```

```rust
// Rust: Trait + derive macro
use chrono::{DateTime, Utc};

// Define trait
trait Timestamped {
    fn created_at(&self) -> DateTime<Utc>;
    fn updated_at(&self) -> DateTime<Utc>;
}

// Derive macro (would be defined in proc macro crate)
#[derive(Timestamped)]
struct User {
    name: String,
    // created_at and updated_at added by derive macro
}

// Or manual implementation with composition
struct User {
    name: String,
    timestamps: Timestamps,
}

struct Timestamps {
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}
```

### Python Mixin → Rust Trait

```python
# Python: Multiple inheritance (mixin classes)
class TimestampedMixin:
    created_at: datetime
    updated_at: datetime

    def touch(self):
        self.updated_at = datetime.now()

class AuditableMixin:
    created_by: str
    updated_by: str

class User(TimestampedMixin, AuditableMixin, BaseModel):
    name: str
```

```rust
// Rust: Multiple trait implementations
trait Timestamped {
    fn created_at(&self) -> DateTime<Utc>;
    fn updated_at(&self) -> DateTime<Utc>;
    fn touch(&mut self);
}

trait Auditable {
    fn created_by(&self) -> &str;
    fn updated_by(&self) -> &str;
}

struct User {
    name: String,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
    created_by: String,
    updated_by: String,
}

impl Timestamped for User {
    fn created_at(&self) -> DateTime<Utc> { self.created_at }
    fn updated_at(&self) -> DateTime<Utc> { self.updated_at }
    fn touch(&mut self) { self.updated_at = Utc::now(); }
}

impl Auditable for User {
    fn created_by(&self) -> &str { &self.created_by }
    fn updated_by(&self) -> &str { &self.updated_by }
}
```

---

## Dependency Injection

### TypeScript DI → Rust Constructor Injection

```typescript
// TypeScript: Decorator-based DI (NestJS style)
@Injectable()
class UserService {
  constructor(
    @Inject("DATABASE") private db: Database,
    private logger: Logger,
  ) {}

  async findUser(id: string): Promise<User> {
    this.logger.info(`Finding user ${id}`);
    return this.db.query("SELECT * FROM users WHERE id = ?", [id]);
  }
}

// Module configuration
@Module({
  providers: [
    UserService,
    { provide: "DATABASE", useClass: PostgresDatabase },
    Logger,
  ],
})
class UserModule {}
```

```rust
// Rust: Constructor injection (no runtime DI)
struct UserService {
    db: Arc<dyn Database>,
    logger: Arc<dyn Logger>,
}

impl UserService {
    fn new(db: Arc<dyn Database>, logger: Arc<dyn Logger>) -> Self {
        Self { db, logger }
    }

    async fn find_user(&self, id: &str) -> Result<User, Error> {
        self.logger.info(&format!("Finding user {}", id));
        self.db.query("SELECT * FROM users WHERE id = ?", &[id]).await
    }
}

// Composition root (main.rs or similar)
fn create_services() -> UserService {
    let db: Arc<dyn Database> = Arc::new(PostgresDatabase::new());
    let logger: Arc<dyn Logger> = Arc::new(ConsoleLogger::new());
    UserService::new(db, logger)
}
```

### TypeScript DI → Go Interface Injection

```typescript
// TypeScript: Interface-based DI
interface Logger {
  info(msg: string): void;
}

@Injectable()
class UserService {
  constructor(private logger: Logger) {}
}
```

```go
// Go: Interface-based DI (idiomatic)
type Logger interface {
    Info(msg string)
}

type UserService struct {
    logger Logger
}

func NewUserService(logger Logger) *UserService {
    return &UserService{logger: logger}
}

func (s *UserService) FindUser(id string) (*User, error) {
    s.logger.Info(fmt.Sprintf("Finding user %s", id))
    // ...
}

// Wire up in main
func main() {
    logger := NewConsoleLogger()
    userService := NewUserService(logger)
    // ...
}
```

---

## Reflection

### Python Reflection → Rust Alternatives

```python
# Python: Dynamic attribute access
class Config:
    host: str = "localhost"
    port: int = 8080

def get_field(obj, name: str):
    return getattr(obj, name)

def set_field(obj, name: str, value):
    setattr(obj, name, value)

def list_fields(obj):
    return [k for k in dir(obj) if not k.startswith('_')]
```

```rust
// Rust: No runtime reflection - use macros or traits

// Option 1: Enum for known fields
enum ConfigField {
    Host,
    Port,
}

impl Config {
    fn get_field(&self, field: ConfigField) -> String {
        match field {
            ConfigField::Host => self.host.clone(),
            ConfigField::Port => self.port.to_string(),
        }
    }
}

// Option 2: Derive macro for reflection-like behavior
// (using serde as example)
#[derive(Serialize, Deserialize)]
struct Config {
    host: String,
    port: u16,
}

// Access fields via serialization
let json = serde_json::to_value(&config)?;
let host = json.get("host");

// Option 3: Trait for known behavior
trait Configurable {
    fn get(&self, key: &str) -> Option<String>;
    fn set(&mut self, key: &str, value: &str) -> Result<(), Error>;
    fn fields(&self) -> Vec<&str>;
}
```

### TypeScript Reflection → Go Struct Tags

```typescript
// TypeScript: Reflect metadata
import "reflect-metadata";

class User {
  @Column("varchar")
  name: string;

  @Column("int")
  age: number;
}

// Read metadata
const columns = Reflect.getMetadata("columns", User);
```

```go
// Go: Struct tags + reflect package
type User struct {
    Name string `db:"name" type:"varchar"`
    Age  int    `db:"age" type:"int"`
}

func GetColumns(v interface{}) map[string]string {
    columns := make(map[string]string)
    t := reflect.TypeOf(v)
    for i := 0; i < t.NumField(); i++ {
        field := t.Field(i)
        dbName := field.Tag.Get("db")
        dbType := field.Tag.Get("type")
        if dbName != "" {
            columns[dbName] = dbType
        }
    }
    return columns
}
```

---

## Code Generation

### Runtime Code Gen → Compile-Time

```python
# Python: Runtime class creation
def create_model(name: str, fields: dict):
    return type(name, (), fields)

User = create_model('User', {
    'name': '',
    'age': 0,
    '__init__': lambda self, name, age: setattr(self, 'name', name) or setattr(self, 'age', age)
})
```

```rust
// Rust: Compile-time macro
macro_rules! create_model {
    ($name:ident { $($field:ident: $type:ty),* $(,)? }) => {
        #[derive(Debug, Default)]
        struct $name {
            $($field: $type),*
        }

        impl $name {
            fn new($($field: $type),*) -> Self {
                Self { $($field),* }
            }
        }
    };
}

create_model!(User {
    name: String,
    age: u32,
});

// Usage
let user = User::new("Alice".into(), 30);
```

```go
// Go: go generate + text templates
//go:generate go run gen.go

// gen.go creates model code at build time
// models_gen.go (generated):
type User struct {
    Name string
    Age  int
}

func NewUser(name string, age int) *User {
    return &User{Name: name, Age: age}
}
```
