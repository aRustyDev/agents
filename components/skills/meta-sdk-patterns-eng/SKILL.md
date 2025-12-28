---
name: meta-sdk-patterns-eng
description: Foundational SDK development patterns that domain-specific SDK skills extend. Use when building SDKs for APIs or specifications, creating SDK development skills, or establishing SDK architecture standards across languages.
---

# SDK Development Patterns

Foundational patterns for building SDKs across languages and domains. This skill serves as:
1. **Root patterns** that domain-specific SDK skills (like `openfeature-sdk-dev`) extend
2. **Template** for creating new SDK development skills

## When to Use This Skill

- Building SDKs that wrap APIs, specifications, or services
- Establishing SDK architecture patterns for a team/organization
- Creating domain-specific SDK development skills
- Reviewing SDK design decisions
- Understanding cross-language SDK patterns

---

# Part 1: SDK Development Fundamentals

## SDK Architecture Patterns

### Client Structure

SDKs typically expose a central client object that encapsulates configuration, authentication, and API access.

#### Singleton Pattern

Use when global state is required or resource-intensive initialization.

```typescript
// TypeScript
class ApiClient {
  private static instance: ApiClient;
  private constructor(private config: Config) {}

  static getInstance(config?: Config): ApiClient {
    if (!ApiClient.instance) {
      if (!config) throw new Error('Config required for initialization');
      ApiClient.instance = new ApiClient(config);
    }
    return ApiClient.instance;
  }
}
```

```python
# Python
class ApiClient:
    _instance = None

    def __new__(cls, config=None):
        if cls._instance is None:
            if config is None:
                raise ValueError("Config required for initialization")
            cls._instance = super().__new__(cls)
            cls._instance._config = config
        return cls._instance
```

```go
// Go
var (
    instance *Client
    once     sync.Once
)

func GetClient(cfg *Config) *Client {
    once.Do(func() {
        instance = &Client{config: cfg}
    })
    return instance
}
```

```rust
// Rust
use once_cell::sync::OnceCell;

static CLIENT: OnceCell<Client> = OnceCell::new();

pub fn get_client() -> &'static Client {
    CLIENT.get().expect("Client not initialized")
}

pub fn init_client(config: Config) -> Result<(), ClientError> {
    CLIENT.set(Client::new(config))
        .map_err(|_| ClientError::AlreadyInitialized)
}
```

```kotlin
// Kotlin
object ApiClient {
    private lateinit var config: Config

    fun initialize(config: Config) {
        this.config = config
    }

    fun getInstance(): ApiClient {
        check(::config.isInitialized) { "Client not initialized" }
        return this
    }
}
```

```swift
// Swift
class ApiClient {
    static let shared = ApiClient()
    private var config: Config?

    private init() {}

    func configure(_ config: Config) {
        self.config = config
    }
}
```

```objc
// Objective-C
@implementation ApiClient

+ (instancetype)sharedClient {
    static ApiClient *sharedClient = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        sharedClient = [[self alloc] init];
    });
    return sharedClient;
}

@end
```

#### Instance Pattern

Use when multiple configurations are needed or for better testability.

```typescript
// TypeScript
class ApiClient {
  constructor(private config: Config) {}

  static create(config: Config): ApiClient {
    return new ApiClient(config);
  }
}

// Usage
const prodClient = ApiClient.create(prodConfig);
const testClient = ApiClient.create(testConfig);
```

```python
# Python
class ApiClient:
    def __init__(self, config: Config):
        self._config = config

    @classmethod
    def create(cls, config: Config) -> 'ApiClient':
        return cls(config)
```

```go
// Go
type Client struct {
    config *Config
    http   *http.Client
}

func NewClient(cfg *Config) *Client {
    return &Client{
        config: cfg,
        http:   &http.Client{Timeout: cfg.Timeout},
    }
}
```

```rust
// Rust
pub struct Client {
    config: Config,
    http: reqwest::Client,
}

impl Client {
    pub fn new(config: Config) -> Self {
        Self {
            http: reqwest::Client::builder()
                .timeout(config.timeout)
                .build()
                .unwrap(),
            config,
        }
    }
}
```

```kotlin
// Kotlin
class ApiClient private constructor(
    private val config: Config
) {
    companion object {
        fun create(config: Config): ApiClient = ApiClient(config)
    }
}
```

```swift
// Swift
class ApiClient {
    private let config: Config

    init(config: Config) {
        self.config = config
    }
}
```

```objc
// Objective-C
@implementation ApiClient

- (instancetype)initWithConfig:(Config *)config {
    self = [super init];
    if (self) {
        _config = config;
    }
    return self;
}

@end
```

### Builder Pattern

Use for complex configuration with many optional parameters.

```typescript
// TypeScript
class ClientBuilder {
  private config: Partial<Config> = {};

  withBaseUrl(url: string): this {
    this.config.baseUrl = url;
    return this;
  }

  withTimeout(ms: number): this {
    this.config.timeout = ms;
    return this;
  }

  withRetries(count: number): this {
    this.config.retries = count;
    return this;
  }

  build(): ApiClient {
    if (!this.config.baseUrl) {
      throw new Error('baseUrl is required');
    }
    return new ApiClient(this.config as Config);
  }
}

// Usage
const client = new ClientBuilder()
  .withBaseUrl('https://api.example.com')
  .withTimeout(5000)
  .withRetries(3)
  .build();
```

