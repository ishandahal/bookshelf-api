# Bookshelf API

A RESTful API for tracking your reading list, built with FastAPI and SQLite.

Evolved from [bookshelf](../bookshelf) — a CLI tool for the same purpose — to explore web API development, dependency injection, and HTTP semantics.

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

## Endpoints

| Method | Path          | Description                                                  | Status Codes |
|--------|---------------|--------------------------------------------------------------|--------------|
| GET    | `/books`      | List all books, or search with `?search_term=...&field=...`  | 200          |
| POST   | `/books`      | Add a new book                                               | 201, 422     |
| PATCH  | `/books/{id}` | Update a book (partial)                                      | 204, 404     |
| DELETE | `/books/{id}` | Delete a book by ID                                          | 204, 404     |

### Query parameters for GET /books

| Parameter     | Type   | Required | Description                                      |
|---------------|--------|----------|--------------------------------------------------|
| `search_term` | string | No       | Substring to search for                          |
| `field`       | string | No       | Limit search to a specific field: `title`, `author`, `genre`, `notes`, or `source` |