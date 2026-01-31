---
name: openmetadata-sdk-dev
description: Develop and contribute to OpenMetadata SDKs, connectors, and core platform. Use when implementing new language SDKs, building connectors for contribution, extending SDK capabilities, or setting up the OpenMetadata development environment.
---

# OpenMetadata SDK & Connector Development

Guide for developing OpenMetadata SDKs, connectors, and contributions to the core platform. All SDK and connector development is intended to be contributed back to the community.

> **Note**: This skill extends patterns from `meta-sdk-patterns-eng`.
> See that skill for foundational SDK patterns (architecture, error handling,
> configuration, testing strategies, packaging).

## When to Use This Skill

- Implementing OpenMetadata SDK for a new language
- Extending existing Python or Java SDK with new features
- **Contributing new connectors to OpenMetadata**
- Adding new entity type support
- Implementing authentication providers
- Setting up OpenMetadata development environment
- Generating entity models from JSON Schemas

## This Skill Does NOT Cover

- Using the existing Python/Java SDK to interact with OpenMetadata (see `openmetadata-dev`)
- Deploying or operating OpenMetadata
- Administering users, bots, and policies (see `openmetadata-ops`)

---

## OpenMetadata SDK Architecture

### Core Components

Every OpenMetadata SDK implements these components:

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenMetadata Client                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Connection  │  │    Auth     │  │   API Clients       │  │
│  │   Config    │  │  Provider   │  │  (Tables, Dashes..) │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Entity Models (Generated)                  ││
│  │   Table, Database, Dashboard, Pipeline, MlModel, etc.   ││
│  └─────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐│
│  │              HTTP Client / Transport Layer              ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Pattern: Gateway with Typed API Clients

OpenMetadata SDKs use a gateway pattern where the main client builds typed API clients:

```python
# Python Pattern
class OpenMetadata:
    def __init__(self, config: OpenMetadataConnection):
        self._config = config
        self._client = self._build_client()

    def get_by_name(self, entity: Type[T], fqn: str) -> Optional[T]:
        """Generic method using TypeVar for type safety."""
        ...

    def create_or_update(self, data: CreateEntity) -> Entity:
        """Handles both create and update operations."""
        ...
```

```java
// Java Pattern
public class OpenMetadata {
    private final OpenMetadataConnection config;

    public <T> T buildClient(Class<T> apiClass) {
        // Build typed API client
        return clientBuilder.build(apiClass);
    }
}

// Usage
TablesApi tablesApi = openMetadata.buildClient(TablesApi.class);
DashboardsApi dashboardApi = openMetadata.buildClient(DashboardsApi.class);
```

---

## Connection Configuration

### Configuration Object

```python
# Python
from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
    AuthProvider,
)

server_config = OpenMetadataConnection(
    hostPort="http://localhost:8585/api",
    authProvider=AuthProvider.openmetadata,
    securityConfig=OpenMetadataJWTClientConfig(jwtToken="<token>"),
    verifySSL="validate",  # or "ignore", "no-ssl"
    sslConfig=ValidateSslClientConfig(caCertificate="/path/to/cert"),
)
```

```java
// Java
OpenMetadataConnection server = new OpenMetadataConnection();
server.setHostPort("http://localhost:8585/api");
server.setApiVersion("v1");
server.setAuthProvider(OpenMetadataConnection.AuthProvider.OPENMETADATA);
server.setSecurityConfig(jwtClientConfig);
```

### Configuration Fields

| Field | Required | Description |
|-------|----------|-------------|
| `hostPort` | Yes | Base URL including `/api` |
| `authProvider` | Yes | Authentication provider type |
| `securityConfig` | Yes | Provider-specific auth config |
| `apiVersion` | No | API version (default: `v1`) |
| `verifySSL` | No | SSL verification mode |
| `sslConfig` | No | Custom SSL certificates |

---

## Authentication Providers

### Provider Architecture

Implement pluggable authentication with a provider interface:

```python
# Python
class AuthenticationProvider(ABC):
    @abstractmethod
    def get_access_token(self) -> str:
        """Return valid access token."""
        pass

class OpenMetadataJWTProvider(AuthenticationProvider):
    def __init__(self, config: OpenMetadataJWTClientConfig):
        self._token = config.jwtToken

    def get_access_token(self) -> str:
        return self._token

class OktaProvider(AuthenticationProvider):
    def __init__(self, config: OktaClientConfig):
        self._client_id = config.clientId
        self._org_url = config.orgURL
        self._scopes = config.scopes

    def get_access_token(self) -> str:
        # OAuth2 token exchange
        ...
```

```java
// Java
public interface AuthenticationProvider {
    String getAccessToken();
}

public class NoOpAuthenticationProvider implements AuthenticationProvider {
    @Override
    public String getAccessToken() {
        return "";
    }
}

public class GoogleAuthenticationProvider implements AuthenticationProvider {
    private final GoogleSSOClientConfig config;

    @Override
    public String getAccessToken() {
        // OAuth2 flow with Google
        ...
    }
}
```

### Supported Providers