```python
# Python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ClientBuilder:
    _base_url: Optional[str] = None
    _timeout: int = 30000
    _retries: int = 0

    def with_base_url(self, url: str) -> 'ClientBuilder':
        self._base_url = url
        return self

    def with_timeout(self, ms: int) -> 'ClientBuilder':
        self._timeout = ms
        return self

    def with_retries(self, count: int) -> 'ClientBuilder':
        self._retries = count
        return self

    def build(self) -> 'ApiClient':
        if not self._base_url:
            raise ValueError("base_url is required")
        return ApiClient(Config(
            base_url=self._base_url,
            timeout=self._timeout,
            retries=self._retries
        ))
```

```go
// Go - Functional Options Pattern (idiomatic)
type Option func(*Client)

func WithTimeout(d time.Duration) Option {
    return func(c *Client) {
        c.timeout = d
    }
}

func WithRetries(n int) Option {
    return func(c *Client) {
        c.retries = n
    }
}

func NewClient(baseURL string, opts ...Option) *Client {
    c := &Client{
        baseURL: baseURL,
        timeout: 30 * time.Second,
        retries: 0,
    }
    for _, opt := range opts {
        opt(c)
    }
    return c
}

// Usage
client := NewClient("https://api.example.com",
    WithTimeout(5*time.Second),
    WithRetries(3),
)
```

```rust
// Rust - Builder with typestate
pub struct ClientBuilder<S = NoUrl> {
    base_url: Option<String>,
    timeout: Duration,
    retries: u32,
    _state: std::marker::PhantomData<S>,
}

pub struct NoUrl;
pub struct HasUrl;

impl ClientBuilder<NoUrl> {
    pub fn new() -> Self {
        Self {
            base_url: None,
            timeout: Duration::from_secs(30),
            retries: 0,
            _state: std::marker::PhantomData,
        }
    }

    pub fn base_url(self, url: impl Into<String>) -> ClientBuilder<HasUrl> {
        ClientBuilder {
            base_url: Some(url.into()),
            timeout: self.timeout,
            retries: self.retries,
            _state: std::marker::PhantomData,
        }
    }
}

impl ClientBuilder<HasUrl> {
    pub fn timeout(mut self, duration: Duration) -> Self {
        self.timeout = duration;
        self
    }

    pub fn retries(mut self, count: u32) -> Self {
        self.retries = count;
        self
    }

    pub fn build(self) -> Client {
        Client {
            base_url: self.base_url.unwrap(),
            timeout: self.timeout,
            retries: self.retries,
        }
    }
}
```

```kotlin
// Kotlin - DSL Builder
class ClientBuilder {
    var baseUrl: String? = null
    var timeout: Long = 30000
    var retries: Int = 0

    fun build(): ApiClient {
        requireNotNull(baseUrl) { "baseUrl is required" }
        return ApiClient(Config(baseUrl!!, timeout, retries))
    }
}

fun apiClient(block: ClientBuilder.() -> Unit): ApiClient {
    return ClientBuilder().apply(block).build()
}

// Usage
val client = apiClient {
    baseUrl = "https://api.example.com"
    timeout = 5000
    retries = 3
}
```

```swift
// Swift
class ClientBuilder {
    private var baseUrl: String?
    private var timeout: TimeInterval = 30
    private var retries: Int = 0

    func withBaseUrl(_ url: String) -> ClientBuilder {
        self.baseUrl = url
        return self
    }

    func withTimeout(_ seconds: TimeInterval) -> ClientBuilder {
        self.timeout = seconds
        return self
    }

    func withRetries(_ count: Int) -> ClientBuilder {
        self.retries = count
        return self
    }

    func build() throws -> ApiClient {
        guard let baseUrl = baseUrl else {
            throw ClientError.missingBaseUrl
        }
        return ApiClient(config: Config(
            baseUrl: baseUrl,
            timeout: timeout,
            retries: retries
        ))
    }
}
```

```objc
// Objective-C
@interface ClientBuilder : NSObject

@property (nonatomic, copy) NSString *baseURL;
@property (nonatomic, assign) NSTimeInterval timeout;
@property (nonatomic, assign) NSInteger retries;

- (instancetype)withBaseURL:(NSString *)url;
- (instancetype)withTimeout:(NSTimeInterval)timeout;
- (instancetype)withRetries:(NSInteger)retries;
- (ApiClient *)build;

@end

@implementation ClientBuilder

- (instancetype)init {
    self = [super init];
    if (self) {
        _timeout = 30.0;
        _retries = 0;
    }
    return self;
}

- (instancetype)withBaseURL:(NSString *)url {
    self.baseURL = url;
    return self;
}

- (ApiClient *)build {
    NSAssert(self.baseURL != nil, @"baseURL is required");
    return [[ApiClient alloc] initWithConfig:
        [[Config alloc] initWithBaseURL:self.baseURL
                                timeout:self.timeout
                                retries:self.retries]];
}

@end
```

## API Design Principles

### Resource-Oriented Design

Follow Google's API design patterns with standard methods:

| Method | HTTP | Description |
|--------|------|-------------|
| List | GET /resources | List collection |
| Get | GET /resources/{id} | Get single resource |
| Create | POST /resources | Create new resource |
| Update | PUT/PATCH /resources/{id} | Update existing |
| Delete | DELETE /resources/{id} | Delete resource |

```typescript
// TypeScript - Resource pattern
interface Resource<T> {
  list(options?: ListOptions): Promise<Page<T>>;
  get(id: string): Promise<T>;
  create(data: CreateInput<T>): Promise<T>;
  update(id: string, data: UpdateInput<T>): Promise<T>;
  delete(id: string): Promise<void>;
}

class UsersResource implements Resource<User> {
  constructor(private client: ApiClient) {}

  async list(options?: ListOptions): Promise<Page<User>> {
    return this.client.get('/users', { params: options });
  }

  async get(id: string): Promise<User> {
    return this.client.get(`/users/${id}`);
  }

  // ... other methods
}

// Fluent access
const users = client.users.list({ limit: 10 });
```

