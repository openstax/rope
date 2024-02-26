from fastapi.testclient import TestClient
from sqlalchemy.exc import NoResultFound
import pytest
from rope.api.main import app
from rope.api.sessions import get_request_session
from rope.api.database import SessionLocal
from rope.db.schema import UserAccount, SchoolDistrict, MoodleSetting, CourseBuild


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
    db.query(CourseBuild).delete()
    db.query(UserAccount).delete()
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


def override_manager_get_request_session():
    session_id = {"session_id": "Z9C8V7"}
    return session_id


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
    get_all_users_response = test_client.get("/user")
    create_user_response = test_client.post("/user", json=non_admin_user)
    update_user_response = test_client.put("/user/12", json=non_admin_user)
    delete_user_response = test_client.delete("/user/12")
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
    assert get_all_users_response.status_code == 403
    assert create_user_response.status_code == 403
    assert update_user_response.status_code == 403
    assert delete_user_response.status_code == 403
    assert create_district_response.status_code == 403
    assert update_district_response.status_code == 403
    assert create_moodle_setting_response.status_code == 403
    assert update_moodle_setting_response.status_code == 403


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
    create_course_build_response = test_client.post(
        "/moodle/course/build", json=course_build_settings
    )
    assert create_course_build_response.status_code == 403


def test_missing_session_id(test_client):
    app.dependency_overrides[get_request_session] = override_empty_get_request_session
    response = test_client.get("/user/current")
    assert response.status_code == 401

    response = test_client.get("/moodle/user")
    assert response.status_code == 401

    response = test_client.get("/admin/settings/district")
    assert response.status_code == 401

    response = test_client.delete("/session")
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


def test_get_moodle_settings_no_results(
    test_client, db, setup_nonadmin_authenticated_user_session
):
    with pytest.raises(NoResultFound) as exc_info:
        test_client.get("/admin/settings/moodle")

    assert exc_info.type is NoResultFound


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