| Provider | Config Class | Auth Flow |
|----------|--------------|-----------|
| `openmetadata` | `OpenMetadataJWTClientConfig` | Static JWT token |
| `google` | `GoogleSSOClientConfig` | OAuth2 OIDC |
| `okta` | `OktaClientConfig` | OAuth2 OIDC |
| `auth0` | `Auth0ClientConfig` | OAuth2 OIDC |
| `azure` | `AzureClientConfig` | OAuth2 OIDC |
| `custom-oidc` | `CustomOIDCClientConfig` | OAuth2 OIDC |
| `no-auth` | None | No authentication |

### Implementing New Provider

1. Define configuration schema (JSON Schema)
2. Generate config class from schema
3. Implement `AuthenticationProvider` interface
4. Register in provider factory
5. Add to `AuthProvider` enum

### Bot Token Internals

OpenMetadata Bots are service accounts that provide JWT tokens for SDK authentication. When implementing SDK auth:

#### Bot Token Structure

Bot tokens are JWTs with specific claims:

```json
{
  "sub": "ingestion-bot",
  "iss": "open-metadata.org",
  "iat": 1234567890,
  "exp": 1234567890,
  "email": "ingestion-bot@openmetadata.org",
  "isBot": true
}
```

#### SDK Token Validation

When implementing auth provider, validate bot tokens:

```python
# Python
import jwt
from typing import Optional

class BotTokenValidator:
    def __init__(self, public_key: str, issuer: str = "open-metadata.org"):
        self._public_key = public_key
        self._issuer = issuer

    def validate(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token,
                self._public_key,
                algorithms=["RS256"],
                issuer=self._issuer,
            )
            if not payload.get("isBot", False):
                raise ValueError("Token is not a bot token")
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Bot token expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid bot token: {e}")
```

```rust
// Rust
use jsonwebtoken::{decode, DecodingKey, Validation, Algorithm};

#[derive(Debug, Deserialize)]
struct BotClaims {
    sub: String,
    iss: String,
    exp: u64,
    is_bot: bool,
}

impl BotTokenValidator {
    pub fn validate(&self, token: &str) -> Result<BotClaims, AuthError> {
        let mut validation = Validation::new(Algorithm::RS256);
        validation.set_issuer(&["open-metadata.org"]);

        let token_data = decode::<BotClaims>(
            token,
            &DecodingKey::from_rsa_pem(self.public_key.as_bytes())?,
            &validation,
        )?;

        if !token_data.claims.is_bot {
            return Err(AuthError::NotBotToken);
        }

        Ok(token_data.claims)
    }
}
```

#### Token Refresh Handling

Bot tokens have expiration. SDKs should handle refresh:

```python
class BotAuthProvider(AuthenticationProvider):
    def __init__(self, config: BotConfig):
        self._config = config
        self._cached_token: Optional[str] = None
        self._expires_at: Optional[datetime] = None

    def get_access_token(self) -> str:
        if self._is_token_valid():
            return self._cached_token

        # Refresh token from OpenMetadata API
        self._cached_token = self._refresh_token()
        self._expires_at = self._parse_expiry(self._cached_token)
        return self._cached_token

    def _is_token_valid(self) -> bool:
        if not self._cached_token or not self._expires_at:
            return False
        # Refresh 5 minutes before expiry
        return datetime.utcnow() < (self._expires_at - timedelta(minutes=5))
```

---

## Entity Models

### Schema-Driven Generation

OpenMetadata entities are defined as JSON Schemas and models are generated:

```
json-schemas/
├── entity/
│   ├── data/
│   │   ├── table.json
│   │   ├── database.json
│   │   └── dashboard.json
│   ├── services/
│   │   └── databaseService.json
│   └── teams/
│       └── user.json
└── api/
    ├── data/
    │   ├── createTable.json
    │   └── createDatabase.json
    └── services/
        └── createDatabaseService.json
```

### Entity vs API Models

OpenMetadata separates entity definitions from API request models:

| Type | Purpose | Example |
|------|---------|---------|
| **Entity** | Response/read models | `Table`, `Database`, `Dashboard` |
| **Create** | POST request body | `CreateTable`, `CreateDatabase` |
| **Update** | PATCH request body | Partial entity fields |

```python
# Entity model (response)
class Table(BaseModel):
    id: UUID
    name: str
    fullyQualifiedName: str
    columns: List[Column]
    database: EntityReference
    ...

# API model (request)
class CreateTable(BaseModel):
    name: str
    columns: List[Column]
    databaseSchema: FullyQualifiedEntityName
    ...
```

### Entity Hierarchy

```
DatabaseService
    └── Database
        └── DatabaseSchema
            └── Table
                └── Column

DashboardService
    └── Dashboard
        └── Chart

PipelineService
    └── Pipeline
        └── Task

MessagingService
    └── Topic
```

### Entity References

Link entities using references:

```python
# By fully qualified name
table = CreateTable(
    name="orders",
    databaseSchema="prod.sales.public",  # FQN string
    columns=[...],
)

# By EntityReference
table.owner = EntityReference(
    id=user_uuid,
    type="user",
)
```

### Custom Property Model Handling

OpenMetadata supports user-defined custom properties on entities. SDKs must handle these dynamic fields.

#### Schema Definition

Custom properties are defined per entity type:

```json
{
  "name": "customField",
  "propertyType": {
    "id": "uuid",
    "type": "type",
    "name": "string"
  },
  "description": "Custom field description"
}
```

#### SDK Model Strategy

**Option 1: Extension Dictionary (Recommended)**

Keep generated models clean, store custom properties separately:

```python
# Python
class Table(BaseModel):
    id: UUID
    name: str
    columns: List[Column]
    # ... standard fields

    extension: Optional[Dict[str, Any]] = None  # Custom properties

    def get_custom_property(self, name: str) -> Any:
        if self.extension is None:
            return None
        return self.extension.get(name)

    def set_custom_property(self, name: str, value: Any) -> None:
        if self.extension is None:
            self.extension = {}
        self.extension[name] = value
```

```typescript
// TypeScript
interface Table {
    id: string;
    name: string;
    columns: Column[];
    // ... standard fields

    extension?: Record<string, unknown>;  // Custom properties
}

function getCustomProperty<T>(entity: Table, name: string): T | undefined {
    return entity.extension?.[name] as T | undefined;
}
```

```rust
// Rust
#[derive(Debug, Serialize, Deserialize)]
pub struct Table {
    pub id: Uuid,
    pub name: String,
    pub columns: Vec<Column>,
    // ... standard fields

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub extension: Option<HashMap<String, serde_json::Value>>,
}

impl Table {
    pub fn get_custom_property<T: DeserializeOwned>(&self, name: &str) -> Option<T> {
        self.extension
            .as_ref()?
            .get(name)
            .and_then(|v| serde_json::from_value(v.clone()).ok())
    }
}
```

**Option 2: Dynamic Model Generation**

Generate models at runtime based on custom property definitions:

```python
# Python - dynamic model creation
from pydantic import create_model

def build_table_model(custom_properties: List[CustomProperty]) -> Type[BaseModel]:
    """Build Table model with custom properties as typed fields."""
    extra_fields = {}
    for prop in custom_properties:
        field_type = PROPERTY_TYPE_MAP.get(prop.propertyType.name, Any)
        extra_fields[prop.name] = (Optional[field_type], None)

    return create_model(
        'TableWithCustomProperties',
        __base__=Table,
        **extra_fields,
    )
```

#### Type Mapping for Custom Properties

| OpenMetadata Type | Python | TypeScript | Rust | Go |
|-------------------|--------|------------|------|-----|
| `string` | `str` | `string` | `String` | `string` |
| `integer` | `int` | `number` | `i64` | `int64` |
| `number` | `float` | `number` | `f64` | `float64` |
| `markdown` | `str` | `string` | `String` | `string` |
| `enum` | `Enum` | `string` | `enum` | `string` |
| `date` | `date` | `string` | `NaiveDate` | `time.Time` |
| `dateTime` | `datetime` | `string` | `DateTime<Utc>` | `time.Time` |
| `time` | `time` | `string` | `NaiveTime` | `time.Time` |
| `duration` | `timedelta` | `string` | `Duration` | `time.Duration` |
| `entityReference` | `EntityReference` | `EntityReference` | `EntityReference` | `EntityReference` |
| `entityReferenceList` | `List[EntityReference]` | `EntityReference[]` | `Vec<EntityReference>` | `[]EntityReference` |

#### Serialization Considerations

Custom properties use the `extension` field in API payloads:

```json
{
  "id": "uuid",
  "name": "orders",
  "columns": [...],
  "extension": {
    "customField1": "value",
    "customField2": 123,
    "customEntityRef": {
      "id": "uuid",
      "type": "user",
      "name": "john"
    }
  }
}
```

SDKs should:
1. Preserve unknown fields during round-trip (deserialize → serialize)
2. Validate custom property types if schema is available
3. Handle missing custom properties gracefully (return `None`/`null`/`Option::None`)

---

## API Client Implementation

### Standard CRUD Operations

Every entity API should implement:

```python
class EntityAPI(Generic[T, CreateT]):
    def create_or_update(self, entity: CreateT) -> T:
        """POST /api/v1/{entities}"""
        ...

    def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """GET /api/v1/{entities}/{id}"""
        ...

    def get_by_name(self, fqn: str, fields: List[str] = None) -> Optional[T]:
        """GET /api/v1/{entities}/name/{fqn}"""
        ...

    def list(self, limit: int = 10, fields: List[str] = None) -> ResultList[T]:
        """GET /api/v1/{entities}"""
        ...

    def delete(
        self,
        entity_id: UUID,
        recursive: bool = False,
        hard_delete: bool = False,
    ) -> None:
        """DELETE /api/v1/{entities}/{id}"""
        ...
```

### API Endpoints Pattern

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List | GET | `/api/v1/{entities}` |
| Get by ID | GET | `/api/v1/{entities}/{id}` |
| Get by Name | GET | `/api/v1/{entities}/name/{fqn}` |
| Create/Update | PUT | `/api/v1/{entities}` |
| Patch | PATCH | `/api/v1/{entities}/{id}` |
| Delete | DELETE | `/api/v1/{entities}/{id}` |

### Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `fields` | Include optional fields | `?fields=columns,owner` |
| `limit` | Pagination limit | `?limit=100` |
| `before`/`after` | Cursor pagination | `?after={cursor}` |
| `include` | Include deleted | `?include=deleted` |

