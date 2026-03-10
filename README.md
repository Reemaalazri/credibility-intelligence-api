# Credibility Intelligence API
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Django](https://img.shields.io/badge/Django-REST%20Framework-green)
![API](https://img.shields.io/badge/API-REST-orange)
![Database](https://img.shields.io/badge/Database-SQLite-lightgrey)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

A data-driven REST API for detecting and analysing misleading claims using a structured dataset and credibility scoring system.

This project was developed for COMP3011 – Web Services and Web Data at the University of Leeds.

The system provides endpoints for browsing claims, analysing credibility scores and allowing authenticated users to report suspicious or misleading content.

## Project Overview
The API enables users to:
- Browse a dataset of claims
- Search and filter claims
- Analyse claim credibility using a scoring endpoint
- Submit reports about misleading statements
- Manage their own reports
- Allow administrators to moderate reports

The system follows a RESTful architecture, returning structured JSON responses and using standard HTTP status codes.

## Features
- RESTful API architecture using Django REST Framework
- Public claims dataset with filtering, search and pagination
- Credibility scoring endpoint for analysing claims
- User reporting system with full CRUD functionality
- JWT authentication and access control
- Role-based permissions for users and administrators
- Automated API testing using Django test framework

## Technology Stack
1- Backend
- Python
- Django
- Django REST Framework
- SimpleJWT Authentication

2- Database
- SQLite

3- Frontend
- HTML
- CSS
- JavaScript (Fetch API)

4- Development Tools
- Git / GitHub
- Postman / DRF Browsable API
- Generative AI tools for planning and debugging

## Dataset
This API uses the **LIAR** dataset, a publicly available dataset for fact-checking and misinformation research.

The dataset contains labelled political claims with metadata including:
- speaker
- statement text
- label (true/false)
- context
- subjects
- timestamp
- political affiliation
- historical credibility counts

The dataset was originally collected from PolitiFact and is widely used in misinformation detection research.

The dataset was imported into the project database and exposed through the /api/claims/ endpoint.

The dataset was preprocessed and imported into the SQLite database using a custom data import script.

### Dataset Source

Wang, W. Y. (2017). “Liar, Liar Pants on Fire: A New Benchmark Dataset for Fake News Detection.” Proceedings of the Annual Meeting of the Association for Computational Linguistics (ACL).

Dataset available from: https://www.cs.ucsb.edu/~william/data/liar_dataset.zip

## API Architecture
The system contains three main functional components.

### 1. Claims Dataset API
Public read-only endpoints providing access to claim records.

**Features:**
- pagination
- filtering
- full-text search
- ordering

### 2. Credibility Scoring API
Evaluates the credibility risk of a claim.

The scoring endpoint analyses text input and returns:
- credibility score
- risk level classification

### 3. User Reporting System
Authenticated users can submit reports about potentially misleading claims.

**Features:**
- create reports
- view personal reports
- update report status
- delete reports
- admin moderation

This model implements full CRUD functionality.

## Interface Preview
(Screenshot of the web interface interacting with the API)

## Requirements 
- Python 3.10+
- pip
- virtualenv

## Quick Start
```bash
git clone https://github.com/YOUR_USERNAME/credibility-intelligence-api.git
cd credibility-intelligence-api

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

Then open:
```http
http://127.0.0.1:8000/api/
```

**Clone the repository**

**Create virtual environment**

**Install dependencies**

**Run database migrations**

**Run the development server**

**Access the API**

## Authentication
The API uses JWT authentication.

**Register a user**

```http
POST /api/auth/register/
```
Example request
```json
{
"username": "testuser",
"email": "user@email.com",
"password": "SecurePass123"
}
```
**Login**
```http
POST /api/auth/token/
```
Response
```json
{
"access": "jwt_access_token",
"refresh": "jwt_refresh_token"
}
```
Use the token in requests:
```
Authorization: Bearer <access_token>
```

## API Endpoints
### Claims

| Endpoint                            | Method | Description       |
| ----------------------------------- | ------ | ----------------- |
| `/api/claims/`                      | GET    | Browse claims     |
| `/api/claims/<id>/`                 | GET    | Retrieve claim    |
| `/api/claims/by-speaker/<speaker>/` | GET    | Filter by speaker |

Supports:
- search
- filtering
- ordering
- pagination

### Score endpoint
```html
POST /api/score/
```
Request
```json
{
"text": "vaccines cause autism"
}
```
Response 
```json
{
"score": 78,
"risk_level": "medium"
}
```
### Reports (Authenticated)

| Endpoint             | Method    | Description       |
| -------------------- | --------- | ----------------- |
| `/api/reports/`      | GET       | List user reports |
| `/api/reports/`      | POST      | Create report     |
| `/api/reports/<id>/` | GET       | Retrieve report   |
| `/api/reports/<id>/` | PUT/PATCH | Update report     |
| `/api/reports/<id>/` | DELETE    | Delete report     |

Permissions:
- users see only their own reports
- admins can see all reports

## Example API Response
Request:
```http
GET /api/claims/12790/
```
Response:
```json
{
"id": 12790,
"statement": "Vaccines cause autism",
"speaker": "example speaker",
"label": "false",
"context": "public speech"
}
```
## Error Handling
The API returns standard HTTP status codes.

Examples:
```
200 OK
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
429 Too Many Requests
```

## Security Features
- JWT authentication
- ownership validation for reports
- admin-only moderation
- request throttling
- pagination for dataset queries

## Testing
Run automated tests with:
```bash
python manage.py test
```
The test suite verifies:
- authentication
- report ownership
- CRUD operations
- API responses

## Repository Structure
```
credibility-intelligence-api/
│
├── claims/
├── credibility_api/
├── manage.py
├── requirements.txt
├── README.md
└── API_DOCS.md
```

## Future Improvements
- frontend interface for user interaction - next
- data visualisation dashboards
- machine learning credibility model
- deployment to cloud platform

## API Documentation
Full API documentation is available here:
- [API Documentation (Markdown)](API_DOCS.md)
- [API Documentation (PDF)](API_DOCS.pdf)

A generated OpenAPI schema is also included:
- [OpenAPI Schema](schema.yml)

Interactive documentation is available locally when the server is running:
- `/api/schema/swagger-ui/`
- `/api/schema/redoc/`

## Generative AI Usage
Generative AI tools were used during development for:
- planning architecture
- debugging implementation
- understanding framework behaviour
- improving documentation clarity

All usage complies with the coursework guidelines and will be declared in the technical report.

## Author
Reema Al-Azri

BSc Computer Science with Artificial Intelligence

University of Leeds

