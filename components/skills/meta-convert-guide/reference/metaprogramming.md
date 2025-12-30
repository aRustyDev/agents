# Metaprogramming Reference

Comprehensive reference for metaprogramming capabilities across languages.

---

## Capability Comparison

| Language   | Decorators                  | Macros                       | Reflection            | Code Gen              |
|------------|-----------------------------|------------------------------|-----------------------|-----------------------|
| Python     | `@decorator`                | No                           | `inspect`, `__dict__` | `ast`                 |
| TypeScript | `@decorator` (experimental) | No                           | Limited runtime       | Via build             |
| Rust       | `#[attr]`                   | `macro_rules!`, proc macros  | No                    | Proc macros           |
| Go         | No                          | No                           | `reflect` package     | `go generate`         |
| Elixir     | No                          | `defmacro` (hygienic)        | Runtime introspection | Macros                |
| Clojure    | No                          | `defmacro` (reader macros)   | Full (JVM)            | Macros                |
| Haskell    | No                          | Template Haskell             | Limited               | TH, generics          |
| Java       | `@annotation`               | No                           | Full runtime          | Annotation processors |
| Scala      | `@annotation`               | `macro` (deprecated), inline | Full (JVM)            | Macros                |

---

## Decorator / Attribute Translation

### Basic Translation

| Python/TS Pattern | Rust Pattern | Go Pattern |
|-------------------|--------------|------------|
| `@decorator` | `#[attribute]` | Struct tags + codegen |
| `@decorator(args)` | `#[attribute(args)]` | Struct tags |
| Class decorator | Derive macro | Type definition |
| Method decorator | Proc macro | Manual wrapper |

### Route Decorator Example

```typescript
// TypeScript (NestJS style)
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
// Rust (axum style)
#[derive(Clone)]
struct UserController { /* ... */ }

impl UserController {
    async fn get_user(
        State(ctrl): State<Self>,
        Path(id): Path<String>,
        _auth: AuthenticatedUser,  // Extractor handles auth
    ) -> Result<Json<User>, AppError> {
        let user = ctrl.user_service.find(&id).await?;
        Ok(Json(user))
    }
}

// Router
let app = Router::new()
    .route("/users/:id", get(UserController::get_user))
    .with_state(controller);
```

```go
// Go (gin style)
type UserController struct { /* ... */ }

func (c *UserController) GetUser(ctx *gin.Context) {
    id := ctx.Param("id")
    user, err := c.userService.Find(id)
    if err != nil {
        ctx.JSON(500, gin.H{"error": err.Error()})
        return
    }
    ctx.JSON(200, user)
}

// Router
r.GET("/users/:id", authMiddleware(), ctrl.GetUser)
```

---

## Macro Systems

### Macro Type Comparison

| Type | Language | Capabilities |
|------|----------|--------------|
| Text substitution | C | Simple replacement |
| Declarative | Rust `macro_rules!` | Pattern matching |
| Procedural | Rust proc macros | AST manipulation |
| Hygienic | Elixir, Rust | No accidental capture |
| Reader | Clojure | Syntax extension |
| Template | Haskell TH | Compile-time codegen |

### Declarative Macro Example

```clojure
;; Clojure
(defmacro unless [pred & body]
  `(if (not ~pred)
     (do ~@body)))
```

```rust
// Rust
macro_rules! unless {
    ($pred:expr, $body:block) => {
        if !$pred $body
    };
}
```

```elixir
# Elixir
defmacro unless(pred, do: body) do
  quote do
    if !unquote(pred), do: unquote(body)
  end