---

## Mixins for Special Behaviors

### Lineage Mixin

```python
class LineageMixin:
    def add_lineage(self, edge: AddLineage) -> None:
        """PUT /api/v1/lineage"""
        ...

    def get_lineage(
        self,
        entity_type: str,
        entity_id: UUID,
        up_depth: int = 1,
        down_depth: int = 1,
    ) -> EntityLineage:
        """GET /api/v1/lineage/{type}/{id}"""
        ...
```

### Tag Mixin

```python
class TagMixin:
    def add_tag(self, entity_id: UUID, tag_fqn: str) -> None:
        """PATCH /api/v1/{entities}/{id}"""
        ...

    def remove_tag(self, entity_id: UUID, tag_fqn: str) -> None:
        ...
```

### Owner Mixin

```python
class OwnerMixin:
    def set_owner(self, entity_id: UUID, owner: EntityReference) -> None:
        ...
```

### Composing Mixins

```python
class OpenMetadata(LineageMixin, TagMixin, OwnerMixin):
    """Main client composes all mixins."""

    def __init__(self, config: OpenMetadataConnection):
        self._config = config
        self._client = self._build_http_client()
```

---

## Error Handling

### Exception Hierarchy

```python
class OpenMetadataException(Exception):
    """Base exception for all SDK errors."""
    pass

class AuthenticationError(OpenMetadataException):
    """Authentication failed."""
    pass

class EntityNotFoundError(OpenMetadataException):
    """Entity does not exist."""
    pass

class ValidationError(OpenMetadataException):
    """Request validation failed."""
    pass

class ConflictError(OpenMetadataException):
    """Entity already exists or version conflict."""
    pass

class RateLimitError(OpenMetadataException):
    """Rate limit exceeded."""
    retry_after: int
```

### HTTP Status Mapping

| Status | Exception | Action |
|--------|-----------|--------|
| 401 | `AuthenticationError` | Re-authenticate |
| 403 | `AuthorizationError` | Check permissions |
| 404 | `EntityNotFoundError` | Return None or raise |
| 409 | `ConflictError` | Handle version conflict |
| 422 | `ValidationError` | Fix request payload |
| 429 | `RateLimitError` | Retry with backoff |
| 5xx | `ServerError` | Retry with backoff |

### Return None vs Raise

```python
def get_by_name(self, entity: Type[T], fqn: str) -> Optional[T]:
    """Return None for 404, raise for other errors."""
    try:
        response = self._client.get(f"/api/v1/{entity.path}/name/{fqn}")
        return entity.parse_obj(response.json())
    except HTTPError as e:
        if e.response.status_code == 404:
            return None
        raise self._map_exception(e)
```

---

## Implementing a New Language SDK

### Step 1: Project Setup

```bash
# Directory structure
openmetadata-sdk-{lang}/
├── src/
│   ├── client/
│   │   ├── openmetadata.{ext}
│   │   └── connection.{ext}
│   ├── auth/
│   │   ├── provider.{ext}
│   │   └── jwt.{ext}
│   ├── api/
│   │   ├── tables.{ext}
│   │   ├── databases.{ext}
│   │   └── ...
│   ├── models/
│   │   └── generated/      # From JSON schemas
│   └── mixins/
│       ├── lineage.{ext}
│       └── tags.{ext}
├── tests/
├── examples/
└── README.md
```

### Step 2: Model Generation

Use JSON Schema to generate models:

```bash
# Python: datamodel-codegen
datamodel-codegen \
    --input json-schemas/ \
    --output src/models/generated/ \
    --output-model-type pydantic_v2.BaseModel

# TypeScript: json-schema-to-typescript
npx json-schema-to-typescript \
    json-schemas/**/*.json \
    --out src/models/

# Rust: schemafy or typify
cargo run --bin generate-models -- \
    --schema-dir json-schemas/ \
    --out-dir src/models/
```

### Step 3: Implement Core Client

```rust
// Rust Example
pub struct OpenMetadata {
    config: OpenMetadataConnection,
    client: reqwest::Client,
    auth: Box<dyn AuthenticationProvider>,
}

impl OpenMetadata {
    pub fn new(config: OpenMetadataConnection) -> Result<Self, Error> {
        let auth = Self::build_auth_provider(&config)?;
        let client = Self::build_http_client(&config)?;

        Ok(Self { config, client, auth })
    }

    pub fn health_check(&self) -> Result<(), Error> {
        let response = self.client
            .get(format!("{}/health-check", self.config.host_port))
            .send()?;

        if response.status().is_success() {
            Ok(())
        } else {
            Err(Error::HealthCheckFailed)
        }
    }

    pub fn tables(&self) -> TablesApi {
        TablesApi::new(&self.client, &self.auth)
    }
}
```

### Step 4: Implement Entity APIs

