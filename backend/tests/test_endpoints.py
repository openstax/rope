from fastapi.testclient import TestClient
import pytest
from rope.api.main import app
from rope.api.sessions import get_request_session, session_store
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


def override_get_request_session():
    session_id = {"session_id": "12345"}
    return session_id


def override_admin_get_request_session():
    session_id = {"session_id": "A1B2C3"}
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
        "rope.api.sessions.session_store",
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
        "rope.api.sessions.session_store",
        user,
    )
    response = test_client.get("/user/current")
    assert response.status_code == 401


def test_delete_session(test_client, mocker):
    app.dependency_overrides[get_request_session] = override_get_request_session
    session_store = {"12345": "ewfnweoif"}
    mocker.patch(
        "rope.api.sessions.session_store",
        session_store,
    )
    response = test_client.delete("/session")
    assert response.status_code == 200
    assert session_store.get("12345") is None


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
    session_id = list(session_store.keys())[0]
    user_data = session_store[session_id]
    assert response.status_code == 200
    assert user_data["email"] == "test@rice.edu"
    assert user_data["is_manager"] is False
    assert user_data["is_admin"] is False


def test_get_all_users(test_client, db, setup_admin_session):
    db_user = UserAccount(email="test@rice.edu", is_manager=False, is_admin=False)
    db_user2 = UserAccount(email="admin@rice.edu", is_manager=False, is_admin=True)
    db.add(db_user)
    db.add(db_user2)
    db.commit()
    response = test_client.get("/user")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 2
    assert data[0].get("id") is not None
    assert data[1].get("id") is not None
    assert data[0].get("email") == "test@rice.edu"
    assert data[0].get("is_manager") is False
    assert data[0].get("is_admin") is False
    assert data[1].get("email") == "admin@rice.edu"
    assert data[1].get("is_manager") is False
    assert data[1].get("is_admin") is True


def test_create_user(test_client, db, setup_admin_session):
    new_user_data = {
        "email": "createduser@rice.edu",
        "is_manager": False,
        "is_admin": False,
    }
    response = test_client.post("/user", json=new_user_data)
    users = db.query(UserAccount).all()
    data = response.json()
    assert response.status_code == 200
    assert len(users) == 1
    assert data["email"] == "createduser@rice.edu"
    assert data["is_manager"] is False
    assert data["is_admin"] is False
    assert data.get("id") is not None


def test_update_user(test_client, db, setup_admin_session):
    db_user = UserAccount(
        email="currentuser@rice.edu", is_manager=False, is_admin=False
    )
    db.add(db_user)
    db.commit()
    user = db.query(UserAccount).first()
    user_id = user.id
    updated_user_data = {
        "id": user_id,
        "email": "updateduser@rice.edu",
        "is_manager": False,
        "is_admin": False,
    }
    response = test_client.put(f"user/{user_id}", json=updated_user_data)
    data = response.json()
    assert response.status_code == 200
    assert data["email"] == "updateduser@rice.edu"
    assert data["is_manager"] is False
    assert data["is_admin"] is False
    assert data.get("id") is not None


def test_delete_user(test_client, db, setup_admin_session):
    db_user = UserAccount(
        email="currentuser@rice.edu", is_manager=False, is_admin=False
    )
    db.add(db_user)
    db.commit()
    user = db.query(UserAccount).first()
    user_id = user.id
    response = test_client.delete(f"user/{user_id}")
    empty_db = db.query(UserAccount).all()
    assert response.status_code == 200
    assert len(empty_db) == 0
