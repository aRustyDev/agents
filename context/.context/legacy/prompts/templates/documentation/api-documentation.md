---
name: API Documentation Template
module_type: template
scope: temporary
priority: low
triggers: ["api docs", "api documentation", "endpoint documentation", "rest api docs", "openapi"]
dependencies: []
conflicts: []
version: 1.0.0
---

# API Documentation Template

## Purpose
Comprehensive template for documenting RESTful APIs, including endpoints, authentication, request/response formats, and examples.

## Template

```markdown
# [API Name] API Documentation

## Overview
[Brief description of what this API does and its main purpose]

**Base URL**: `https://api.example.com/v1`  
**Version**: 1.0.0  
**Last Updated**: [Date]

## Table of Contents
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Users](#users)
  - [Resources](#resources)
- [Webhooks](#webhooks)
- [SDK/Libraries](#sdklibraries)
- [Changelog](#changelog)

## Authentication

This API uses [Bearer token/OAuth 2.0/API Key] authentication.

### Obtaining Credentials
```bash
curl -X POST https://api.example.com/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret"
  }'
```

### Using Authentication
Include the authentication token in the Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Example Request
```bash
curl -X GET https://api.example.com/v1/users \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Rate Limiting

API calls are limited to:
- **Standard**: 1000 requests per hour
- **Premium**: 10000 requests per hour

Rate limit information is included in response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found",
    "details": {
      "resource_type": "user",
      "resource_id": "123"
    },
    "request_id": "req_abcd1234"
  }
}
```

### Common Error Codes
| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | BAD_REQUEST | Invalid request parameters |
| 401 | UNAUTHORIZED | Missing or invalid authentication |
| 403 | FORBIDDEN | Valid auth but insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |

## Endpoints

### Users

#### List Users
Get a paginated list of users.

**Endpoint**: `GET /users`

**Query Parameters**:
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| page | integer | No | Page number | 1 |
| limit | integer | No | Items per page (max 100) | 20 |
| sort | string | No | Sort field (name, created_at) | created_at |
| order | string | No | Sort order (asc, desc) | desc |

**Response**:
```json
{
  "data": [
    {
      "id": "usr_123",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "admin",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

**Example Request**:
```bash
curl -X GET "https://api.example.com/v1/users?page=2&limit=50" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get User
Retrieve a specific user by ID.

**Endpoint**: `GET /users/{user_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | string | Unique user identifier |

**Response**:
```json
{
  "id": "usr_123",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "admin",
  "metadata": {
    "department": "Engineering",
    "location": "San Francisco"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Create User
Create a new user.

**Endpoint**: `POST /users`

**Request Body**:
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "SecurePassword123!",
  "role": "user",
  "metadata": {
    "department": "Marketing",
    "location": "New York"
  }
}
```

**Validation Rules**:
- `name`: Required, 2-100 characters
- `email`: Required, valid email format, unique
- `password`: Required, min 8 characters, must contain uppercase, lowercase, number
- `role`: Required, enum: ["admin", "user", "readonly"]

**Response**: `201 Created`
```json
{
  "id": "usr_456",
  "name": "Jane Smith",
  "email": "jane@example.com",
  "role": "user",
  "created_at": "2024-01-15T14:20:00Z"
}
```

#### Update User
Update user information.

**Endpoint**: `PATCH /users/{user_id}`

**Request Body** (all fields optional):
```json
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "metadata": {
    "department": "Sales"
  }
}
```

**Response**: `200 OK`
Returns updated user object.

#### Delete User
Delete a user account.

**Endpoint**: `DELETE /users/{user_id}`

**Response**: `204 No Content`

### Resources

#### Search Resources
Search for resources with filtering.

**Endpoint**: `POST /resources/search`

**Request Body**:
```json
{
  "query": "example",
  "filters": {
    "type": ["document", "image"],
    "created_after": "2024-01-01",
    "tags": ["important", "public"]
  },
  "sort": {
    "field": "relevance",
    "order": "desc"
  },
  "pagination": {
    "page": 1,
    "limit": 20
  }
}
```

**Response**:
```json
{
  "results": [
    {
      "id": "res_789",
      "title": "Example Document",
      "type": "document",
      "score": 0.95,
      "highlights": {
        "content": ["This is an <em>example</em> of..."]
      }
    }
  ],
  "facets": {
    "type": {
      "document": 45,
      "image": 12
    }
  },
  "total": 57
}
```

## Webhooks

### Webhook Events
Subscribe to real-time events via webhooks.

**Available Events**:
- `user.created`
- `user.updated`
- `user.deleted`
- `resource.created`
- `resource.updated`

### Webhook Payload
```json
{
  "id": "evt_abc123",
  "type": "user.created",
  "created": "2024-01-15T10:30:00Z",
  "data": {
    "object": {
      "id": "usr_123",
      "name": "John Doe"
    }
  }
}
```

### Webhook Signature Verification
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## SDK/Libraries

Official SDKs available for:
- **JavaScript/TypeScript**: `npm install @example/api-sdk`
- **Python**: `pip install example-api`
- **Go**: `go get github.com/example/api-go`
- **Ruby**: `gem install example-api`

### Quick Start (JavaScript)
```javascript
const ExampleAPI = require('@example/api-sdk');

const client = new ExampleAPI({
  apiKey: 'YOUR_API_KEY'
});

// List users
const users = await client.users.list({
  page: 1,
  limit: 20
});

// Create user
const newUser = await client.users.create({
  name: 'John Doe',
  email: 'john@example.com'
});
```

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial API release
- User management endpoints
- Resource search functionality
- Webhook support

### Version 0.9.0 (2023-12-01)
- Beta release
- Basic authentication
- Core endpoints
```

## Usage Examples

### Minimal API Documentation
```markdown
# Simple CRUD API

**Base URL**: `http://localhost:3000/api`

## Authentication
Include API key in header: `X-API-Key: your_key`

## Endpoints

### GET /items
Returns all items.

**Response**:
```json
[
  {
    "id": 1,
    "name": "Item 1",
    "price": 10.99
  }
]
```

### GET /items/{id}
Returns specific item.

### POST /items
Create new item.

**Body**:
```json
{
  "name": "New Item",
  "price": 15.99
}
```

### PUT /items/{id}
Update item.

### DELETE /items/{id}
Delete item.
```

### OpenAPI/Swagger Format
```yaml
openapi: 3.0.0
info:
  title: Example API
  version: 1.0.0
  description: API for managing resources

servers:
  - url: https://api.example.com/v1
    description: Production server

paths:
  /users:
    get:
      summary: List users
      operationId: listUsers
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        email:
          type: string
      required:
        - id
        - name
        - email

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer

security:
  - bearerAuth: []
```

## Best Practices

### DO
- ✅ Include real examples for every endpoint
- ✅ Document all error responses
- ✅ Specify rate limits clearly
- ✅ Version your API
- ✅ Provide SDK examples

### DON'T
- ❌ Use technical jargon without explanation
- ❌ Omit authentication details
- ❌ Forget edge cases
- ❌ Mix versions in one doc
- ❌ Assume prior knowledge

## Documentation Tools

### API Documentation Generators
- **Swagger/OpenAPI**: Industry standard specification
- **Postman**: Collections with documentation
- **Slate**: Beautiful static documentation
- **Redoc**: OpenAPI documentation
- **Docusaurus**: Full documentation sites

### Testing Tools
- **Postman**: API testing and documentation
- **Insomnia**: REST client with docs
- **HTTPie**: Command-line HTTP client
- **curl**: Universal HTTP client

---
*Well-documented APIs are easier to adopt, maintain, and scale. This template provides a comprehensive structure for any REST API documentation.*