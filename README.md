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

| Method | Path     | Description       |
|--------|----------|-------------------|
| GET    | `/books` | List all books    |

*More endpoints coming soon.*
