import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from bookshelf_api.db import (add_book, delete_book, init_db, list_books,
                              search_books, update_book)
from bookshelf_api.models import Book, BookNotFoundError

DEFAULT_DB = Path.home() / ".bookshelf.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(DEFAULT_DB)
    yield


app = FastAPI(lifespan=lifespan)

LOCAL_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5500",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5500",
]

FRONTEND_URL = os.environ.get("FRONTEND_URL")
allowed_origins = LOCAL_ORIGINS + ([FRONTEND_URL] if FRONTEND_URL else [])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)


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


SearchableFields = Literal["title", "author", "genre", "notes", "source"]


def path_to_db() -> Path:
    """Return the default database path."""
    return DEFAULT_DB


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


@app.get("/books")
def find_book(
    path: Annotated[Path, Depends(path_to_db)],
    search_term: Annotated[str | None, Query()] = None,
    field: Annotated[SearchableFields | None, Query()] = None,
) -> list[Book]:
    """Fetch all books from the database that match the search term. If field is provided
    only search in the field.

    Args:
        path: Database path, injected via dependency.
        search_term: Used to search in the table
        field: Column to be searched

    Returns:
        List of all books.
    """
    if search_term is not None:
        return search_books(path, search_term, field)
    return list_books(path)
