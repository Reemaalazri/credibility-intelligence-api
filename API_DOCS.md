# API Documentation

## Base URL

Local development base URL:

`http://127.0.0.1:8000`

Deployed backend:

`https://credibility-intelligence-api.onrender.com`

Deployed frontend interacting with backend:

`https://credibility-intelligence-frontend.onrender.com`

## Authentication

The API uses JWT authentication for protected endpoints.

Protected endpoints include `/api/reports/` and `/api/score`.

Public endpoints include claims browsing and user registration/login.

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

Returns the main available API routes as URL strings.

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

- `search`

- `label`

- `ordering`

- `page`

Example:

`/api/claims/?search=vaccine`

Example response structure:

```json
{
  "count": 18,
  "next": http://127.0.0.1:8000/api/claims/?page=2,
  "previous": null,
  "results": [
    {
      "url": "https://credibility-intelligence-api.onrender.com/api/claims/9906/",
      "id": 9906,
      "liar_id": "11222.json",
      "label": "half-true",
      "statement": "Rhode Island will become just the second state to mandate the vaccine and the only state to do so by regulatory fiat, without public debate, and without consideration from the elected representatives of the people.",
      "subjects": "government-regulation,health-care",
      "speaker": "rhode-island-center-freedom-and-prosperity",
      "speaker_job_title": "",
      "state": "Rhode Island",
      "party": "organization",
      "barely_true_count": 1,
      "false_count": 0,
      "half_true_count": 1,
      "mostly_true_count": 0,
      "pants_on_fire_count": 0,
      "context": "news release",
      "split": "train",
      "created_at": "2026-03-10T17:27:15.720754Z"
    },
    {....}
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
  "created_at": "2026-03-11T03:41:00.268604Z",
  "updated_at": "2026-03-11T03:41:00.268613Z",
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

Note: report status moderation is intended for administrator use. Creator of the claim can modify the other fields.

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

## Interactive Documentation

Swagger UI:
`api/schema/swagger-ui`

ReDoc:
`/api/schema/redoc`

OpenAPI schema file:
`schema.yml`