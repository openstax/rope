import pytest

from rope.db.schema import MoodleSetting


@pytest.fixture(autouse=True)
def clear_database_table(db):
    db.query(MoodleSetting).delete()
    db.commit()


def test_non_manager_access_manager_endpoint(
    test_client,
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
    course_build_settings = {
        "instructor_firstname": "Franklin",
        "instructor_lastname": "Saint",
        "instructor_email": "fsaint@rice.edu",
        "school_district_name": "snowfall_isd",
    }
    response = test_client.post("/moodle/course/build", json=course_build_settings)

    assert response.status_code == 403


def test_missing_session_id(test_client, setup_override_empty_get_request_session):
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
            "school_district_name": "school_isd",
        }
        test_client.post("/moodle/course/build", json=course_build_settings)

    assert exc_info.type is Exception
