# <https://skillsmp.com/docs/api>

`GET /api/v1/skills/search`
> Search skills using keywords

|Parameter|Type|Required|Description|
|--|--|--|--|
|q|string|✓|Search query|
|page|number| - |Page number (default: 1)|
|limit|number| - |Items per page (default: 20, max: 100)|
| sortBy | string | - | Sort: stars |

`GET /api/v1/skills/ai-search`
> AI semantic search powered by Cloudflare AI

|Parameter|Type|Required|Description|
|--|--|--|--|
|q|string|✓|AI search query|

**Rate Limits**

- 500 requests per day per API key (resets at midnight UTC)
- Wildcard searches (e.g. *) are not supported

Every API response includes the following headers to help you track quota usage:

|Header|Description|
|--|--|
|X-RateLimit-Daily-Limit|Daily request limit (500)|
|X-RateLimit-Daily-Remaining|Remaining requests for today|

## Code Examples

```javascript
// Keyword Search
const response = await fetch(
  'https://skillsmp.com/api/v1/skills/search?q=SEO',
  {
    headers: {
      'Authorization': 'Bearer sk_live_skillsmp_UySlEpJqR1UYUBvUserFQcB8zzu3_S2mGSKxLysxuTY'
    }
  }
);

const data = await response.json();
console.log(data.data.skills);
```

```javascript
// AI Semantic Search
const response = await fetch(
  'https://skillsmp.com/api/v1/skills/ai-search?q=How+to+create+a+web+scraper',
  {
    headers: {
      'Authorization': 'Bearer sk_live_skillsmp_UySlEpJqR1UYUBvUserFQcB8zzu3_S2mGSKxLysxuTY'
    }
  }
);

const data = await response.json();
console.log(data.data.skills);
```

## Error Handling

> The API uses standard HTTP status codes and returns error details in JSON format

| Error Code | HTTP | Description |
|--|--|--|
| MISSING_API_KEY | 401 | API key not provided |
| INVALID_API_KEY | 401 | Invalid API key |
| MISSING_QUERY | 400 | Missing required query parameter |
| DAILY_QUOTA_EXCEEDED | 429 | Daily API quota exceeded |
| INTERNAL_ERROR | 500 | Internal server error |

```json
{
  "success": false,
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The provided API key is invalid"
  }
}
```
