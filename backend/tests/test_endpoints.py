from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest
from rope.api.main import app
from rope.api.sessions import get_request_session


@pytest.fixture
def test_client():
    return TestClient(app)


def override_get_request_session():
    session_id = {"session_id": "12345"}
    return session_id


def test_get_current_user(test_client, mocker):
    app.dependency_overrides[get_request_session] = override_get_request_session
    user = {
        "12345": {
            "email": "test@rice.edu",
            "is_manager": False,
            "is_admin": False,
        }
    }
    mocker.patch(
        "rope.api.sessions.sessions",
        user,
    )
    response = test_client.get("/user/current")
    data = response.json()
    assert response.status_code == 200
    assert data["email"] == "test@rice.edu"
    assert data["is_manager"] is False
    assert data["is_admin"] is False


def test_unauthenticated_user(test_client, mocker):
    app.dependency_overrides[get_request_session] = override_get_request_session
    user = {
        "ABCDEFG": {
            "email": "test@rice.edu",
            "is_manager": False,
            "is_admin": False,
        }
    }
    mocker.patch(
        "rope.api.sessions.sessions",
        user,
    )
    response = test_client.get("/user/current")
    assert response.status_code == 401


def test_delete_session(test_client, mocker):
    app.dependency_overrides[get_request_session] = override_get_request_session
    mocker.patch(
        "rope.api.sessions.sessions",
        {"12345": "ewfnweoif"},
    )
    response = test_client.delete("/session")
    assert response.status_code == 200
