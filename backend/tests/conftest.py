from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pytest

from rope.api.main import app
from rope.api.sessions import get_request_session
from rope.api import database


SQLALCHEMY_DATABASE_URL = "postgresql://pguser:pgpassword@localhost/ropedb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_client():
    return TestClient(app, follow_redirects=False)


@pytest.fixture
def db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def setup_admin_session(mocker):
    app.dependency_overrides[get_request_session] = override_admin_get_request_session
    admin = {
        "A1B2C3": {
            "email": "admin@rice.edu",
            "is_manager": False,
            "is_admin": True,
        }
    }
    mocker.patch(
        "rope.api.sessions.session_store",
        admin,
    )


@pytest.fixture
def setup_nonadmin_authenticated_user_session(
    setup_override_get_request_session,
    mocker,
):
    user = {
        "12345": {
            "email": "test@rice.edu",
            "is_manager": False,
            "is_admin": False,
        }
    }
    mocker.patch(
        "rope.api.sessions.session_store",
        user,
    )


@pytest.fixture
def setup_manager_session(mocker):
    app.dependency_overrides[get_request_session] = override_manager_get_request_session
    manager = {
        "Z9C8V7": {
            "email": "manager@rice.edu",
            "is_manager": True,
            "is_admin": False,
        }
    }
    mocker.patch(
        "rope.api.sessions.session_store",
        manager,
    )


@pytest.fixture
def setup_override_get_request_session():
    app.dependency_overrides[get_request_session] = override_get_request_session


@pytest.fixture
def setup_override_empty_get_request_session():
    app.dependency_overrides[get_request_session] = override_empty_get_request_session


# Overriding get_db used in the application code.
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_request_session():
    session_id = {"session_id": "12345"}
    return session_id


def override_admin_get_request_session():
    session_id = {"session_id": "A1B2C3"}
    return session_id


def override_manager_get_request_session():
    session_id = {"session_id": "Z9C8V7"}
    return session_id


def override_empty_get_request_session():
    session_id = {}
    return session_id


app.dependency_overrides[database.get_db] = override_get_db