```python
# Python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class Resource(ABC, Generic[T]):
    @abstractmethod
    def list(self, **options) -> List[T]: ...

    @abstractmethod
    def get(self, id: str) -> T: ...

    @abstractmethod
    def create(self, data: dict) -> T: ...

    @abstractmethod
    def update(self, id: str, data: dict) -> T: ...

    @abstractmethod
    def delete(self, id: str) -> None: ...

class UsersResource(Resource[User]):
    def __init__(self, client: ApiClient):
        self._client = client

    def list(self, **options) -> List[User]:
        return self._client.get('/users', params=options)
```

```go
// Go
type Resource[T any] interface {
    List(ctx context.Context, opts *ListOptions) (*Page[T], error)
    Get(ctx context.Context, id string) (*T, error)
    Create(ctx context.Context, input *CreateInput) (*T, error)
    Update(ctx context.Context, id string, input *UpdateInput) (*T, error)
    Delete(ctx context.Context, id string) error
}

type UsersService struct {
    client *Client
}

func (s *UsersService) List(ctx context.Context, opts *ListOptions) (*Page[User], error) {
    var page Page[User]
    err := s.client.Get(ctx, "/users", opts, &page)
    return &page, err
}
```

```rust
// Rust
#[async_trait]
pub trait Resource<T> {
    async fn list(&self, options: Option<ListOptions>) -> Result<Page<T>, Error>;
    async fn get(&self, id: &str) -> Result<T, Error>;
    async fn create(&self, data: CreateInput) -> Result<T, Error>;
    async fn update(&self, id: &str, data: UpdateInput) -> Result<T, Error>;
    async fn delete(&self, id: &str) -> Result<(), Error>;
}

pub struct UsersResource<'a> {
    client: &'a Client,
}

#[async_trait]
impl Resource<User> for UsersResource<'_> {
    async fn list(&self, options: Option<ListOptions>) -> Result<Page<User>, Error> {
        self.client.get("/users", options).await
    }
    // ...
}
```

### Options Objects vs Positional Arguments

Prefer options objects for methods with multiple optional parameters.

```typescript
// TypeScript - Bad: positional optionals
function search(query: string, limit?: number, offset?: number,
                sortBy?: string, order?: 'asc' | 'desc'): Promise<Results>;

// Good: options object
interface SearchOptions {
  limit?: number;
  offset?: number;
  sortBy?: string;
  order?: 'asc' | 'desc';
}

function search(query: string, options?: SearchOptions): Promise<Results>;
```

```python
# Python - Use TypedDict or dataclass for options
from typing import TypedDict, Optional

class SearchOptions(TypedDict, total=False):
    limit: int
    offset: int
    sort_by: str
    order: str

def search(query: str, options: Optional[SearchOptions] = None) -> Results:
    opts = options or {}
    # ...
```

```go
// Go - Options struct with sensible defaults
type SearchOptions struct {
    Limit  int    `json:"limit,omitempty"`
    Offset int    `json:"offset,omitempty"`
    SortBy string `json:"sort_by,omitempty"`
    Order  string `json:"order,omitempty"`
}

func (c *Client) Search(ctx context.Context, query string, opts *SearchOptions) (*Results, error) {
    if opts == nil {
        opts = &SearchOptions{Limit: 20}
    }
    // ...
}
```

```rust
// Rust - Builder for complex options
#[derive(Default)]
pub struct SearchOptions {
    pub limit: Option<u32>,
    pub offset: Option<u32>,
    pub sort_by: Option<String>,
    pub order: Option<SortOrder>,
}

impl SearchOptions {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn limit(mut self, limit: u32) -> Self {
        self.limit = Some(limit);
        self
    }
    // ... other builders
}

// Usage
client.search("query", SearchOptions::new().limit(10).offset(0)).await?;
```

## Error Handling

### Exception Hierarchies

Create a clear error hierarchy with specific error types.

```typescript
// TypeScript
export class SdkError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly cause?: Error
  ) {
    super(message);
    this.name = 'SdkError';
  }
}

export class NetworkError extends SdkError {
  constructor(message: string, cause?: Error) {
    super(message, 'NETWORK_ERROR', cause);
    this.name = 'NetworkError';
  }
}

export class ApiError extends SdkError {
  constructor(
    message: string,
    public readonly statusCode: number,
    public readonly body?: unknown
  ) {
    super(message, 'API_ERROR');
    this.name = 'ApiError';
  }
}

export class ValidationError extends SdkError {
  constructor(
    message: string,
    public readonly field?: string
  ) {
    super(message, 'VALIDATION_ERROR');
    this.name = 'ValidationError';
  }
}
```

```python
# Python
class SdkError(Exception):
    """Base exception for all SDK errors."""
    def __init__(self, message: str, code: str, cause: Exception = None):
        super().__init__(message)
        self.code = code
        self.cause = cause

class NetworkError(SdkError):
    """Network-related errors (connection, timeout)."""
    def __init__(self, message: str, cause: Exception = None):
        super().__init__(message, 'NETWORK_ERROR', cause)

class ApiError(SdkError):
    """API returned an error response."""
    def __init__(self, message: str, status_code: int, body: dict = None):
        super().__init__(message, 'API_ERROR')
        self.status_code = status_code
        self.body = body

class ValidationError(SdkError):
    """Input validation failed."""
    def __init__(self, message: str, field: str = None):
        super().__init__(message, 'VALIDATION_ERROR')
        self.field = field
```

