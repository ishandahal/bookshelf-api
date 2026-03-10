from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from bookshelf_api.db import add_book, list_books
from bookshelf_api.models import Book

DEFAULT_DB = Path.home() / ".bookshelf.db"

app = FastAPI()


class BookCreate(BaseModel):
    """Schema for creating a new book."""

    title: str
    author: str
    status: str = "want-to-read"
    genre: str = ""
    notes: str = ""
    source: str = ""


def path_to_db() -> Path:
    """Return the default database path."""
    return DEFAULT_DB


@app.get("/books")
def book_list(path: Annotated[Path, Depends(path_to_db)]) -> list[Book]:
    """Fetch all books from the database.

    Args:
        path: Database path, injected via dependency.

    Returns:
        List of all books.
    """
    return list_books(path)


@app.post("/books", status_code=201)
def create_book(
    path: Annotated[Path, Depends(path_to_db)], book_data: BookCreate
) -> dict[str, int]:
    """Add a book to the database.

    Args:
        path: Database path, injected via dependency.
        book_data: Book fields from the request body.

    Returns:
        Dictionary containing the newly created book's id.
    """
    book = Book(**book_data.model_dump())
    book_id = add_book(path, book)
    return {"id": book_id}
