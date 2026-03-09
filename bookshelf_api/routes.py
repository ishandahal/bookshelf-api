from fastapi import FastAPI

app = FastAPI()

@app.get("/books")
def book_list():
    # returning a dummy book
    return [
        {
            "id": 1, 
            "author": "test author", 
            "title": "test title",
        }
    ]
