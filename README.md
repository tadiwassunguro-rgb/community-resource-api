# Community Resource API

A lightweight Python/Flask REST API for tracking community resources and requests.

## Why I built it

Small community organizations often track available resources and requests with spreadsheets or chat messages. This project provides a simple API for creating resources, recording requests, checking availability, and exposing operational health information.

## Features

- REST API built with Flask
- SQLite persistence
- CRUD operations for resources
- Resource request workflow
- Input validation and clear error responses
- Health and readiness endpoints
- Basic operational metrics
- Structured application logging
- Automated tests with pytest
- Docker support
- Environment-based configuration

## Project structure

```text
community-resource-api/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── routes.py
│   └── services.py
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── run.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
└── README.md
```

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python run.py
```

The API runs at `http://127.0.0.1:5000`.

## Example requests

Create a resource:

```bash
curl -X POST http://127.0.0.1:5000/api/resources \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"School laptops\",\"category\":\"education\",\"quantity\":10}"
```

List resources:

```bash
curl http://127.0.0.1:5000/api/resources
```

Request a resource:

```bash
curl -X POST http://127.0.0.1:5000/api/requests \
  -H "Content-Type: application/json" \
  -d "{\"resource_id\":1,\"requester\":\"Community Centre\",\"quantity\":2}"
```

Health check:

```bash
curl http://127.0.0.1:5000/health
```

Metrics:

```bash
curl http://127.0.0.1:5000/metrics
```

## Run tests

```bash
pytest -q
```

## Docker

```bash
docker build -t community-resource-api .
docker run -p 5000:5000 community-resource-api
```

## Future improvements

- Authentication and role-based access
- PostgreSQL for production deployments
- Redis-backed rate limiting
- Prometheus-compatible metrics
- CI/CD with GitHub Actions
- A small JavaScript frontend
- Audit logs for resource changes
