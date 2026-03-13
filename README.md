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

## Live Demo
Live API:

```http
https://credibility-intelligence-api.onrender.com/api/
```

Live API with frontend
```http
https://credibility-intelligence-frontend.onrender.com 
```

Swagger Documentation:
```http
https://credibility-intelligence-api.onrender.com/api/schema/swagger-ui/
```

PDF API Documentation:
[API Documentation (PDF)](API_DOCS.pdf)

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

Wang, W.Y., 2017. "Liar, Liar Pants on Fire": A New Benchmark Dataset for Fake News Detection. In: Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers). Vancouver, Canada, 30 July - 4 August 2017. Stroudsburg: Association for Computational Linguistics, pp.422-426. Kaggle dataset: https://www.kaggle.com/datasets/doanquanvietnamca/liar-dataset 

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

## Installation and Setup

Follow these steps to run the project locally.

### 1. Clone the repository

```bash
git clone https://github.com/Reemaalazri/credibility-intelligence-api.git
cd credibility-intelligence-api
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Mac/Linux

```bash
source venv/bin/activate
```

Windows
```bash
venv\Scripts\activate 
``` 

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash 
python manage.py migrate
```

### 5. Import the dataset

The project includes a dataset import script which loads the LIAR dataset into the database.

```bash 
python manage.py import_dataset
```

### 6. (Optional) Create an admin account

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

The API will be available at:

```http
http://127.0.0.1:8000/api/
```

## API Documentation (Local)
When the server is running, interactive documentation is available at:

Swagger UI
```
http://127.0.0.1:8000/api/schema/swagger-ui/
```

ReDoc documentation
```
http://127.0.0.1:8000/api/schema/redoc/
```

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
"claim": "Vaccines cause autism",
"summary": {
  "final_verdict": "likely_false",
  "final_credibility_score": 0,
  "final_risk_score": 100,
  "final_confidence": 56
}
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

## Deployment
The API is deployed on Render.

Live backend API:

```http
https://credibility-intelligence-api.onrender.com/api/
```

Interactive API documentation:

```http
https://credibility-intelligence-api.onrender.com/api/schema/swagger-ui/
```

The system can be accessed directly through the deployed backend or via the frontend interface.

The frontend interface communicates with the deployed backend API.

## Repository Structure

Main Components: 

```
credibility-intelligence-api/
│
├── src/claims/                # dataset models, views and serializers
├── src/credibility_api/       # Django project configuration
├── frontend/                  # static web interface
├── data/                      # LIAR dataset files
├── src/manage.py
├── requirements.txt
├── README.md
├── API_DOCS.pdf
└── schema.yml
```

## Future Improvements
- enhanced frontend interface and UI improvements
- interactive data visualisation dashboards
- machine learning credibility models
- additional fact-checking data sources
- improved external fact-check integration

## API Documentation

The API documentation is generated automatically from the OpenAPI specification.

Available documentation resources include:

- **Swagger UI** – Interactive interface for exploring endpoints and testing API requests.
- **ReDoc** – Structured reference view of the API specification.
- **Swagger Documentation (PDF)** – Exported PDF version of the OpenAPI documentation for offline review.

[API Documentation (PDF)](API_DOCS.pdf)

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

