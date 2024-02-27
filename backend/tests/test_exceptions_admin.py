from fastapi.testclient import TestClient
from sqlalchemy.exc import NoResultFound
import pytest
from rope.api.main import app
from rope.api.sessions import get_request_session
from rope.api.database import SessionLocal
from rope.db.schema import SchoolDistrict, MoodleSetting


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
    db.query(SchoolDistrict).delete()
    db.query(MoodleSetting).delete()
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


@pytest.fixture
def setup_nonadmin_authenticated_user_session(mocker):
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
    new_school_district_data = {
        "name": "New_ISD",
        "active": True,
    }
    updated_district_data = {
        "id": 12345678,
        "name": "Updatedschool_ISD",
        "active": False,
    }
    new_moodle_setting_data = {
        "name": "Academic_Year",
        "value": "AY 2030",
    }
    updated_moodle_setting_data = {
        "id": 829384923,
        "name": "Updated_Academic_Year",
        "value": "AY 2200",
    }
    create_district_response = test_client.post(
        "/admin/settings/district", json=new_school_district_data
    )
    update_district_response = test_client.put(
        "/admin/settings/district/77", json=updated_district_data
    )
    create_moodle_setting_response = test_client.post(
        "/admin/settings/moodle", json=new_moodle_setting_data
    )
    update_moodle_setting_response = test_client.put(
        "/admin/settings/moodle/77", json=updated_moodle_setting_data
    )

    assert create_district_response.status_code == 403
    assert update_district_response.status_code == 403
    assert create_moodle_setting_response.status_code == 403
    assert update_moodle_setting_response.status_code == 403


def test_missing_session_id(test_client):
    app.dependency_overrides[get_request_session] = override_empty_get_request_session

    response = test_client.get("/admin/settings/district")

    assert response.status_code == 401


def test_update_db_district_no_results(test_client, db, setup_admin_session):
    with pytest.raises(NoResultFound) as exc_info:
        db_district = SchoolDistrict(name="currentschool_isd", active=True)
        db.add(db_district)
        db.commit()
        district = db.query(SchoolDistrict).first()
        district_id = district.id
        updated_district_data = {
            "id": 12345,
            "name": "updatedschool_isd",
            "active": False,
        }
        test_client.put(
            f"/admin/settings/district/{district_id}", json=updated_district_data
        )

    assert exc_info.type is NoResultFound


def test_update_db_moodle_setting_no_results(test_client, db, setup_admin_session):
    with pytest.raises(NoResultFound) as exc_info:
        db_moodle_setting = MoodleSetting(name="academic_year", value="AY 2040")
        db.add(db_moodle_setting)
        db.commit()
        moodle_setting = db.query(MoodleSetting).first()
        moodle_setting_id = moodle_setting.id
        updated_moodle_setting_data = {
            "id": 8765234624624324,
            "name": "updated_academic_year",
            "value": "AY 2500",
        }
        test_client.put(
            f"/admin/settings/moodle/{moodle_setting_id}",
            json=updated_moodle_setting_data,
        )

    assert exc_info.type is NoResultFound