from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI

from bookshelf_api.db import list_books
from bookshelf_api.models import Book

DEFAULT_DB = Path.home() / ".bookshelf.db"

app = FastAPI()


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
