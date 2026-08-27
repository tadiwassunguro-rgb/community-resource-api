import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    database = tmp_path / "test.db"

    return create_app({
        "TESTING": True,
        "DATABASE_PATH": str(database),
    })


@pytest.fixture
def client(app):
    return app.test_client()
