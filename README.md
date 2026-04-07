# Bookshelf API

A RESTful API for tracking your reading list, built with FastAPI and SQLite.

Evolved from [bookshelf](../bookshelf) — a CLI tool for the same purpose — to explore web API development, dependency injection, and HTTP semantics.

## Dependencies

- [FastAPI](https://fastapi.tiangolo.com/) — web framework
- [uvicorn](https://www.uvicorn.org/) — ASGI server
- [python-jose](https://python-jose.readthedocs.io/) — JWT creation and verification
- [bcrypt](https://pypi.org/project/bcrypt/) — password hashing
- [python-multipart](https://pypi.org/project/python-multipart/) — form data parsing (required for OAuth2 login)

## Setup

```bash
uv sync
```

## Run

```bash
uv run uvicorn bookshelf_api.routes:app --reload
```

Interactive API docs are available at `http://localhost:8000/docs`.

## Test

```bash
uv run pytest -v
```

## Docker

Build the image:

```bash
docker build -t bookshelf-api .
```

Run the container:

```bash
docker run -p 3000:8080 bookshelf-api
```

The API will be available at `http://localhost:3000`. Interactive docs at `http://localhost:3000/docs`.

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | Yes (production) | `dev-secret-key-change-in-production` | Secret used to sign JWT tokens. Generate with `openssl rand -hex 32` |
| `ADMIN_USERNAME` | No | `admin` | Username for the seeded admin account |
| `ADMIN_PASSWORD` | No | `password` | Password for the seeded admin account |
| `FRONTEND_URL` | No | — | Allowed CORS origin for the deployed frontend |

The admin user is created automatically on startup if they don't already exist.

## Endpoints

> All `/books` endpoints require a valid `Authorization: Bearer <token>` header.
> Obtain a token from `POST /auth/login`.

| Method | Path          | Description                                                  | Status Codes |
|--------|---------------|--------------------------------------------------------------|--------------|  
| POST   | `/auth/login` | Authenticate and receive a JWT token                         | 200, 401     |
| GET    | `/books`      | List all books, or search with `?search_term=...&field=...`  | 200          |
| POST   | `/books`      | Add a new book                                               | 201, 422     |
| PATCH  | `/books/{id}` | Update a book (partial)                                      | 204, 404     |
| DELETE | `/books/{id}` | Delete a book by ID                                          | 204, 404     |

### Auth request body for POST /auth/login

Sent as `application/x-www-form-urlencoded`:

| Field | Type | Required | Description |
|---|---|---|---|
| `username` | string | Yes | Admin username |
| `password` | string | Yes | Admin password |

### Query parameters for GET /books

| Parameter     | Type   | Required | Description                                      |
|---------------|--------|----------|--------------------------------------------------|
| `search_term` | string | No       | Substring to search for                          |
| `field`       | string | No       | Limit search to a specific field: `title`, `author`, `genre`, `notes`, or `source` |