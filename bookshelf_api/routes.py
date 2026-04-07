import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from pydantic import BaseModel

from bookshelf_api.auth import (
    create_token,
    decode_token,
    hash_password,
    verify_password,
)
from bookshelf_api.db import (
    add_book,
    create_user,
    delete_book,
    get_user,
    init_db,
    list_books,
    search_books,
    update_book,
)
from bookshelf_api.models import Book, BookNotFoundError, User

DEFAULT_DB = Path.home() / ".bookshelf.db"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(DEFAULT_DB)
    _seed_admin(DEFAULT_DB)
    yield


def _seed_admin(db_path: Path) -> None:
    """Create the admin user from env vars if they don't exist yet."""
    username = os.environ.get("ADMIN_USERNAME", "admin")
    password = os.environ.get("ADMIN_PASSWORD", "password")
    create_user(
        db_path, User(username=username, hashed_password=hash_password(password))
    )


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
    allow_headers=["Content-Type", "Authorization"],
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


def get_current_user(
    path: Annotated[Path, Depends(path_to_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """Validate the JWT and return the current user.

    Raises:
        HTTPException 401: If the token is missing, invalid, or the user doesn't exist.
    """
    try:
        username = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user(path, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ── Auth ──────────────────────────────────────────────────────────────────────


@app.post("/auth/login")
def login(
    path: Annotated[Path, Depends(path_to_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dict[str, str]:
    """Authenticate and return a JWT token.

    Args:
        path: Database path, injected via dependency.
        form_data: Username and password from the request form.

    Returns:
        Dict with access_token and token_type.

    Raises:
        HTTPException 401: If credentials are invalid.
    """
    user = get_user(path, form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_token(form_data.username), "token_type": "bearer"}


# ── Books (protected) ─────────────────────────────────────────────────────────


@app.post("/books", status_code=201)
def create_book(
    path: Annotated[Path, Depends(path_to_db)],
    book_data: BookCreate,
    _: Annotated[User, Depends(get_current_user)],
) -> dict[str, int]:
    """Add a book to the database."""
    book = Book(**book_data.model_dump())
    book_id = add_book(path, book)
    return {"id": book_id}


@app.delete("/books/{book_id}", status_code=204)
def remove_book(
    path: Annotated[Path, Depends(path_to_db)],
    book_id: int,
    _: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a book from the database."""
    try:
        delete_book(path, book_id)
    except BookNotFoundError:
        raise HTTPException(status_code=404, detail="Book not found")


@app.patch("/books/{book_id}", status_code=204)
def edit_book(
    path: Annotated[Path, Depends(path_to_db)],
    book_id: int,
    new_book_data: BookUpdate,
    _: Annotated[User, Depends(get_current_user)],
) -> None:
    """Update book details in the database."""
    new_book_data_dict = new_book_data.model_dump(exclude_none=True)
    try:
        update_book(path, book_id, new_book_data_dict)
    except BookNotFoundError:
        raise HTTPException(status_code=404, detail="Book not found")


@app.get("/books")
def find_book(
    path: Annotated[Path, Depends(path_to_db)],
    _: Annotated[User, Depends(get_current_user)],
    search_term: Annotated[str | None, Query()] = None,
    field: Annotated[SearchableFields | None, Query()] = None,
) -> list[Book]:
    """Fetch all books, with optional search."""
    if search_term is not None:
        return search_books(path, search_term, field)
    return list_books(path)
