
from bookshelf_api.routes import app 
from fastapi.testclient import TestClient

client = TestClient(app)

def test_book_list():
    response = client.get("/books")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1, 
            "author": "test author", 
            "title": "test title",
        }
    ]