```go
// Go - Error types with Is/As support
type ErrorCode string

const (
    ErrNetwork    ErrorCode = "NETWORK_ERROR"
    ErrApi        ErrorCode = "API_ERROR"
    ErrValidation ErrorCode = "VALIDATION_ERROR"
)

type SdkError struct {
    Code    ErrorCode
    Message string
    Cause   error
}

func (e *SdkError) Error() string {
    if e.Cause != nil {
        return fmt.Sprintf("%s: %s: %v", e.Code, e.Message, e.Cause)
    }
    return fmt.Sprintf("%s: %s", e.Code, e.Message)
}

func (e *SdkError) Unwrap() error {
    return e.Cause
}

type ApiError struct {
    SdkError
    StatusCode int
    Body       json.RawMessage
}

// Check errors with errors.Is and errors.As
var apiErr *ApiError
if errors.As(err, &apiErr) {
    log.Printf("API error %d: %s", apiErr.StatusCode, apiErr.Body)
}
```

```rust
// Rust - thiserror for ergonomic errors
use thiserror::Error;

#[derive(Error, Debug)]
pub enum SdkError {
    #[error("Network error: {message}")]
    Network {
        message: String,
        #[source]
        source: Option<reqwest::Error>,
    },

    #[error("API error ({status_code}): {message}")]
    Api {
        message: String,
        status_code: u16,
        body: Option<serde_json::Value>,
    },

    #[error("Validation error: {message}")]
    Validation {
        message: String,
        field: Option<String>,
    },

    #[error("Configuration error: {0}")]
    Config(String),
}

// Usage
match result {
    Err(SdkError::Api { status_code: 404, .. }) => {
        // Handle not found
    }
    Err(e) => return Err(e),
    Ok(value) => value,
}
```

```kotlin
// Kotlin
sealed class SdkException(
    message: String,
    val code: String,
    cause: Throwable? = null
) : Exception(message, cause)

class NetworkException(
    message: String,
    cause: Throwable? = null
) : SdkException(message, "NETWORK_ERROR", cause)

class ApiException(
    message: String,
    val statusCode: Int,
    val body: Any? = null
) : SdkException(message, "API_ERROR")

class ValidationException(
    message: String,
    val field: String? = null
) : SdkException(message, "VALIDATION_ERROR")

// Usage with when
try {
    client.getUser(id)
} catch (e: SdkException) {
    when (e) {
        is ApiException -> handleApiError(e.statusCode)
        is NetworkException -> retry()
        is ValidationException -> fixInput(e.field)
    }
}
```

```swift
// Swift
enum SdkError: Error {
    case network(message: String, underlying: Error?)
    case api(message: String, statusCode: Int, body: Data?)
    case validation(message: String, field: String?)
    case configuration(String)
}

extension SdkError: LocalizedError {
    var errorDescription: String? {
        switch self {
        case .network(let message, _):
            return "Network error: \(message)"
        case .api(let message, let code, _):
            return "API error (\(code)): \(message)"
        case .validation(let message, let field):
            if let field = field {
                return "Validation error on \(field): \(message)"
            }
            return "Validation error: \(message)"
        case .configuration(let message):
            return "Configuration error: \(message)"
        }
    }
}
```

```objc
// Objective-C
extern NSErrorDomain const SdkErrorDomain;

typedef NS_ERROR_ENUM(SdkErrorDomain, SdkErrorCode) {
    SdkErrorCodeNetwork = 1000,
    SdkErrorCodeApi = 2000,
    SdkErrorCodeValidation = 3000,
    SdkErrorCodeConfiguration = 4000,
};

// Creating errors
NSError *error = [NSError errorWithDomain:SdkErrorDomain
                                     code:SdkErrorCodeApi
                                 userInfo:@{
    NSLocalizedDescriptionKey: @"API returned error",
    @"statusCode": @(404),
    @"body": responseBody
}];
```

### Retry and Timeout Patterns

```typescript
// TypeScript
interface RetryConfig {
  maxRetries: number;
  baseDelay: number;
  maxDelay: number;
  retryableErrors: string[];
}

async function withRetry<T>(
  fn: () => Promise<T>,
  config: RetryConfig
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      if (!isRetryable(error, config.retryableErrors)) {
        throw error;
      }

      if (attempt < config.maxRetries) {
        const delay = Math.min(
          config.baseDelay * Math.pow(2, attempt),
          config.maxDelay
        );
        await sleep(delay + Math.random() * 100); // Jitter
      }
    }
  }

  throw lastError;
}
```

```go
// Go
type RetryConfig struct {
    MaxRetries     int
    BaseDelay      time.Duration
    MaxDelay       time.Duration
    RetryableFunc  func(error) bool
}

func WithRetry[T any](ctx context.Context, cfg RetryConfig, fn func() (T, error)) (T, error) {
    var lastErr error
    var zero T

    for attempt := 0; attempt <= cfg.MaxRetries; attempt++ {
        result, err := fn()
        if err == nil {
            return result, nil
        }

        lastErr = err
        if !cfg.RetryableFunc(err) {
            return zero, err
        }

        if attempt < cfg.MaxRetries {
            delay := time.Duration(math.Pow(2, float64(attempt))) * cfg.BaseDelay
            if delay > cfg.MaxDelay {
                delay = cfg.MaxDelay
            }

            select {
            case <-ctx.Done():
                return zero, ctx.Err()
            case <-time.After(delay):
            }
        }
    }

    return zero, lastErr
}
```

