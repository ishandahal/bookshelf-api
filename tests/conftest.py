from pathlib import Path

import pytest

from bookshelf_api.db import init_db
from bookshelf_api.routes import app, path_to_db

DEFAULT_DB_TEST = ".bookshelf.db"


@pytest.fixture
def db_path(tmp_path: Path):
    """Provide an initialized temp database and override the app dependency."""

    def path_to_testdb():
        return tmp_path / DEFAULT_DB_TEST

    app.dependency_overrides[path_to_db] = path_to_testdb
    db_path = path_to_testdb()
    init_db(db_path)
    yield db_path
    app.dependency_overrides.clear()
