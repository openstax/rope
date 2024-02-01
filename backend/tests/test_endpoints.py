from fastapi.testclient import TestClient
import pytest
from rope.api.main import app
from rope.api.sessions import get_request_session, sessions
from rope.api.database import SessionLocal
from rope.db.schema import UserAccount


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clear_database_table(db):
    db.query(UserAccount).delete()
    db.commit()


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


def test_google_login(test_client, db, mocker):
    google_oauth_mock = mocker.Mock()
    google_oauth_mock.verify_oauth2_token.return_value = {
        "hd": "rice.edu",
        "email": "test@rice.edu",
    }
    mocker.patch(
        "rope.api.auth.id_token.verify_oauth2_token",
        google_oauth_mock.verify_oauth2_token,
    )
    db_user = UserAccount(email="test@rice.edu", is_manager=False, is_admin=False)
    db.add(db_user)
    db.commit()
    response = test_client.post("/session", json={"token": "fp2m3fpwimef"})
    session_id = list(sessions.keys())[0]
    user_data = sessions[session_id]
    assert response.status_code == 200
    assert user_data["email"] == "test@rice.edu"
    assert user_data["is_manager"] is False
    assert user_data["is_admin"] is False