```typescript
// TypeScript Example
export class TablesApi {
    constructor(
        private client: HttpClient,
        private auth: AuthenticationProvider,
    ) {}

    async getByName(fqn: string, fields?: string[]): Promise<Table | null> {
        const params = fields ? { fields: fields.join(',') } : {};
        try {
            const response = await this.client.get(
                `/api/v1/tables/name/${encodeURIComponent(fqn)}`,
                { params },
            );
            return response.data as Table;
        } catch (e) {
            if (e.response?.status === 404) return null;
            throw this.mapError(e);
        }
    }

    async createOrUpdate(table: CreateTable): Promise<Table> {
        const response = await this.client.put('/api/v1/tables', table);
        return response.data as Table;
    }

    async delete(
        id: string,
        options: { recursive?: boolean; hardDelete?: boolean } = {},
    ): Promise<void> {
        await this.client.delete(`/api/v1/tables/${id}`, {
            params: {
                recursive: options.recursive ?? false,
                hardDelete: options.hardDelete ?? false,
            },
        });
    }
}
```

### Step 5: Add Authentication Providers

```go
// Go Example
type AuthenticationProvider interface {
    GetAccessToken() (string, error)
}

type JWTProvider struct {
    token string
}

func (p *JWTProvider) GetAccessToken() (string, error) {
    return p.token, nil
}

type OktaProvider struct {
    clientID    string
    orgURL      string
    privateKey  string
    scopes      []string
    cachedToken string
    expiresAt   time.Time
}

func (p *OktaProvider) GetAccessToken() (string, error) {
    if time.Now().Before(p.expiresAt) {
        return p.cachedToken, nil
    }
    // Refresh token via OAuth2
    token, expiry, err := p.refreshToken()
    if err != nil {
        return "", err
    }
    p.cachedToken = token
    p.expiresAt = expiry
    return token, nil
}
```

### Step 6: Implement Mixins

```kotlin
// Kotlin Example
interface LineageMixin {
    val client: HttpClient

    suspend fun addLineage(edge: AddLineage) {
        client.put("/api/v1/lineage", edge)
    }

    suspend fun getLineage(
        entityType: String,
        entityId: UUID,
        upDepth: Int = 1,
        downDepth: Int = 1,
    ): EntityLineage {
        return client.get(
            "/api/v1/lineage/$entityType/$entityId",
            mapOf("upDepth" to upDepth, "downDepth" to downDepth),
        )
    }
}

class OpenMetadata(
    private val config: OpenMetadataConnection,
) : LineageMixin, TagMixin {
    override val client = buildHttpClient()
    // ...
}
```

---

## Extending Existing SDKs

### Adding New Entity Type

1. **Add JSON Schema**:
   ```json
   // json-schemas/entity/data/newEntity.json
   {
     "$schema": "http://json-schema.org/draft-07/schema#",
     "title": "NewEntity",
     "type": "object",
     "properties": {
       "id": { "type": "string", "format": "uuid" },
       "name": { "type": "string" },
       ...
     }
   }
   ```

2. **Generate Models**:
   ```bash
   make generate-models
   ```

3. **Add API Client**:
   ```python
   class NewEntityAPI:
       ENTITY_PATH = "newEntities"

       def get_by_name(self, fqn: str) -> Optional[NewEntity]:
           ...
   ```

4. **Register in Main Client**:
   ```python
   class OpenMetadata:
       def new_entities(self) -> NewEntityAPI:
           return NewEntityAPI(self._client)
   ```

### Adding New Mixin

1. **Define Interface**:
   ```python
   class CustomBehaviorMixin:
       def custom_operation(self, entity_id: UUID) -> Result:
           ...
   ```

2. **Add to Main Client**:
   ```python
   class OpenMetadata(LineageMixin, TagMixin, CustomBehaviorMixin):
       ...
   ```

### Adding New Auth Provider

1. **Define Config Schema**:
   ```json
   {
     "title": "NewProviderConfig",
     "properties": {
       "apiKey": { "type": "string" },
       "endpoint": { "type": "string" }
     }
   }
   ```

2. **Implement Provider**:
   ```python
   class NewProvider(AuthenticationProvider):
       def __init__(self, config: NewProviderConfig):
           self._api_key = config.apiKey
           self._endpoint = config.endpoint

       def get_access_token(self) -> str:
           # Custom auth flow
           ...
   ```

3. **Register in Factory**:
   ```python
   AUTH_PROVIDERS = {
       AuthProvider.openmetadata: OpenMetadataJWTProvider,
       AuthProvider.google: GoogleProvider,
       AuthProvider.new_provider: NewProvider,  # Add here
   }
   ```

---

## Testing Strategy

### Unit Tests

```python
def test_table_get_by_name():
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "http://localhost:8585/api/v1/tables/name/db.schema.table",
            json={"id": "123", "name": "table", ...},
            status=200,
        )

        client = OpenMetadata(test_config)
        table = client.get_by_name(Table, "db.schema.table")

        assert table.name == "table"

def test_table_get_by_name_not_found():
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            "http://localhost:8585/api/v1/tables/name/missing",
            status=404,
        )

        client = OpenMetadata(test_config)
        table = client.get_by_name(Table, "missing")

        assert table is None
```

### Integration Tests

