from fastapi.testclient import TestClient
import pytest
from rope.api.main import app
from rope.api.sessions import get_request_session
from rope.api.database import SessionLocal
from rope.db.schema import MoodleSetting


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
    db.query(MoodleSetting).delete()
    db.commit()


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


def override_manager_get_request_session():
    session_id = {"session_id": "Z9C8V7"}
    return session_id


def override_get_request_session():
    session_id = {"session_id": "12345"}
    return session_id


def override_empty_get_request_session():
    session_id = {}
    return session_id


def test_non_manager_access_manager_endpoint(test_client, mocker):
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
    course_build_settings = {
        "instructor_firstname": "Franklin",
        "instructor_lastname": "Saint",
        "instructor_email": "fsaint@rice.edu",
        "school_district": 21,
    }
    response = test_client.post(
        "/moodle/course/build", json=course_build_settings
    )

    assert response.status_code == 403


def test_missing_session_id(test_client):
    app.dependency_overrides[get_request_session] = override_empty_get_request_session

    response = test_client.get("/moodle/user")

    assert response.status_code == 401


def test_create_course_build_missing_moodle_settings(
    test_client, db, setup_manager_session
):
    with pytest.raises(Exception) as exc_info:
        db_moodle_setting = MoodleSetting(name="academic_year", value="AY 2040")
        db.add(db_moodle_setting)
        db.commit()
        course_build_settings = {
            "instructor_firstname": "Franklin",
            "instructor_lastname": "Saint",
            "instructor_email": "fsaint@rice.edu",
            "school_district": "school_isd",
        }
        test_client.post("/moodle/course/build", json=course_build_settings)

    assert exc_info.type is Exception
