from pathlib import Path

from fastapi.testclient import TestClient

from bookshelf_api.auth import hash_password
from bookshelf_api.db import create_user, init_db
from bookshelf_api.models import User
from bookshelf_api.routes import app, path_to_db

client = TestClient(app)


def make_db(tmp_path: Path) -> Path:
    """Create a fresh test DB with a known user."""
    db = tmp_path / "test.db"
    init_db(db)
    create_user(db, User(username="alice", hashed_password=hash_password("secret")))
    return db


def test_login_returns_token(tmp_path: Path):
    db = make_db(tmp_path)
    app.dependency_overrides[path_to_db] = lambda: db

    response = client.post(
        "/auth/login",
        data={"username": "alice", "password": "secret"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    app.dependency_overrides.clear()


def test_login_wrong_password(tmp_path: Path):
    db = make_db(tmp_path)
    app.dependency_overrides[path_to_db] = lambda: db

    response = client.post(
        "/auth/login",
        data={"username": "alice", "password": "wrong"},
    )

    assert response.status_code == 401

    app.dependency_overrides.clear()


def test_books_requires_auth():
    response = client.get("/books")

    assert response.status_code == 401