```python
@pytest.fixture
def openmetadata():
    """Connect to test OpenMetadata instance."""
    config = OpenMetadataConnection(
        hostPort=os.getenv("OM_HOST", "http://localhost:8585/api"),
        authProvider=AuthProvider.openmetadata,
        securityConfig=OpenMetadataJWTClientConfig(
            jwtToken=os.getenv("OM_TOKEN"),
        ),
    )
    client = OpenMetadata(config)
    client.health_check()
    return client

def test_create_and_get_table(openmetadata):
    create = CreateTable(
        name=f"test_table_{uuid4().hex[:8]}",
        databaseSchema="default.default",
        columns=[
            Column(name="id", dataType=DataType.INT),
            Column(name="name", dataType=DataType.STRING),
        ],
    )

    table = openmetadata.create_or_update(create)
    assert table.id is not None

    fetched = openmetadata.get_by_name(Table, table.fullyQualifiedName)
    assert fetched.name == create.name

    # Cleanup
    openmetadata.delete(Table, table.id, hard_delete=True)
```

---

## SDK Implementation Checklist

### Core Components
- [ ] Connection configuration with all auth providers
- [ ] HTTP client with retry, timeout, and error handling
- [ ] Authentication provider interface and implementations
- [ ] Model generation from JSON Schemas
- [ ] Health check endpoint

### Entity APIs
- [ ] Tables API
- [ ] Databases API
- [ ] Database Schemas API
- [ ] Database Services API
- [ ] Dashboard API
- [ ] Dashboard Services API
- [ ] Pipeline API
- [ ] Pipeline Services API
- [ ] Topic API
- [ ] Messaging Services API
- [ ] ML Model API
- [ ] ML Model Services API
- [ ] User/Team APIs
- [ ] Tag/Classification APIs

### Mixins
- [ ] Lineage operations
- [ ] Tag operations
- [ ] Owner operations
- [ ] Custom properties operations

### Quality
- [ ] Type safety throughout
- [ ] Comprehensive error handling
- [ ] Unit test coverage > 80%
- [ ] Integration test suite
- [ ] API documentation
- [ ] Usage examples

---

# Contributing to OpenMetadata

All SDK and connector development should be contributed back to the OpenMetadata community. This section covers setting up the development environment and contribution workflows.

## Development Environment Setup

### Prerequisites

| Tool | Version | Installation |
|------|---------|--------------|
| Docker | 20+ | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Java JDK | 21 | `brew install openjdk@21` or SDKMAN |
| Maven | 3.5+ | `brew install maven` |
| Python | 3.9-3.11 | System or pyenv |
| Node.js | 18.x | `brew install node@18` |
| Yarn | 1.22+ | `npm install -g yarn` |
| Antlr | 4.9.2 | `sudo make install_antlr_cli` |
| JQ | Latest | `brew install jq` |

### Verify Prerequisites

```bash
make prerequisites
```

### Clone and Setup

```bash
# Clone repository
git clone https://github.com/open-metadata/OpenMetadata
cd OpenMetadata

# Setup Python environment
python3 -m venv env
source env/bin/activate
pip install pre-commit

# Install development dependencies
make install_dev
make install_test
make precommit_install

# Generate models from schemas
make generate
```

### Start Development Stack

```bash
# MySQL + Elasticsearch (default)
docker compose -f docker/development/docker-compose.yml up mysql elasticsearch --build -d

# OR PostgreSQL + OpenSearch
docker compose -f docker/development/docker-compose-postgres.yml up postgresql opensearch --build -d
```

### Build and Run Server

```bash
# Build (skip tests for speed)
mvn clean install -DskipTests

# Bootstrap database
cd openmetadata-dist/target/openmetadata-*/
sh bootstrap/openmetadata-ops.sh drop-create

# Start server
sh bin/openmetadata-server-start.sh conf/openmetadata.yaml
```

Access at `http://localhost:8585`

---

## Repository Structure

```
OpenMetadata/
├── openmetadata-spec/                    # JSON Schemas (source of truth)
│   └── src/main/resources/json/schema/
│       ├── entity/                       # Entity definitions
│       │   ├── data/                     # Table, Database, Dashboard...
│       │   ├── services/                 # Service definitions
│       │   └── teams/                    # User, Team...
│       ├── api/                          # API request schemas
│       └── type/                         # Common types
│
├── openmetadata-service/                 # Java backend
│   └── src/main/java/org/openmetadata/service/
│       ├── resources/                    # REST API endpoints (Dropwizard)
│       ├── jdbi3/                        # Database access layer
│       ├── events/                       # Change event handlers
│       ├── security/                     # Auth & authorization
│       └── secrets/converter/            # ClassConverters for oneOf
│
├── ingestion/                            # Python ingestion framework
│   └── src/metadata/
│       ├── ingestion/
│       │   ├── source/                   # Source connectors
│       │   ├── processor/                # Processors
│       │   ├── sink/                     # Sinks
│       │   └── api/                      # Workflow APIs
│       └── generated/                    # Generated Pydantic models
│
└── openmetadata-ui/                      # React frontend
    └── src/main/resources/ui/
        ├── src/
        │   ├── utils/                    # ServiceUtils files
        │   └── locale/languages/         # i18n translations
        └── public/locales/               # Entity documentation
```

### Key Directories for Contributions