end
```

---

## Reflection Capabilities

| Capability       | Python                    | TypeScript          | Rust         | Go                        |
|------------------|---------------------------|---------------------|--------------|---------------------------|
| Get field names  | `dir()`, `__dict__`       | `Object.keys()`     | Derive macro | `reflect.TypeOf()`        |
| Get field values | `getattr()`               | Direct access       | No           | `reflect.ValueOf()`       |
| Set field values | `setattr()`               | Direct access       | No           | `reflect.Set()` (limited) |
| Call by name     | `getattr(obj, name)()`    | `obj[name]()`       | No           | `reflect.Method()`        |
| Create instance  | `type(name, bases, dict)` | `new Constructor()` | No           | `reflect.New()`           |

### Translation Strategies

| Reflection Use Case | Static Language Alternative |
|---------------------|----------------------------|
| Serialization | Derive macros, codegen |
| Dependency injection | Constructor injection |
| ORM mapping | Compile-time macros |
| Dynamic dispatch | Trait objects, enums |
| Configuration | Builder pattern |

---

## Dependency Injection Patterns

| Language    | DI Approach                   | Example                               |
|-------------|-------------------------------|---------------------------------------|
| TypeScript  | Class decorators + reflection | `@Injectable()`, Angular/NestJS       |
| Python      | Decorators + containers       | `@inject`, dependency-injector        |
| Rust        | Trait objects + constructors  | Manual DI, no runtime reflection      |
| Go          | Interface + constructors      | Wire (codegen), manual DI             |
| Java/Kotlin | Annotations + reflection      | Spring `@Autowired`, Dagger           |
| Elixir      | Module behaviours + config    | No DI framework (functional approach) |

### From Decorator DI to Manual DI

```typescript
// TypeScript: Decorator-based DI
@Injectable()
class UserService {
  constructor(
    @Inject("DATABASE") private db: Database,
    private logger: Logger,
  ) {}
}
```

```rust
// Rust: Constructor injection
struct UserService {
    db: Arc<dyn Database>,
    logger: Arc<dyn Logger>,
}

impl UserService {
    fn new(db: Arc<dyn Database>, logger: Arc<dyn Logger>) -> Self {
        Self { db, logger }
    }
}

// Composition root
fn create_services() -> UserService {
    let db: Arc<dyn Database> = Arc::new(PostgresDatabase::new());
    let logger: Arc<dyn Logger> = Arc::new(ConsoleLogger::new());
    UserService::new(db, logger)
}
```

---

## Code Generation

### Build-Time vs Runtime

| Approach | Languages | When |
|----------|-----------|------|
| Compile-time macros | Rust, Elixir, Clojure | Compilation |
| Annotation processors | Java, Kotlin | Compilation |
| go generate | Go | Before compilation |
| Runtime reflection | Python, JS, Java | Runtime |

### Go Generate Pattern

```go
//go:generate stringer -type=Color

type Color int

const (
    Red Color = iota
    Green
    Blue
)
```

### Rust Derive Macro

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
struct User {
    name: String,
    age: u32,
}
// Generates impl blocks at compile time
```

---

## Mixin / Trait Composition

| Language | Pattern | Example |
|----------|---------|---------|
| Python | Multiple inheritance | `class C(A, B)` |
| Ruby | Module include | `include ModuleName` |
| TypeScript | Mixin function | `class extends Mixin(Base)` |
| Rust | Multiple impl | `impl TraitA for T`, `impl TraitB for T` |
| Go | Embedding | `type C struct { A; B }` |
| Scala | Trait mixing | `class C extends A with B` |

### Translation Example

```typescript
// TypeScript: Mixin
function Timestamped<T extends Constructor>(Base: T) {
  return class extends Base {
    createdAt = new Date();
  };
}

class User extends Timestamped(BaseModel) {}
```

```rust
// Rust: Trait + derive (or manual impl)
trait Timestamped {
    fn created_at(&self) -> DateTime<Utc>;
}

// Via derive macro or manual impl
impl Timestamped for User {
    fn created_at(&self) -> DateTime<Utc> {
        self.created_at
    }
}
```

---

## Converting FROM Reflection-Heavy Code

1. **Identify what reflection achieves**
   - Serialization → Use serde/codegen
   - DI → Use constructor injection
   - ORM → Use compile-time macros

2. **Use compile-time alternatives**
   - Macros for boilerplate
   - Generics for type flexibility
   - Traits for polymorphism

3. **Accept limitations**
   - Some dynamic patterns can't translate
   - May need architecture changes

---

## Converting TO Reflection-Capable

1. **Consider if reflection is idiomatic**
   - Often there are better patterns
   - Reflection can be slow

2. **Prefer static approaches**
   - Better type safety
   - Faster execution
   - Easier to reason about