```rust
// Rust
use tokio::time::{sleep, Duration};

pub struct RetryConfig {
    pub max_retries: u32,
    pub base_delay: Duration,
    pub max_delay: Duration,
}

impl RetryConfig {
    pub async fn execute<T, E, F, Fut>(&self, mut f: F) -> Result<T, E>
    where
        F: FnMut() -> Fut,
        Fut: std::future::Future<Output = Result<T, E>>,
        E: std::fmt::Debug,
    {
        let mut last_error = None;

        for attempt in 0..=self.max_retries {
            match f().await {
                Ok(value) => return Ok(value),
                Err(e) => {
                    last_error = Some(e);

                    if attempt < self.max_retries {
                        let delay = self.base_delay * 2u32.pow(attempt);
                        let delay = delay.min(self.max_delay);
                        sleep(delay).await;
                    }
                }
            }
        }

        Err(last_error.unwrap())
    }
}
```

## Configuration Patterns

### Environment-Based Configuration

```typescript
// TypeScript
interface Config {
  baseUrl: string;
  apiKey: string;
  timeout: number;
  debug: boolean;
}

function loadConfig(): Config {
  return {
    baseUrl: process.env.SDK_BASE_URL ?? 'https://api.example.com',
    apiKey: process.env.SDK_API_KEY ?? '',
    timeout: parseInt(process.env.SDK_TIMEOUT ?? '30000', 10),
    debug: process.env.SDK_DEBUG === 'true',
  };
}
```

```python
# Python
import os
from dataclasses import dataclass

@dataclass
class Config:
    base_url: str
    api_key: str
    timeout: int
    debug: bool

    @classmethod
    def from_env(cls) -> 'Config':
        return cls(
            base_url=os.getenv('SDK_BASE_URL', 'https://api.example.com'),
            api_key=os.getenv('SDK_API_KEY', ''),
            timeout=int(os.getenv('SDK_TIMEOUT', '30000')),
            debug=os.getenv('SDK_DEBUG', 'false').lower() == 'true',
        )
```

```go
// Go
type Config struct {
    BaseURL string        `env:"SDK_BASE_URL" envDefault:"https://api.example.com"`
    APIKey  string        `env:"SDK_API_KEY,required"`
    Timeout time.Duration `env:"SDK_TIMEOUT" envDefault:"30s"`
    Debug   bool          `env:"SDK_DEBUG" envDefault:"false"`
}

// Using github.com/caarlos0/env
func LoadConfig() (*Config, error) {
    cfg := &Config{}
    if err := env.Parse(cfg); err != nil {
        return nil, err
    }
    return cfg, nil
}
```

```rust
// Rust - Using envy crate
use serde::Deserialize;

#[derive(Deserialize)]
pub struct Config {
    #[serde(default = "default_base_url")]
    pub sdk_base_url: String,
    pub sdk_api_key: String,
    #[serde(default = "default_timeout")]
    pub sdk_timeout: u64,
    #[serde(default)]
    pub sdk_debug: bool,
}

fn default_base_url() -> String {
    "https://api.example.com".to_string()
}

fn default_timeout() -> u64 {
    30000
}

impl Config {
    pub fn from_env() -> Result<Self, envy::Error> {
        envy::from_env()
    }
}
```

### Authentication Patterns

```typescript
// TypeScript
interface AuthProvider {
  getHeaders(): Promise<Record<string, string>>;
  refresh?(): Promise<void>;
}

class ApiKeyAuth implements AuthProvider {
  constructor(private apiKey: string) {}

  async getHeaders(): Promise<Record<string, string>> {
    return { 'Authorization': `Bearer ${this.apiKey}` };
  }
}

class OAuth2Auth implements AuthProvider {
  private accessToken: string;
  private refreshToken: string;
  private expiresAt: Date;

  constructor(private clientId: string, private clientSecret: string) {}

  async getHeaders(): Promise<Record<string, string>> {
    if (this.isExpired()) {
      await this.refresh();
    }
    return { 'Authorization': `Bearer ${this.accessToken}` };
  }

  async refresh(): Promise<void> {
    // Token refresh logic
  }

  private isExpired(): boolean {
    return new Date() >= this.expiresAt;
  }
}
```

```python
# Python
from abc import ABC, abstractmethod
from typing import Dict

class AuthProvider(ABC):
    @abstractmethod
    async def get_headers(self) -> Dict[str, str]:
        pass

class ApiKeyAuth(AuthProvider):
    def __init__(self, api_key: str):
        self._api_key = api_key

    async def get_headers(self) -> Dict[str, str]:
        return {'Authorization': f'Bearer {self._api_key}'}

class OAuth2Auth(AuthProvider):
    def __init__(self, client_id: str, client_secret: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = None
        self._expires_at = None

    async def get_headers(self) -> Dict[str, str]:
        if self._is_expired():
            await self._refresh()
        return {'Authorization': f'Bearer {self._access_token}'}
```

```go
// Go
type AuthProvider interface {
    GetHeaders(ctx context.Context) (http.Header, error)
}

type APIKeyAuth struct {
    apiKey string
}

func (a *APIKeyAuth) GetHeaders(ctx context.Context) (http.Header, error) {
    h := make(http.Header)
    h.Set("Authorization", "Bearer "+a.apiKey)
    return h, nil
}

type OAuth2Auth struct {
    clientID     string
    clientSecret string
    accessToken  string
    expiresAt    time.Time
    mu           sync.RWMutex
}

func (a *OAuth2Auth) GetHeaders(ctx context.Context) (http.Header, error) {
    a.mu.RLock()
    if time.Now().Before(a.expiresAt) {
        defer a.mu.RUnlock()
        h := make(http.Header)
        h.Set("Authorization", "Bearer "+a.accessToken)
        return h, nil
    }
    a.mu.RUnlock()

    if err := a.refresh(ctx); err != nil {
        return nil, err
    }

    a.mu.RLock()
    defer a.mu.RUnlock()
    h := make(http.Header)
    h.Set("Authorization", "Bearer "+a.accessToken)
    return h, nil
}
```