| Contribution Type | Primary Directory |
|-------------------|-------------------|
| New connector schema | `openmetadata-spec/.../connections/` |
| Connector Python code | `ingestion/src/metadata/ingestion/source/` |
| Java ClassConverter | `openmetadata-service/.../secrets/converter/` |
| UI connector config | `openmetadata-ui/.../utils/` |

---

## Contributing New Connectors

### When to Contribute vs Custom Connector

| Scenario | Approach |
|----------|----------|
| Connector useful to many users | **Contribute** to OpenMetadata |
| Single-use, custom data source | Build Custom Connector (not contributed) |

### Connector Development Workflow

```
1. Define JSON Schema
       ↓
2. Generate Types (Java/Python/TS)
       ↓
3. Implement Python Ingestion Code
       ↓
4. Create Java ClassConverter (if oneOf used)
       ↓
5. Apply UI Changes
       ↓
6. Write Tests
       ↓
7. Update Documentation
       ↓
8. Submit PR
```

### Step 1: Define JSON Schema

Create connection schema at:
```
openmetadata-spec/src/main/resources/json/schema/entity/services/connections/{source_type}/
```

**Example: `myDatabaseConnection.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://open-metadata.org/schema/entity/services/connections/database/myDatabaseConnection.json",
  "title": "MyDatabaseConnection",
  "description": "Connection to MyDatabase",
  "type": "object",
  "javaType": "org.openmetadata.schema.services.connections.database.MyDatabaseConnection",
  "definitions": {
    "myDatabaseType": {
      "description": "Service type",
      "type": "string",
      "enum": ["MyDatabase"],
      "default": "MyDatabase"
    },
    "myDatabaseScheme": {
      "description": "SQLAlchemy driver scheme",
      "type": "string",
      "enum": ["mydatabase+driver"],
      "default": "mydatabase+driver"
    }
  },
  "properties": {
    "type": {
      "$ref": "#/definitions/myDatabaseType"
    },
    "scheme": {
      "$ref": "#/definitions/myDatabaseScheme"
    },
    "hostPort": {
      "description": "Host and port",
      "type": "string"
    },
    "username": {
      "description": "Username",
      "type": "string"
    },
    "password": {
      "description": "Password",
      "type": "string",
      "format": "password"
    },
    "database": {
      "description": "Database name",
      "type": "string"
    },
    "supportsMetadataExtraction": {
      "$ref": "../connectionBasicType.json#/definitions/supportsMetadataExtraction"
    }
  },
  "additionalProperties": false,
  "required": ["hostPort"]
}
```

**Register in service schema** (`databaseService.json`):

```json
{
  "config": {
    "oneOf": [
      { "$ref": "./connections/database/myDatabaseConnection.json" }
    ]
  }
}
```

### Step 2: Generate Types

```bash
# Regenerate all models
mvn clean install -DskipTests

# Python models
cd ingestion
make generate

# TypeScript models (for UI)
cd openmetadata-ui/src/main/resources/ui
yarn install
./json2ts.sh path/to/myDatabaseConnection.json
```

### Step 3: Implement Python Ingestion

Create connector at:
```
ingestion/src/metadata/ingestion/source/database/mydatabase/
├── __init__.py
├── connection.py
├── metadata.py
└── service_spec.py
```

**`service_spec.py`**:

```python
from metadata.ingestion.source.database.mydatabase.metadata import MydatabaseSource
from metadata.utils.service_spec.default import DefaultDatabaseSpec

ServiceSpec = DefaultDatabaseSpec(metadata_source_class=MydatabaseSource)
```

**`connection.py`**:

```python
from metadata.generated.schema.entity.services.connections.database.myDatabaseConnection import (
    MyDatabaseConnection,
)
from metadata.ingestion.connections.builders import create_generic_db_connection
from metadata.ingestion.connections.test_connections import test_connection_db_schema_sources

def get_connection(connection: MyDatabaseConnection):
    return create_generic_db_connection(
        connection=connection,
        get_connection_url_fn=get_connection_url,
    )

def get_connection_url(connection: MyDatabaseConnection) -> str:
    return f"{connection.scheme.value}://{connection.username}:{connection.password}@{connection.hostPort}/{connection.database}"

def test_connection(engine) -> None:
    test_connection_db_schema_sources(engine)
```

**`metadata.py`**:

```python
from metadata.ingestion.source.database.common_db_source import CommonDbSourceService

class MydatabaseSource(CommonDbSourceService):
    """MyDatabase metadata extraction source."""

    @classmethod
    def create(cls, config_dict, metadata, pipeline_name=None):
        config = WorkflowSource.parse_obj(config_dict)
        return cls(config, metadata)

    # Override methods as needed for custom extraction logic
```

### Step 4: Create Java ClassConverter (if using `oneOf`)

Only needed if your schema uses `oneOf` for auth types:

```java
// openmetadata-service/.../secrets/converter/MyDatabaseConnectionClassConverter.java
package org.openmetadata.service.secrets.converter;

import org.openmetadata.schema.services.connections.database.MyDatabaseConnection;

public class MyDatabaseConnectionClassConverter extends ClassConverter {
    @Override
    public Object convert(Object object) {
        MyDatabaseConnection connection = (MyDatabaseConnection) JsonUtils.convertValue(object, MyDatabaseConnection.class);
        // Handle oneOf auth types if needed
        return connection;
    }
}
```

