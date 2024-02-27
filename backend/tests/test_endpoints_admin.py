from fastapi.testclient import TestClient

import pytest

from rope.api.main import app
from rope.api.database import SessionLocal
from rope.api.sessions import get_request_session
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


def override_admin_get_request_session():
    session_id = {"session_id": "A1B2C3"}
    return session_id


def test_get_districts_admin(test_client, db, mocker):
    app.dependency_overrides[get_request_session] = override_get_request_session
    user = {
        "12345": {
            "email": "districts@rice.edu",
            "is_manager": False,
            "is_admin": True,
        }
    }
    mocker.patch(
        "rope.api.sessions.session_store",
        user,
    )
    db_district = SchoolDistrict(name="active_isd", active=True)
    db_district2 = SchoolDistrict(name="not_active_isd", active=False)
    db.add(db_district)
    db.add(db_district2)
    db.commit()
    response = test_client.get("/admin/settings/district")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0].get("id") is not None
    assert data[1].get("id") is not None
    assert data[0].get("name") == "active_isd"
    assert data[0].get("active") is True
    assert data[1].get("name") == "not_active_isd"
    assert data[1].get("active") is False


def test_get_districts_authenticated_non_admin(
    test_client, db, setup_nonadmin_authenticated_user_session
):
    db_district = SchoolDistrict(name="active_isd", active=True)
    db_district2 = SchoolDistrict(name="not_active_isd", active=False)
    db.add(db_district)
    db.add(db_district2)
    db.commit()
    response = test_client.get("/admin/settings/district")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0].get("id") is not None
    assert data[0].get("name") == "active_isd"
    assert data[0].get("active") is True


def test_create_district(test_client, db, setup_admin_session):
    new_school_district_data = {
        "name": "New_ISD",
        "active": True,
    }
    response = test_client.post(
        "/admin/settings/district", json=new_school_district_data
    )
    districts = db.query(SchoolDistrict).all()
    data = response.json()

    assert response.status_code == 200
    assert len(districts) == 1
    assert data["name"] == "new_isd"
    assert data["active"] is True
    assert data.get("id") is not None


def test_update_district(test_client, db, setup_admin_session):
    db_district = SchoolDistrict(name="currentschool_isd", active=True)
    db.add(db_district)
    db.commit()
    district = db.query(SchoolDistrict).first()
    district_id = district.id
    updated_district_data = {
        "id": district_id,
        "name": "Updatedschool_ISD",
        "active": False,
    }
    response = test_client.put(
        f"/admin/settings/district/{district_id}", json=updated_district_data
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "updatedschool_isd"
    assert data["active"] is False
    assert data.get("id") is not None


def test_get_moodle_settings(
    test_client, db, setup_nonadmin_authenticated_user_session
):
    moodle_setting = MoodleSetting(name="academic_year", value="AY 2024")
    moodle_setting2 = MoodleSetting(name="academic_year_short", value="AY24")
    db.add(moodle_setting)
    db.add(moodle_setting2)
    db.commit()
    response = test_client.get("/admin/settings/moodle")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0].get("id") is not None
    assert data[1].get("id") is not None
    assert data[0].get("name") == "academic_year"
    assert data[0].get("value") == "AY 2024"
    assert data[1].get("name") == "academic_year_short"
    assert data[1].get("value") == "AY24"


def test_create_moodle_settings(test_client, db, setup_admin_session):
    new_moodle_setting_data = {
        "name": "academic_year",
        "value": "AY 2030",
    }
    response = test_client.post("/admin/settings/moodle", json=new_moodle_setting_data)
    moodle_settings = db.query(MoodleSetting).all()
    data = response.json()

    assert response.status_code == 200
    assert len(moodle_settings) == 1
    assert data["name"] == "academic_year"
    assert data["value"] == "AY 2030"
    assert data.get("id") is not None


def test_update_moodle_settings(test_client, db, setup_admin_session):
    db_moodle_setting = MoodleSetting(name="academic_year", value="AY 2030")
    db.add(db_moodle_setting)
    db.commit()
    moodle_setting = db.query(MoodleSetting).first()
    moodle_setting_id = moodle_setting.id
    updated_moodle_setting_data = {
        "id": moodle_setting_id,
        "name": "Updated_Academic_Year",
        "value": "AY 2100",
    }
    response = test_client.put(
        f"/admin/settings/moodle/{moodle_setting_id}", json=updated_moodle_setting_data
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "updated_academic_year"
    assert data["value"] == "AY 2100"
    assert data.get("id") is not None