```rust
// Rust
use async_trait::async_trait;

#[async_trait]
pub trait AuthProvider: Send + Sync {
    async fn get_headers(&self) -> Result<HeaderMap, AuthError>;
}

pub struct ApiKeyAuth {
    api_key: String,
}

#[async_trait]
impl AuthProvider for ApiKeyAuth {
    async fn get_headers(&self) -> Result<HeaderMap, AuthError> {
        let mut headers = HeaderMap::new();
        headers.insert(
            AUTHORIZATION,
            format!("Bearer {}", self.api_key).parse()?,
        );
        Ok(headers)
    }
}

pub struct OAuth2Auth {
    client_id: String,
    client_secret: String,
    token: RwLock<Option<TokenData>>,
}

#[async_trait]
impl AuthProvider for OAuth2Auth {
    async fn get_headers(&self) -> Result<HeaderMap, AuthError> {
        let token = self.token.read().await;
        if token.as_ref().map_or(true, |t| t.is_expired()) {
            drop(token);
            self.refresh().await?;
        }

        let token = self.token.read().await;
        let mut headers = HeaderMap::new();
        headers.insert(
            AUTHORIZATION,
            format!("Bearer {}", token.as_ref().unwrap().access_token).parse()?,
        );
        Ok(headers)
    }
}
```

## Testing Strategies

### Unit Testing with Mocks

```typescript
// TypeScript - Jest
import { ApiClient } from './client';
import { HttpClient } from './http';

jest.mock('./http');

describe('ApiClient', () => {
  let client: ApiClient;
  let mockHttp: jest.Mocked<HttpClient>;

  beforeEach(() => {
    mockHttp = new HttpClient() as jest.Mocked<HttpClient>;
    client = new ApiClient({ http: mockHttp });
  });

  it('should fetch user by id', async () => {
    const mockUser = { id: '1', name: 'Test' };
    mockHttp.get.mockResolvedValue(mockUser);

    const user = await client.users.get('1');

    expect(mockHttp.get).toHaveBeenCalledWith('/users/1');
    expect(user).toEqual(mockUser);
  });

  it('should handle errors', async () => {
    mockHttp.get.mockRejectedValue(new ApiError('Not found', 404));

    await expect(client.users.get('999')).rejects.toThrow(ApiError);
  });
});
```

```python
# Python - pytest
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_http():
    return AsyncMock()

@pytest.fixture
def client(mock_http):
    return ApiClient(http=mock_http)

@pytest.mark.asyncio
async def test_get_user(client, mock_http):
    mock_user = {'id': '1', 'name': 'Test'}
    mock_http.get.return_value = mock_user

    user = await client.users.get('1')

    mock_http.get.assert_called_with('/users/1')
    assert user == mock_user

@pytest.mark.asyncio
async def test_get_user_not_found(client, mock_http):
    mock_http.get.side_effect = ApiError('Not found', 404)

    with pytest.raises(ApiError) as exc:
        await client.users.get('999')

    assert exc.value.status_code == 404
```

```go
// Go - testify
func TestGetUser(t *testing.T) {
    mockHTTP := &MockHTTPClient{}
    client := NewClient(WithHTTP(mockHTTP))

    expectedUser := &User{ID: "1", Name: "Test"}
    mockHTTP.On("Get", mock.Anything, "/users/1", mock.Anything).
        Return(expectedUser, nil)

    user, err := client.Users.Get(context.Background(), "1")

    require.NoError(t, err)
    assert.Equal(t, expectedUser, user)
    mockHTTP.AssertExpectations(t)
}

func TestGetUserNotFound(t *testing.T) {
    mockHTTP := &MockHTTPClient{}
    client := NewClient(WithHTTP(mockHTTP))

    mockHTTP.On("Get", mock.Anything, "/users/999", mock.Anything).
        Return(nil, &ApiError{StatusCode: 404})

    _, err := client.Users.Get(context.Background(), "999")

    var apiErr *ApiError
    require.ErrorAs(t, err, &apiErr)
    assert.Equal(t, 404, apiErr.StatusCode)
}
```

```rust
// Rust - mockall
use mockall::predicate::*;

#[cfg(test)]
mod tests {
    use super::*;
    use mockall::mock;

    mock! {
        HttpClient {}

        #[async_trait]
        impl HttpClientTrait for HttpClient {
            async fn get<T: DeserializeOwned>(&self, path: &str) -> Result<T, Error>;
        }
    }

    #[tokio::test]
    async fn test_get_user() {
        let mut mock = MockHttpClient::new();
        mock.expect_get::<User>()
            .with(eq("/users/1"))
            .returning(|_| Ok(User { id: "1".into(), name: "Test".into() }));

        let client = Client::new(mock);
        let user = client.users().get("1").await.unwrap();

        assert_eq!(user.id, "1");
    }
}
```

### Contract Testing

