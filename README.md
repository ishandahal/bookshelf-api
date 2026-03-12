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

## Test

```bash
uv run pytest -v
```

## Endpoints

| Method | Path            | Description                          | Status Codes   |
|--------|-----------------|--------------------------------------|----------------|
| GET    | `/books`        | List all books, or search with `?search_term=...&field=...` | 200 |
| POST   | `/books`        | Add a new book                       | 201, 422       |
| PATCH  | `/books/{id}`   | Update a book (partial)              | 204, 404       |
| DELETE | `/books/{id}`   | Delete a book by ID                  | 204, 404       |
