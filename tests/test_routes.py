from pathlib import Path

from bookshelf_api.db import add_book
from bookshelf_api.models import Book
from bookshelf_api.routes import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_book_list(db_path: Path):
    book1 = Book(author="Daniel Kahneman", title="Thinking Fast and Slow")
    add_book(db_path, book1)
    book2 = Book(author="Anonymous", title="Bible")
    add_book(db_path, book2)

    response = client.get("/books")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_add_book(db_path: Path):
    book_data = {"author": "Daniel Kahneman", "title": "Thinking Fast and Slow"}

    response = client.post("/books", json=book_data)

    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_add_book_no_title(db_path: Path):
    book_data = {"author": "Daniel Kahneman"}

    response = client.post("/books", json=book_data)

    assert response.status_code == 422


def test_remove_book(db_path: Path):
    book = Book(author="Daniel Kahneman", title="Thinking Fast and Slow")
    book_id = add_book(db_path, book)

    response = client.delete(f"/books/{book_id}")

    assert response.status_code == 204


def test_remove_book_invalid_id(db_path: Path):
    response = client.delete("/books/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_edit_book(db_path: Path):
    book = Book(author="D K", title="Thinking Fast and Slow")
    book_id = add_book(db_path, book)

    new_book_data = {"author": "Daniel Kahneman"}

    response = client.patch(f"/books/{book_id}", json=new_book_data)

    assert (
        response.status_code == 204
    )  # Using 204 instead of 200 because we do not send anything back on successful update


def test_edit_book_invalid_id(db_path: Path):
    new_book_data = {"author": "Daniel Kahneman"}

    response = client.patch(f"/books/{999}", json=new_book_data)

    assert response.status_code == 404  # Using 404 because the book_id is not found
    assert response.json()["detail"] == "Book not found"


def test_find_book_with_search_term(db_path: Path):
    book1 = Book(author="Daniel Kahneman", title="Thinking Fast and Slow")
    add_book(db_path, book1)
    book2 = Book(author="Anonymous", title="Bible")
    add_book(db_path, book2)

    search_term = "Fast"

    response = client.get("/books/", params={"search_term": search_term})

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_find_book_with_search_term_not_in_db(db_path: Path):
    book1 = Book(author="Daniel Kahneman", title="Thinking Fast and Slow")
    add_book(db_path, book1)
    book2 = Book(author="Anonymous", title="Bible")
    add_book(db_path, book2)

    search_term = "epic"

    response = client.get("/books/", params={"search_term": search_term})

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_find_book_with_term_and_field(db_path: Path):
    book1 = Book(author="Daniel Kahneman", title="Thinking Fast and Slow")
    add_book(db_path, book1)
    book2 = Book(author="Anonymous", title="Bible")
    add_book(db_path, book2)
    book3 = Book(author="Jack Riper", title="Bible things")
    add_book(db_path, book3)

    search_term = "Bible"
    field = "title"

    response = client.get(
        "/books/", params={"search_term": search_term, "field": field}
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
