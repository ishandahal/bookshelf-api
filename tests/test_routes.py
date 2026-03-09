from pathlib import Path

from bookshelf_api.db import add_book, init_db
from bookshelf_api.models import Book
from bookshelf_api.routes import app, path_to_db
from fastapi.testclient import TestClient

DEFAULT_DB_TEST = ".bookshelf.db"

client = TestClient(app)


def test_book_list(tmp_path: Path):
    def path_to_testdb():
        return tmp_path / DEFAULT_DB_TEST

    db_path = path_to_testdb()
    init_db(db_path)

    app.dependency_overrides[path_to_db] = path_to_testdb

    try:
        book1 = Book(author="Daniel Kahneman", title="Thinking Fast and Slow")
        add_book(db_path, book1)
        book2 = Book(author="Anonymous", title="Bible")
        add_book(db_path, book2)

        response = client.get("/books")

        assert response.status_code == 200
        assert len(response.json()) == 2

    finally:
        app.dependency_overrides.clear()
