# API Documentation

## Base URL

Local development base URL:

`http://127.0.0.1:8000`

## Authentication

The API uses JWT authentication for protected endpoints.

### Register
`POST /api/auth/register/`

Example request:

```json
{
  "username": "testuser",
  "email": "user@example.com",
  "password": "SecurePass123"
}
```
### Login
`POST /api/auth/token/`

Example response:

```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token"
}
```

### Refresh Token
`POST /api/auth/token/refresh/`

Protected endpoints require:

`Authorization: Bearer <access_token>`

## 1. API Root
`GET /api/`

Returns the main available API routes.

Example response:

```json
{
  "claims": "/api/claims/",
  "reports": "/api/reports/",
  "score": "/api/score/",
  "register": "/api/auth/register/",
  "login": "/api/auth/token/"
}
```

## 2. Claims Endpoints
`GET /api/claims/`

Returns a paginated list of claims.

Supported query parameters:

- search

- label

- ordering

- page

Example:

`/api/claims/?search=vaccine`

Example response structure:

```json
{
  "count": 123,
  "next": "http://127.0.0.1:8000/api/claims/?page=2",
  "previous": null,
  "results": [
    {
      "id": 12790,
      "liar_id": "example.json",
      "label": "false",
      "statement": "Vaccines cause autism",
      "speaker": "example-speaker"
    }
  ]
}
```

`GET /api/claims/{id}/`

Returns one claim by ID.

Path parameter:

- id (integer)

`GET /api/claims/by-speaker/{speaker}/`

Returns claims matching a speaker.

Path parameter:

- speaker (string)

Example:

`/api/claims/by-speaker/trump/`

## 3. Reports Endpoints
These endpoints require authentication.

`GET /api/reports/`

Returns reports for the authenticated user.

Admin users can view all reports.

Supported query parameters:

- status

- risk_level

- page

`POST /api/reports/`

Creates a new report.

Example request:

```json
{
  "statement_text": "vaccines cause autism",
  "speaker": "Unknown",
  "report_reason": "false claim",
  "risk_score": 78,
  "risk_level": "medium",
  "status": "open"
}
```

Example response:

```json
{
  "id": 11,
  "statement_text": "vaccines cause autism",
  "speaker": "Unknown",
  "report_reason": "false claim",
  "risk_score": 78,
  "risk_level": "medium",
  "status": "open",
  "user": 1
}
```

`GET /api/reports/{id}/`

Returns one report by ID.

Path parameter:

- id (integer)


`PUT /api/reports/{id}/`

Replaces an existing report.

`PATCH /api/reports/{id}/`

Partially updates an existing report.

Example PATCH request:

```json
{
  "status": "reviewed"
}
```

`DELETE /api/reports/{id}/`

Deletes a report.

Permissions:

- users can manage their own reports

- admins can manage all reports

## 4. Score Endpoint
This endpoint requires authentication.

`POST /api/score/`

Analyses a claim and returns a credibility/risk result.

Example request:

```json
{
  "text": "vaccines cause autism"
}
```

Example response:

```json
{
  "claim": "vaccines cause autism",
  "summary": {
    "final_verdict": "likely_false",
    "final_credibility_score": 18,
    "final_risk_score": 82,
    "final_confidence": 74
  },
  "local_analysis": {},
  "external_analysis": {},
  "fusion": {}
}
```
## Error Handling

Common status codes:

- 200 OK

- 201 Created

- 400 Bad Request

- 401 Unauthorized

- 403 Forbidden

- 404 Not Found

- 429 Too Many Requests

Example custom error response:

```json
{
  "error": "text is required"
}
```

Example framework error response:

```json
{
  "detail": "Authentication credentials were not provided."
}
```




