import pytest
from sqlalchemy import text
from rope.db.schema import CourseBuild, MoodleSetting, SchoolDistrict, UserAccount
from rope.api.main import app
from rope.api.utils import get_sqs_client
import boto3
import botocore.stub
import json


@pytest.fixture(autouse=True)
def clear_database_table(db):
    db.query(CourseBuild).delete()
    db.query(UserAccount).delete()
    db.query(SchoolDistrict).delete()
    db.query(MoodleSetting).delete()
    db.execute(text("ALTER SEQUENCE course_build_id_seq RESTART WITH 1"))
    db.commit()


@pytest.fixture
def setup_school_district(db):
    school_district = SchoolDistrict(name="snowfall_isd", active=True)
    db.add(school_district)
    db.commit()
    db.refresh(school_district)

    return school_district


@pytest.fixture
def setup_new_user_manager(db):
    user = UserAccount(email="manager@rice.edu", is_manager=True, is_admin=False)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def setup_moodle_settings(db):
    academic_year = MoodleSetting(name="academic_year", value="AY 2024")
    academic_year_short = MoodleSetting(name="academic_year_short", value="AY24")
    course_category = MoodleSetting(name="course_category", value="21")
    base_course_id = MoodleSetting(name="base_course_id", value="100")
    db.add(academic_year)
    db.add(academic_year_short)
    db.add(course_category)
    db.add(base_course_id)
    db.commit()

    moodle_settings = db.query(MoodleSetting).all()
    return moodle_settings


@pytest.fixture
def setup_get_course_builds(
    db,
    setup_nonadmin_authenticated_user_session,
    setup_school_district,
    setup_new_user_manager,
):
    school_district_id = setup_school_district.id
    user_id = setup_new_user_manager.id
    add_db_course_build1 = CourseBuild(
        instructor_firstname="Franklin",
        instructor_lastname="Saint",
        instructor_email="fsaint@rice.edu",
        course_name="Algebra 1 - Franklin Saint (AY 2025)",
        course_shortname="Alg1 FS AY25",
        course_category="21",
        course_id=None,
        course_enrollment_url=None,
        course_enrollment_key=None,
        school_district_id=school_district_id,
        academic_year="AY 2025",
        academic_year_short="AY25",
        base_course_id="2121",
        status="created",
        creator_id=user_id,
    )
    add_db_course_build2 = CourseBuild(
        instructor_firstname="Leon",
        instructor_lastname="Simmons",
        instructor_email="lsimmons@rice.edu",
        course_name="Algebra 1 - Leon Simmons (AY 2025)",
        course_shortname="Alg1 LS AY25",
        course_category="21",
        course_id=None,
        course_enrollment_url=None,
        course_enrollment_key=None,
        school_district_id=school_district_id,
        academic_year="AY 2025",
        academic_year_short="AY25",
        base_course_id="2121",
        status="created",
        creator_id=user_id,
    )
    add_db_course_build3 = CourseBuild(
        instructor_firstname="Franklin",
        instructor_lastname="Saint",
        instructor_email="fsaint@rice.edu",
        course_name="Algebra 1 - Franklin Saint (AY 2030)",
        course_shortname="Alg1 FS AY30",
        course_category="41",
        course_id=None,
        course_enrollment_url=None,
        course_enrollment_key=None,
        school_district_id=school_district_id,
        academic_year="AY 2030",
        academic_year_short="AY30",
        base_course_id="4141",
        status="created",
        creator_id=user_id,
    )
    add_db_course_build4 = CourseBuild(
        instructor_firstname="Reed",
        instructor_lastname="Thompson",
        instructor_email="lthompson@rice.edu",
        course_name="Algebra 1 - Reed Thompson (AY 2025)",
        course_shortname="Alg1 RT AY25",
        course_category="21",
        course_id=47,
        course_enrollment_url="url.com",
        course_enrollment_key="12345",
        school_district_id=school_district_id,
        academic_year="AY 2025",
        academic_year_short="AY25",
        base_course_id="2121",
        status="created",
        creator_id=user_id,
    )
    db.add(add_db_course_build1)
    db.add(add_db_course_build2)
    db.add(add_db_course_build3)
    db.add(add_db_course_build4)
    db.commit()