Register in `ClassConverterFactory.java`:

```java
Map.entry(MyDatabaseConnection.class, new MyDatabaseConnectionClassConverter())
```

### Step 5: Apply UI Changes

**Update ServiceUtils** (`DatabaseServiceUtils.ts`):

```typescript
import myDatabaseConnection from '../jsons/connectionSchemas/connections/database/myDatabaseConnection.json';

// In getDatabaseConfig switch:
case DatabaseServiceType.MyDatabase: {
    schema = myDatabaseConnection;
    break;
}
```

**Create documentation** at:
```
openmetadata-ui/.../public/locales/en-US/Database/MyDatabase.md
```

### Step 6: Write Tests

```python
# ingestion/tests/unit/source/database/test_mydatabase.py
import pytest
from metadata.ingestion.source.database.mydatabase.metadata import MydatabaseSource

def test_connection_url():
    connection = MyDatabaseConnection(
        hostPort="localhost:5432",
        username="user",
        password="pass",
        database="mydb",
    )
    url = get_connection_url(connection)
    assert url == "mydatabase+driver://user:pass@localhost:5432/mydb"
```

### Step 7: Update Documentation

Create comprehensive docs following OpenMetadata patterns:
- Connector overview
- Prerequisites
- Configuration steps
- Troubleshooting

---

## Type Generation

### JSON Schema → Multi-Language Models

```
JSON Schema (source of truth)
    ↓
┌───────────────────────────────────────────┐
│                                           │
↓               ↓               ↓           ↓
Java          Python        TypeScript    (Others)
POJOs         Pydantic      Interfaces
              Models
```

### Generation Commands

| Language | Tool | Command |
|----------|------|---------|
| Java | jsonschema2pojo | `mvn clean install` |
| Python | datamodel-codegen | `make generate` |
| TypeScript | quicktype | `./json2ts.sh <schema>` |

### Generated Output Locations

| Language | Output Directory |
|----------|------------------|
| Java | `openmetadata-spec/target/classes/org/openmetadata/schema/` |
| Python | `ingestion/src/metadata/generated/` |
| TypeScript | `openmetadata-ui/.../src/generated/` |

---

## Testing

### Python Tests

```bash
cd ingestion

# Install test dependencies
make install_test

# Run all tests with coverage
make coverage

# Run specific tests
pytest tests/unit/source/database/test_mydatabase.py -v

# Lint and format
make lint
make black
make isort
```

### Java Tests

```bash
# Run all tests
mvn test

# Run specific test class
mvn test -Dtest=MyDatabaseConnectionTest

# Skip tests during build
mvn clean install -DskipTests
```

### Integration Tests

Require running OpenMetadata server:

```bash
# Start server first
sh bin/openmetadata-server-start.sh conf/openmetadata.yaml

# Run integration tests
pytest tests/integration/ -v
```

### Pre-commit Hooks

```bash
# Install hooks
make precommit_install

# Run manually
pre-commit run --all-files
```

---

## Contribution Checklist

### New Connector
- [ ] JSON Schema defined with all required properties
- [ ] Schema registered in service type file
- [ ] Java/Python/TypeScript types generated
- [ ] Python Source implemented
- [ ] Java ClassConverter (if oneOf used)
- [ ] UI ServiceUtils updated
- [ ] UI documentation created
- [ ] Unit tests written
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Pre-commit hooks passing
- [ ] PR submitted with description

### SDK Extension
- [ ] JSON Schema updated/created
- [ ] Types regenerated
- [ ] Python/Java code implemented
- [ ] Tests written
- [ ] Documentation updated

---

## References

### SDK Documentation
- [OpenMetadata SDK Documentation](https://docs.open-metadata.org/latest/sdk)
- [OpenMetadata Python SDK](https://docs.open-metadata.org/latest/sdk/python)
- [OpenMetadata Java SDK](https://docs.open-metadata.org/latest/sdk/java)
- [OpenMetadata API (Swagger)](https://docs.open-metadata.org/swagger.html)

### Contributing
- [Build Prerequisites](https://docs.open-metadata.org/latest/developers/contribute/build-code-and-run-tests/prerequisites)
- [Build & Run Server](https://docs.open-metadata.org/latest/developers/contribute/build-code-and-run-tests/openmetadata-server)
- [Ingestion Framework](https://docs.open-metadata.org/latest/developers/contribute/build-code-and-run-tests/ingestion-framework)
- [Developing New Connectors](https://docs.open-metadata.org/latest/developers/contribute/developing-a-new-connector)
- [Architecture Overview](https://docs.open-metadata.org/latest/developers/architecture)
- [Code Layout](https://docs.open-metadata.org/latest/developers/architecture/code-layout)

### Source Code
- [OpenMetadata GitHub](https://github.com/open-metadata/OpenMetadata)
- [JSON Schemas](https://github.com/open-metadata/OpenMetadata/tree/main/openmetadata-spec/src/main/resources/json/schema)

### Related Skills
- `meta-sdk-patterns-eng` - Foundational SDK patterns
- `openmetadata-dev` - Using OpenMetadata SDKs/APIs
- `openmetadata-ops` - Administering OpenMetadata