```typescript
// TypeScript - Pact
import { Pact } from '@pact-foundation/pact';

const provider = new Pact({
  consumer: 'MySdk',
  provider: 'MyApi',
});

describe('API Contract', () => {
  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());
  afterEach(() => provider.verify());

  it('should get user', async () => {
    await provider.addInteraction({
      state: 'user exists',
      uponReceiving: 'a request for user 1',
      withRequest: {
        method: 'GET',
        path: '/users/1',
      },
      willRespondWith: {
        status: 200,
        body: {
          id: '1',
          name: like('Test User'),
        },
      },
    });

    const client = new ApiClient({ baseUrl: provider.mockService.baseUrl });
    const user = await client.users.get('1');

    expect(user.id).toBe('1');
  });
});
```

## Documentation Standards

### API Documentation Structure

```markdown
# SDK Name

Brief description of what the SDK does.

## Installation

### npm
\`\`\`bash
npm install my-sdk
\`\`\`

### yarn
\`\`\`bash
yarn add my-sdk
\`\`\`

## Quick Start

\`\`\`typescript
import { Client } from 'my-sdk';

const client = new Client({ apiKey: 'your-api-key' });

// List users
const users = await client.users.list();

// Get single user
const user = await client.users.get('user-id');
\`\`\`

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | `string` | required | Your API key |
| `baseUrl` | `string` | `https://api.example.com` | API base URL |
| `timeout` | `number` | `30000` | Request timeout in ms |
| `retries` | `number` | `3` | Number of retry attempts |

## Resources

### Users

#### `client.users.list(options?)`

List all users.

**Parameters:**
- `options.limit` (number, optional): Maximum results to return
- `options.offset` (number, optional): Pagination offset

**Returns:** `Promise<Page<User>>`

**Example:**
\`\`\`typescript
const page = await client.users.list({ limit: 10 });
console.log(page.data);
\`\`\`

## Error Handling

\`\`\`typescript
try {
  await client.users.get('invalid-id');
} catch (error) {
  if (error instanceof ApiError) {
    console.error(`API Error ${error.statusCode}: ${error.message}`);
  } else if (error instanceof NetworkError) {
    console.error('Network error:', error.message);
  }
}
\`\`\`

## Migration Guide

### v1.x to v2.x

- `client.getUser(id)` → `client.users.get(id)`
- `UserResponse` type renamed to `User`
```

## Packaging and Distribution

### Semantic Versioning