def test_create_course_build(
    test_client,
    db,
    setup_school_district,
    setup_moodle_settings,
    setup_new_user_manager,
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
    app.dependency_overrides[get_sqs_client] = lambda : mocker.MagicMock()
    school_district_name = setup_school_district.name
    course_build_settings = {
        "instructor_firstname": "Franklin",
        "instructor_lastname": "Saint",
        "instructor_email": "fsaint@rice.edu",
        "school_district_name": school_district_name,
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
    assert data["school_district_name"] == "snowfall_isd"
    assert data["academic_year"] == "AY 2024"
    assert data["academic_year_short"] == "AY24"
    assert data["status"] == "created"
    assert data["creator_email"] == "manager@rice.edu"


def test_create_course_build_sqs_message(
    test_client,
    db,
    setup_school_district,
    setup_moodle_settings,
    setup_new_user_manager,
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
    mock_settings = mocker.Mock()
    setattr(mock_settings, 'SQS_QUEUE', 'testqueue')
    mocker.patch(
        "rope.api.routers.moodle.settings",
        mock_settings
    )
    sqs_client = boto3.client("sqs", region_name="nor-cal")
    stubber = botocore.stub.Stubber(sqs_client)

    expected_params = {
        'QueueUrl': 'https://testqueue',
        'MessageBody': json.dumps({"course_build_id": 1})
    }

    stubber.add_response('get_queue_url', {'QueueUrl': 'https://testqueue'},
                                          {'QueueName': 'testqueue'})

    stubber.add_response('send_message', {}, expected_params)

    app.dependency_overrides[get_sqs_client] = lambda : sqs_client
    stubber.activate()

    school_district_name = setup_school_district.name

    course_build_settings = {
        "instructor_firstname": "Franklin",
        "instructor_lastname": "Saint",
        "instructor_email": "fsaint@rice.edu",
        "school_district_name": school_district_name,
    }

    response = test_client.post("/moodle/course/build", json=course_build_settings)
    course_build = db.query(CourseBuild).all()
    data = response.json()

    stubber.assert_no_pending_responses()
    assert len(course_build) == 1

    assert response.status_code == 200
    assert data["instructor_firstname"] == "Franklin"
    assert data["instructor_lastname"] == "Saint"


def test_create_course_build_duplicate_shortname(
    test_client,
    db,
    setup_school_district,
    setup_moodle_settings,
    setup_new_user_manager,
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
    app.dependency_overrides[get_sqs_client] = lambda : mocker.MagicMock()

    school_district_name = setup_school_district.name
    course_build_settings1 = {
        "instructor_firstname": "Franklin",
        "instructor_lastname": "Saint",
        "instructor_email": "fsaint@rice.edu",
        "school_district_name": school_district_name,
    }
    course_build_settings2 = {
        "instructor_firstname": "Freya",
        "instructor_lastname": "Santiago",
        "instructor_email": "fsantiago@rice.edu",
        "school_district_name": school_district_name,
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
    assert first_course_data["school_district_name"] == "snowfall_isd"
    assert first_course_data["academic_year"] == "AY 2024"
    assert first_course_data["academic_year_short"] == "AY24"
    assert first_course_data["status"] == "created"
    assert first_course_data["creator_email"] == "manager@rice.edu"

    assert second_course_response.status_code == 200
    assert secound_course_data["instructor_firstname"] == "Freya"
    assert secound_course_data["instructor_lastname"] == "Santiago"
    assert secound_course_data["instructor_email"] == "fsantiago@rice.edu"
    assert secound_course_data["course_name"] == "Algebra 1 - Freya Santiago (AY 2024)"
    assert secound_course_data["course_shortname"] == "Alg1 FS1 AY24"
    assert secound_course_data["course_id"] is None
    assert secound_course_data["course_enrollment_url"] is None
    assert secound_course_data["course_enrollment_key"] is None
    assert secound_course_data["school_district_name"] == "snowfall_isd"
    assert secound_course_data["academic_year"] == "AY 2024"
    assert secound_course_data["academic_year_short"] == "AY24"
    assert secound_course_data["status"] == "created"
    assert secound_course_data["creator_email"] == "manager@rice.edu"


def test_create_course_build_duplicate_shortname_moodle(
    test_client,
    db,
    setup_school_district,
    setup_moodle_settings,
    setup_new_user_manager,
    setup_manager_session,
    mocker,
):
    school_district_name = setup_school_district.name
    course_build_settings = {
        "instructor_firstname": "Reed",
        "instructor_lastname": "Thompson",
        "instructor_email": "rthompson@rice.edu",
        "school_district_name": school_district_name,
    }
    mocker.patch(
        "rope.api.routers.moodle.moodle_client.get_course_by_shortname",
        side_effect=[
            {"courses": [{}]},
            {"courses": []},
        ],
    )
    app.dependency_overrides[get_sqs_client] = lambda : mocker.MagicMock()

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
    assert data["school_district_name"] == "snowfall_isd"
    assert data["academic_year"] == "AY 2024"
    assert data["academic_year_short"] == "AY24"
    assert data["status"] == "created"
    assert data["creator_email"] == "manager@rice.edu"


def test_get_course_build_by_academic_year_and_instructor_email(
    test_client,
    setup_nonadmin_authenticated_user_session,
    setup_school_district,
    setup_new_user_manager,
    setup_get_course_builds,
):
    school_district_name = setup_school_district.name
    response = test_client.get(
        "/moodle/course/build?academic_year=AY 2025&instructor_email=fsaint@rice.edu"
    )
    data = response.json()

    assert len(data) == 1

    assert response.status_code == 200
    assert data[0].get("instructor_firstname") == "Franklin"
    assert data[0].get("instructor_lastname") == "Saint"
    assert data[0].get("instructor_email") == "fsaint@rice.edu"
    assert data[0].get("course_name") == "Algebra 1 - Franklin Saint (AY 2025)"
    assert data[0].get("course_shortname") == "Alg1 FS AY25"
    assert data[0].get("course_id") is None
    assert data[0].get("course_enrollment_url") is None
    assert data[0].get("course_enrollment_key") is None
    assert data[0].get("school_district_name") == school_district_name
    assert data[0].get("academic_year") == "AY 2025"
    assert data[0].get("academic_year_short") == "AY25"
    assert data[0].get("status") == "created"
    assert data[0].get("creator_email") == "manager@rice.edu"


def test_get_course_build_by_academic_year(
    test_client,
    setup_nonadmin_authenticated_user_session,
    setup_school_district,
    setup_new_user_manager,
    setup_get_course_builds,
):
    school_district_name = setup_school_district.name
    response = test_client.get("/moodle/course/build?academic_year=AY 2025")
    data = response.json()

    assert len(data) == 3

    assert response.status_code == 200
    assert data[0].get("instructor_firstname") == "Franklin"
    assert data[0].get("instructor_lastname") == "Saint"
    assert data[0].get("instructor_email") == "fsaint@rice.edu"
    assert data[0].get("course_name") == "Algebra 1 - Franklin Saint (AY 2025)"
    assert data[0].get("course_shortname") == "Alg1 FS AY25"
    assert data[0].get("course_id") is None
    assert data[0].get("course_enrollment_url") is None
    assert data[0].get("course_enrollment_key") is None
    assert data[0].get("school_district_name") == school_district_name
    assert data[0].get("academic_year") == "AY 2025"
    assert data[0].get("academic_year_short") == "AY25"
    assert data[0].get("status") == "created"
    assert data[0].get("creator_email") == "manager@rice.edu"

    assert data[1].get("instructor_firstname") == "Leon"
    assert data[1].get("instructor_lastname") == "Simmons"
    assert data[1].get("instructor_email") == "lsimmons@rice.edu"
    assert data[1].get("course_name") == "Algebra 1 - Leon Simmons (AY 2025)"
    assert data[1].get("course_shortname") == "Alg1 LS AY25"
    assert data[1].get("course_id") is None
    assert data[1].get("course_enrollment_url") is None
    assert data[1].get("course_enrollment_key") is None
    assert data[1].get("school_district_name") == school_district_name
    assert data[1].get("academic_year") == "AY 2025"
    assert data[1].get("academic_year_short") == "AY25"
    assert data[1].get("status") == "created"
    assert data[1].get("creator_email") == "manager@rice.edu"

    assert data[2].get("instructor_firstname") == "Reed"
    assert data[2].get("instructor_lastname") == "Thompson"
    assert data[2].get("instructor_email") == "lthompson@rice.edu"
    assert data[2].get("course_name") == "Algebra 1 - Reed Thompson (AY 2025)"
    assert data[2].get("course_shortname") == "Alg1 RT AY25"
    assert data[2].get("course_id") == 47
    assert data[2].get("course_enrollment_url") == "url.com"
    assert data[2].get("course_enrollment_key") == "12345"
    assert data[2].get("school_district_name") == school_district_name
    assert data[2].get("academic_year") == "AY 2025"
    assert data[2].get("academic_year_short") == "AY25"
    assert data[2].get("status") == "created"
    assert data[2].get("creator_email") == "manager@rice.edu"


def test_get_course_build_by_instructor_email(
    test_client,
    setup_nonadmin_authenticated_user_session,
    setup_school_district,
    setup_new_user_manager,
    setup_get_course_builds,
):
    school_district_name = setup_school_district.name
    response = test_client.get("/moodle/course/build?instructor_email=fsaint@rice.edu")
    data = response.json()

    assert len(data) == 2

    assert response.status_code == 200
    assert data[0].get("instructor_firstname") == "Franklin"
    assert data[0].get("instructor_lastname") == "Saint"
    assert data[0].get("instructor_email") == "fsaint@rice.edu"
    assert data[0].get("course_name") == "Algebra 1 - Franklin Saint (AY 2025)"
    assert data[0].get("course_shortname") == "Alg1 FS AY25"
    assert data[0].get("course_id") is None
    assert data[0].get("course_enrollment_url") is None
    assert data[0].get("course_enrollment_key") is None
    assert data[0].get("school_district_name") == school_district_name
    assert data[0].get("academic_year") == "AY 2025"
    assert data[0].get("academic_year_short") == "AY25"
    assert data[0].get("status") == "created"
    assert data[0].get("creator_email") == "manager@rice.edu"

    assert data[1].get("instructor_firstname") == "Franklin"
    assert data[1].get("instructor_lastname") == "Saint"
    assert data[1].get("instructor_email") == "fsaint@rice.edu"
    assert data[1].get("course_name") == "Algebra 1 - Franklin Saint (AY 2030)"
    assert data[1].get("course_shortname") == "Alg1 FS AY30"
    assert data[1].get("course_id") is None
    assert data[1].get("course_enrollment_url") is None
    assert data[1].get("course_enrollment_key") is None
    assert data[1].get("school_district_name") == school_district_name
    assert data[1].get("academic_year") == "AY 2030"
    assert data[1].get("academic_year_short") == "AY30"
    assert data[1].get("status") == "created"
    assert data[1].get("creator_email") == "manager@rice.edu"


def test_get_all_course_builds(
    test_client,
    setup_nonadmin_authenticated_user_session,
    setup_school_district,
    setup_new_user_manager,
    setup_get_course_builds,
):
    school_district_name = setup_school_district.name
    response = test_client.get("/moodle/course/build")
    data = response.json()

    assert len(data) == 4

    assert response.status_code == 200
    assert data[0].get("instructor_firstname") == "Franklin"
    assert data[0].get("instructor_lastname") == "Saint"
    assert data[0].get("instructor_email") == "fsaint@rice.edu"
    assert data[0].get("course_name") == "Algebra 1 - Franklin Saint (AY 2025)"
    assert data[0].get("course_shortname") == "Alg1 FS AY25"
    assert data[0].get("course_id") is None
    assert data[0].get("course_enrollment_url") is None
    assert data[0].get("course_enrollment_key") is None
    assert data[0].get("school_district_name") == school_district_name
    assert data[0].get("academic_year") == "AY 2025"
    assert data[0].get("academic_year_short") == "AY25"
    assert data[0].get("status") == "created"
    assert data[0].get("creator_email") == "manager@rice.edu"

    assert data[1].get("instructor_firstname") == "Leon"
    assert data[1].get("instructor_lastname") == "Simmons"
    assert data[1].get("instructor_email") == "lsimmons@rice.edu"
    assert data[1].get("course_name") == "Algebra 1 - Leon Simmons (AY 2025)"
    assert data[1].get("course_shortname") == "Alg1 LS AY25"
    assert data[1].get("course_id") is None
    assert data[1].get("course_enrollment_url") is None
    assert data[1].get("course_enrollment_key") is None
    assert data[1].get("school_district_name") == school_district_name
    assert data[1].get("academic_year") == "AY 2025"
    assert data[1].get("academic_year_short") == "AY25"
    assert data[1].get("status") == "created"
    assert data[1].get("creator_email") == "manager@rice.edu"

    assert data[2].get("instructor_firstname") == "Franklin"
    assert data[2].get("instructor_lastname") == "Saint"
    assert data[2].get("instructor_email") == "fsaint@rice.edu"
    assert data[2].get("course_name") == "Algebra 1 - Franklin Saint (AY 2030)"
    assert data[2].get("course_shortname") == "Alg1 FS AY30"
    assert data[2].get("course_id") is None
    assert data[2].get("course_enrollment_url") is None
    assert data[2].get("course_enrollment_key") is None
    assert data[2].get("school_district_name") == school_district_name
    assert data[2].get("academic_year") == "AY 2030"
    assert data[2].get("academic_year_short") == "AY30"
    assert data[2].get("status") == "created"
    assert data[2].get("creator_email") == "manager@rice.edu"

    assert data[3].get("instructor_firstname") == "Reed"
    assert data[3].get("instructor_lastname") == "Thompson"
    assert data[3].get("instructor_email") == "lthompson@rice.edu"
    assert data[3].get("course_name") == "Algebra 1 - Reed Thompson (AY 2025)"
    assert data[3].get("course_shortname") == "Alg1 RT AY25"
    assert data[3].get("course_id") == 47
    assert data[3].get("course_enrollment_url") == "url.com"
    assert data[3].get("course_enrollment_key") == "12345"
    assert data[3].get("school_district_name") == school_district_name
    assert data[3].get("academic_year") == "AY 2025"
    assert data[3].get("academic_year_short") == "AY25"
    assert data[3].get("status") == "created"
    assert data[3].get("creator_email") == "manager@rice.edu"


def test_get_moodle_user(
    test_client,
    setup_nonadmin_authenticated_user_session,
    mocker,
):
    mocker.patch(
        "rope.api.routers.moodle.moodle_client.get_user_by_email",
        return_value={
            "firstname": "first",
            "lastname": "last",
            "email": "first.last@email.com",
        },
    )

    response = test_client.get("/moodle/user?email=first.last@email.com")

    assert response.status_code == 200

    data = response.json()

    assert data["first_name"] == "first"
    assert data["last_name"] == "last"
    assert data["email"] == "first.last@email.com"

    mocker.patch(
        "rope.api.routers.moodle.moodle_client.get_user_by_email",
        return_value=None,
    )

    response = test_client.get("/moodle/user?email=first.last@email.com")

    assert response.status_code == 200

    data = response.json()

    assert not data
