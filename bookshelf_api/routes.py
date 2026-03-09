from typing import Annotated
from fastapi import FastAPI, Depends
from pathlib import Path

from bookshelf_api.db import list_books


DEFAULT_DB = Path.home() / ".bookshelf.db"

app = FastAPI()

def path_to_db():
    return DEFAULT_DB

@app.get("/books")
def book_list(path: Annotated[Path, Depends(path_to_db)]):
    response = list_books(path)
    return response




