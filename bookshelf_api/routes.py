from pathlib import Path
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from bookshelf_api.db import add_book, delete_book, list_books, update_book
from bookshelf_api.models import Book, BookNotFoundError

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


class BookUpdate(BaseModel):
    """Schema for editing an existing book."""

    title: Optional[str] = None
    author: Optional[str] = None
    status: Optional[str] = None
    genre: Optional[str] = None
    notes: Optional[str] = None
    source: Optional[str] = None


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


@app.delete("/books/{book_id}", status_code=204)
def remove_book(path: Annotated[Path, Depends(path_to_db)], book_id: int) -> None:
    """Delete a book from the database.

    Args:
        path: Database path, injected via dependency.
        book_id: ID of the book to delete.

    Raises:
        HTTPException: If the book is not found.
    """
    try:
        delete_book(path, book_id)
    except BookNotFoundError:
        raise HTTPException(status_code=404, detail="Book not found")


@app.patch("/books/{book_id}", status_code=204)
def edit_book(
    path: Annotated[Path, Depends(path_to_db)], book_id: int, new_book_data: BookUpdate
) -> None:
    """Update book details from the database.

    Args:
        path: Database path, injected via dependency.
        book_id: ID of the book to be updated.
        new_book_data: field and values of book to be updated.

    Raises:
        HTTPException: If the book is not found.
    """
    new_book_data_dict = new_book_data.model_dump(exclude_none=True)

    try:
        update_book(path, book_id, new_book_data_dict)
    except BookNotFoundError:
        raise HTTPException(status_code=404, detail="Book not found")