Follow [SemVer 2.0.0](https://semver.org/):

| Version | When to Increment |
|---------|-------------------|
| MAJOR (X.0.0) | Breaking changes to public API |
| MINOR (0.X.0) | New backward-compatible features |
| PATCH (0.0.X) | Backward-compatible bug fixes |

**Pre-release versions:** `1.0.0-alpha.1`, `1.0.0-beta.2`, `1.0.0-rc.1`

### Changelog Format

Follow [Keep a Changelog](https://keepachangelog.com/):

```markdown
# Changelog

## [Unreleased]

### Added
- New `client.batch()` method for batch operations

### Changed
- Improved error messages for validation errors

## [2.1.0] - 2024-01-15

### Added
- OAuth2 authentication support
- Automatic token refresh

### Fixed
- Race condition in concurrent requests

## [2.0.0] - 2024-01-01

### Changed
- **BREAKING**: Renamed `getUser()` to `users.get()`
- **BREAKING**: Minimum Node.js version is now 18

### Removed
- **BREAKING**: Removed deprecated `v1` endpoints
```

### Breaking Change Policy

1. **Document clearly** in CHANGELOG and migration guide
2. **Deprecate first** - warn users before removal
3. **Provide migration path** - automated codemods if possible
4. **Major version only** - never in minor/patch

## Cross-Cutting Concerns

### Logging

```typescript
// TypeScript
interface Logger {
  debug(message: string, meta?: object): void;
  info(message: string, meta?: object): void;
  warn(message: string, meta?: object): void;
  error(message: string, meta?: object): void;
}

class Client {
  constructor(
    private config: Config,
    private logger: Logger = console
  ) {}

  async request(method: string, path: string): Promise<Response> {
    this.logger.debug('Making request', { method, path });

    try {
      const response = await this.http.request(method, path);
      this.logger.debug('Request succeeded', { status: response.status });
      return response;
    } catch (error) {
      this.logger.error('Request failed', { error: error.message });
      throw error;
    }
  }
}
```

### Telemetry / Observability

```typescript
// TypeScript
interface Metrics {
  increment(name: string, tags?: Record<string, string>): void;
  timing(name: string, ms: number, tags?: Record<string, string>): void;
}

class InstrumentedClient {
  constructor(
    private client: Client,
    private metrics: Metrics
  ) {}

  async request(method: string, path: string): Promise<Response> {
    const start = Date.now();
    const tags = { method, path };

    try {
      const response = await this.client.request(method, path);
      this.metrics.increment('sdk.request.success', tags);
      return response;
    } catch (error) {
      this.metrics.increment('sdk.request.error', { ...tags, error: error.code });
      throw error;
    } finally {
      this.metrics.timing('sdk.request.duration', Date.now() - start, tags);
    }
  }
}
```

### Rate Limiting

```typescript
// TypeScript
class RateLimiter {
  private tokens: number;
  private lastRefill: number;

  constructor(
    private maxTokens: number,
    private refillRate: number // tokens per second
  ) {
    this.tokens = maxTokens;
    this.lastRefill = Date.now();
  }

  async acquire(): Promise<void> {
    this.refill();

    if (this.tokens <= 0) {
      const waitTime = (1 / this.refillRate) * 1000;
      await sleep(waitTime);
      this.refill();
    }

    this.tokens--;
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    this.tokens = Math.min(
      this.maxTokens,
      this.tokens + elapsed * this.refillRate
    );
    this.lastRefill = now;
  }
}
```

---

# Part 2: Creating SDK Development Skills

This section provides patterns for creating domain-specific SDK development skills that extend these foundational patterns.

## Skill Structure Template

```markdown
---
name: <domain>-sdk-dev
description: Develop <Domain> SDK implementations from the specification.
Use when implementing the <Domain> spec in a new language, extending
existing SDKs with new features, or contributing to official SDK repositories.
---

# <Domain> SDK Development

Guide for implementing <Domain> SDKs from the specification.

## When to Use This Skill

- Implementing <Domain> in a new programming language
- Contributing to official <Domain> SDK repositories
- Building custom providers/plugins from scratch
- Extending existing SDKs with new features

## Specification Overview

[Link to official specification]

### Key Concepts

- Concept 1: Brief explanation
- Concept 2: Brief explanation
- ...

## Core Architecture

[Domain-specific architecture diagram]

## Type Definitions

[Domain-specific types with language examples]

## Interface Specifications

[MUST/SHOULD requirements from spec]

## Implementation Checklist

### Phase 1: Core Types
- [ ] Type definition 1
- [ ] Type definition 2

### Phase 2: Core Interface
- [ ] Interface method 1
- [ ] Interface method 2

[Continue phases...]

## Testing Requirements

[Domain-specific test patterns]

## References

- [Official Specification](url)
- [Reference Implementations](url)
- [Test Suites](url)
```

## Analyzing Specifications

When creating an SDK development skill from a specification:

### 1. Identify Normative Requirements

Look for RFC 2119 keywords:

| Keyword | Meaning | SDK Implication |
|---------|---------|-----------------|
| MUST | Absolute requirement | Required for compliance |
| MUST NOT | Absolute prohibition | Must be prevented |
| SHOULD | Recommended | Include with escape hatch |
| SHOULD NOT | Not recommended | Warn if used |
| MAY | Optional | Document as optional |

### 2. Extract Core Concepts

Map specification concepts to SDK components:

```
Specification Concept → SDK Component
─────────────────────────────────────
Client API           → Client class/struct
Provider Interface   → Plugin/Provider trait
Configuration        → Config struct/builder
Events              → Event emitter pattern
Hooks/Middleware    → Hook interface
Context             → Context object
```

### 3. Map Types

Create type definition section mapping spec types to language idioms:

| Spec Type | TypeScript | Python | Go | Rust |
|-----------|------------|--------|-----|------|
| String | `string` | `str` | `string` | `String` |
| Number | `number` | `int/float` | `int/float64` | `i32/f64` |
| Boolean | `boolean` | `bool` | `bool` | `bool` |
| Object/Map | `Record<K,V>` | `Dict[K,V]` | `map[K]V` | `HashMap<K,V>` |
| Array | `T[]` | `List[T]` | `[]T` | `Vec<T>` |
| Optional | `T \| undefined` | `Optional[T]` | `*T` | `Option<T>` |
| Result | `Promise<T>` | `Result[T]` | `(T, error)` | `Result<T,E>` |

### 4. Create Implementation Checklist

Break down implementation into phases:

1. **Core Types** - Basic type definitions
2. **Core Interface** - Primary API surface
3. **Provider/Plugin System** - Extensibility
4. **Lifecycle Management** - Init/shutdown
5. **Error Handling** - Error types and propagation
6. **Events** - If spec includes events
7. **Hooks/Middleware** - If spec includes hooks
8. **Testing** - Compliance tests

### 5. Include Compliance Tests

Reference or include Gherkin/BDD tests from specification:

```gherkin
Feature: Core API

Scenario: Client initialization
  Given a valid configuration
  When the client is initialized
  Then the client status should be "ready"

Scenario: Error handling
  Given an invalid configuration
  When the client is initialized
  Then an error should be returned
  And the error code should be "INVALID_CONFIG"
```

## Skill Inheritance Pattern

Domain-specific skills should reference this skill:

```markdown
---
name: openfeature-sdk-dev
description: ...
---

# OpenFeature SDK Development

> **Note**: This skill extends patterns from `meta-sdk-patterns-eng`.
> See that skill for foundational SDK patterns.

## OpenFeature-Specific Patterns

[Domain-specific content...]
```

## Example: Creating a New SDK Skill

Given a specification for "FeatureFlags API v2":

1. **Read specification** completely
2. **Extract MUST requirements** → Implementation checklist
3. **Identify types** → Type definitions section
4. **Map interfaces** → Interface specifications
5. **Find test suites** → Testing requirements
6. **Document architecture** → Core architecture section

---

## References

### API Design
- [Google API Design Guide](https://cloud.google.com/apis/design)
- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [Zalando RESTful API Guidelines](https://opensource.zalando.com/restful-api-guidelines/)

### SDK Development
- [AWS SDK Design](https://aws.amazon.com/developers/getting-started/tools/)
- [Stripe API Design](https://stripe.com/docs/api)
- [Twilio SDK Design](https://www.twilio.com/docs/libraries)

### Versioning & Releases
- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Open Source Best Practices
- [Open Source Guides](https://opensource.guide/)
- [The Documentation System](https://documentation.divio.com/)

### Language-Specific Resources
- **Rust**: [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- **Go**: [Effective Go](https://go.dev/doc/effective_go)
- **Python**: [PEP 8](https://peps.python.org/pep-0008/), [Google Python Style](https://google.github.io/styleguide/pyguide.html)
- **TypeScript**: [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- **Kotlin**: [Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html)
- **Swift**: [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)
- **Objective-C**: [Apple Coding Guidelines](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/CodingGuidelines/)
