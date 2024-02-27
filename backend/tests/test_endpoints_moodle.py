from fastapi.testclient import TestClient

import pytest

from rope.api.main import app
from rope.api.database import SessionLocal
from rope.api.sessions import get_request_session
from rope.db.schema import CourseBuild, MoodleSetting, SchoolDistrict, UserAccount


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


@pytest.fixture
def create_course_build_setup_district(test_client, setup_admin_session):
    new_school_district_data = {
        "name": "snowfall_isd",
        "active": True,
    }
    response = test_client.post(
        "/admin/settings/district", json=new_school_district_data
    )
    return response.json()


@pytest.fixture
def create_course_build_setup_moodle_settings(test_client, db, setup_admin_session):
    academic_year = {
        "name": "academic_year",
        "value": "AY 2024",
    }
    academic_year_short = {
        "name": "academic_year_short",
        "value": "AY24",
    }
    course_category = {
        "name": "course_category",
        "value": "21",
    }
    base_course_id = {
        "name": "base_course_id",
        "value": "100",
    }
    test_client.post("/admin/settings/moodle", json=academic_year)
    test_client.post("/admin/settings/moodle", json=academic_year_short)
    test_client.post("/admin/settings/moodle", json=course_category)
    test_client.post("/admin/settings/moodle", json=base_course_id)
    moodle_settings = db.query(MoodleSetting).all()
    return moodle_settings


@pytest.fixture
def create_course_build_setup_user(test_client, db, setup_admin_session):
    new_user_data = {
        "email": "manager@rice.edu",
        "is_manager": True,
        "is_admin": False,
    }
    response = test_client.post("/user", json=new_user_data)
    return response.json()


def override_get_request_session():
    session_id = {"session_id": "12345"}
    return session_id


def override_admin_get_request_session():
    session_id = {"session_id": "A1B2C3"}
    return session_id


def override_manager_get_request_session():
    session_id = {"session_id": "Z9C8V7"}
    return session_id


def test_create_course_build(
    test_client,
    db,
    create_course_build_setup_district,
    create_course_build_setup_moodle_settings,
    create_course_build_setup_user,
    setup_manager_session,
    mocker,
):
    mocker.patch(
        "rope.api.routers.moodle.moodle_client.get_course_by_shortname",
        return_value={
            "courses": [],
            "warnings": [],
        },
    )
    school_district_name = create_course_build_setup_district["name"]
    course_build_settings = {
        "instructor_firstname": "Franklin",
        "instructor_lastname": "Saint",
        "instructor_email": "fsaint@rice.edu",
        "school_district": school_district_name,
    }
    response = test_client.post("/moodle/course/build", json=course_build_settings)
    course_build = db.query(CourseBuild).all()
    data = response.json()

    assert len(course_build) == 1

    assert response.status_code == 200
    assert data["instructor_firstname"] == "Franklin"
    assert data["instructor_lastname"] == "Saint"
    assert data["instructor_email"] == "fsaint@rice.edu"
    assert data["course_name"] == "Algebra 1 - Franklin Saint (AY 2024)"
    assert data["course_shortname"] == "Alg1 FS AY24"
    assert data["course_id"] is None
    assert data["course_enrollment_url"] is None
    assert data["course_enrollment_key"] is None
    assert data["school_district"] == "snowfall_isd"
    assert data["academic_year"] == "AY 2024"
    assert data["academic_year_short"] == "AY24"
    assert data["status"] == "created"
    assert data["creator"] == "manager@rice.edu"


