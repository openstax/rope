from fastapi.testclient import TestClient
from sqlalchemy.exc import NoResultFound
import pytest
from rope.api.main import app
from rope.api.sessions import get_request_session
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


def override_empty_get_request_session():
    session_id = {}
    return session_id


def override_admin_get_request_session():
    session_id = {"session_id": "A1B2C3"}
    return session_id


def test_non_admin_access_admin_endpoint(test_client, mocker):
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
    non_admin_user = {
        "email": "createduser@rice.edu",
        "is_manager": False,
        "is_admin": False,
    }
    get_all_users_response = test_client.get("/user")
    create_user_response = test_client.post("/user", json=non_admin_user)
    update_user_response = test_client.put("/user/12", json=non_admin_user)
    delete_user_response = test_client.delete("/user/12")
    assert get_all_users_response.status_code == 403
    assert create_user_response.status_code == 403
    assert update_user_response.status_code == 403
    assert delete_user_response.status_code == 403


def test_missing_session_id(test_client):
    app.dependency_overrides[get_request_session] = override_empty_get_request_session
    response = test_client.get("/user/current")
    assert response.status_code == 401


def test_incorrect_user_domain(test_client, mocker):
    google_oauth_mock = mocker.Mock()
    google_oauth_mock.verify_oauth2_token.return_value = {
        "hd": "school.edu",
        "email": "test123@school.edu",
    }
    mocker.patch(
        "rope.api.auth.id_token.verify_oauth2_token",
        google_oauth_mock.verify_oauth2_token,
    )
    response = test_client.post("/session", json={"token": "fp2m3fpwim433tef"})
    assert response.status_code == 401


def test_verify_google_token_valueerror(test_client):
    response = test_client.post("/session", json={"token": "asd32fp2m3fpwim433tef"})
    assert response.status_code == 401


def test_get_user_by_email_no_results(test_client, db, mocker):
    google_oauth_mock = mocker.Mock()
    google_oauth_mock.verify_oauth2_token.return_value = {
        "hd": "rice.edu",
        "email": "test@rice.edu",
    }
    mocker.patch(
        "rope.api.auth.id_token.verify_oauth2_token",
        google_oauth_mock.verify_oauth2_token,
    )
    db_user = UserAccount(
        email="differentuser@rice.edu", is_manager=False, is_admin=False
    )
    db.add(db_user)
    db.commit()
    response = test_client.post("/session", json={"token": "12345fp2m3fpwimef"})
    assert response.status_code == 401


def test_update_db_user_no_results(test_client, db, setup_admin_session):
    with pytest.raises(NoResultFound) as exc_info:
        db_user = UserAccount(
            email="currentuser@rice.edu", is_manager=False, is_admin=False
        )
        db.add(db_user)
        db.commit()
        user = db.query(UserAccount).first()
        user_id = user.id
        updated_user_data = {
            "id": 1235235352,
            "email": "updateduser@rice.edu",
            "is_manager": False,
            "is_admin": False,
        }
        test_client.put(f"user/{user_id}", json=updated_user_data)

    assert exc_info.type is NoResultFound


def test_delete_db_user_no_results(test_client, setup_admin_session):
    response = test_client.delete(f"user/{12352353525324}")
    assert response.status_code == 404