def test_create_course_build_duplicate_shortname(
    test_client,
    db,
    create_course_build_setup_district,
    create_course_build_setup_moodle_settings,
    create_course_build_setup_user,
    setup_manager_session,
    mocker,
):
    mocker.patch(
        "rope.api.routers.moodle.moodle_client.get_course_by_shortname",
        return_value={
            "courses": [],
            "warnings": [],
        },
    )
    school_district_name = create_course_build_setup_district["name"]
    course_build_settings1 = {
        "instructor_firstname": "Franklin",
        "instructor_lastname": "Saint",
        "instructor_email": "fsaint@rice.edu",
        "school_district": school_district_name,
    }
    course_build_settings2 = {
        "instructor_firstname": "Freya",
        "instructor_lastname": "Santiago",
        "instructor_email": "fsantiago@rice.edu",
        "school_district": school_district_name,
    }
    first_course_response = test_client.post(
        "/moodle/course/build", json=course_build_settings1
    )
    second_course_response = test_client.post(
        "/moodle/course/build", json=course_build_settings2
    )
    course_build = db.query(CourseBuild).all()
    first_course_data = first_course_response.json()
    secound_course_data = second_course_response.json()

    assert len(course_build) == 2

    assert first_course_response.status_code == 200
    assert first_course_data["instructor_firstname"] == "Franklin"
    assert first_course_data["instructor_lastname"] == "Saint"
    assert first_course_data["instructor_email"] == "fsaint@rice.edu"
    assert first_course_data["course_name"] == "Algebra 1 - Franklin Saint (AY 2024)"
    assert first_course_data["course_shortname"] == "Alg1 FS AY24"
    assert first_course_data["course_id"] is None
    assert first_course_data["course_enrollment_url"] is None
    assert first_course_data["course_enrollment_key"] is None
    assert first_course_data["school_district"] == "snowfall_isd"
    assert first_course_data["academic_year"] == "AY 2024"
    assert first_course_data["academic_year_short"] == "AY24"
    assert first_course_data["status"] == "created"
    assert first_course_data["creator"] == "manager@rice.edu"

    assert second_course_response.status_code == 200
    assert secound_course_data["instructor_firstname"] == "Freya"
    assert secound_course_data["instructor_lastname"] == "Santiago"
    assert secound_course_data["instructor_email"] == "fsantiago@rice.edu"
    assert secound_course_data["course_name"] == "Algebra 1 - Freya Santiago (AY 2024)"
    assert secound_course_data["course_shortname"] == "Alg1 FS1 AY24"
    assert secound_course_data["course_id"] is None
    assert secound_course_data["course_enrollment_url"] is None
    assert secound_course_data["course_enrollment_key"] is None
    assert secound_course_data["school_district"] == "snowfall_isd"
    assert secound_course_data["academic_year"] == "AY 2024"
    assert secound_course_data["academic_year_short"] == "AY24"
    assert secound_course_data["status"] == "created"
    assert secound_course_data["creator"] == "manager@rice.edu"


def test_create_course_build_duplicate_shortname_moodle(
    test_client,
    db,
    create_course_build_setup_district,
    create_course_build_setup_moodle_settings,
    create_course_build_setup_user,
    setup_manager_session,
    mocker,
):
    school_district_name = create_course_build_setup_district["name"]
    course_build_settings = {
        "instructor_firstname": "Reed",
        "instructor_lastname": "Thompson",
        "instructor_email": "rthompson@rice.edu",
        "school_district": school_district_name,
    }
    mocker.patch(
        "rope.api.routers.moodle.moodle_client.get_course_by_shortname",
        side_effect=[
            {"courses": [{}]},
            {"courses": []},
        ],
    )
    response = test_client.post("/moodle/course/build", json=course_build_settings)
    course_build = db.query(CourseBuild).all()
    data = response.json()

    assert len(course_build) == 1

    assert response.status_code == 200
    assert data["instructor_firstname"] == "Reed"
    assert data["instructor_lastname"] == "Thompson"
    assert data["instructor_email"] == "rthompson@rice.edu"
    assert data["course_name"] == "Algebra 1 - Reed Thompson (AY 2024)"
    assert data["course_shortname"] == "Alg1 RT1 AY24"
    assert data["course_id"] is None
    assert data["course_enrollment_url"] is None
    assert data["course_enrollment_key"] is None
    assert data["school_district"] == "snowfall_isd"
    assert data["academic_year"] == "AY 2024"
    assert data["academic_year_short"] == "AY24"
    assert data["status"] == "created"
    assert data["creator"] == "manager@rice.edu"


def test_get_moodle_user(
    test_client, setup_nonadmin_authenticated_user_session, mocker
):
    mocker.patch(
        "rope.api.routers.moodle.moodle_client.get_user_by_email",
        return_value={
            "firstname": "first",
            "lastname": "last",
            "email": "first.last@email.com",
        },
    )

    response = test_client.get("/moodle/user/?email=first.last@email.com")

    assert response.status_code == 200

    data = response.json()

    assert data["first_name"] == "first"
    assert data["last_name"] == "last"
    assert data["email"] == "first.last@email.com"

    mocker.patch(
        "rope.api.routers.moodle.moodle_client.get_user_by_email",
        return_value=None,
    )

    response = test_client.get("/moodle/user/?email=first.last@email.com")

    assert response.status_code == 200

    data = response.json()

    assert not data