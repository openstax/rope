import boto3
import pytest
import botocore.stub
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import io
import csv
from rope.api.processors import course_build_processor
from rope.db.schema import CourseBuild, SchoolDistrict, UserAccount


@pytest.fixture(autouse=True)
def clear_course_build_table(db):
    db.query(CourseBuild).delete()
    db.query(UserAccount).delete()
    db.query(SchoolDistrict).delete()
    db.commit()


@pytest.fixture
def setup_school_district(db):
    school_district = SchoolDistrict(name="blacktemple_isd", active=True)
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
def create_course_builds(
    db,
    setup_nonadmin_authenticated_user_session,
    setup_school_district,
    setup_new_user_manager,
):
    school_district_id = setup_school_district.id
    user_id = setup_new_user_manager.id
    course_build = CourseBuild(
        instructor_firstname="Illidan",
        instructor_lastname="Stormrage",
        instructor_email="istormrage@blacktemple.edu",
        course_name="Algebra 1 - Illidan Stormrage (AY 2024)",
        course_shortname="Alg1 IS AY24",
        course_category_id=6,
        course_id=None,
        course_enrollment_url=None,
        course_enrollment_key=None,
        school_district_id=school_district_id,
        academic_year="AY 2024",
        academic_year_short="AY24",
        base_course_id=70,
        status="created",
        creator_id=user_id,
    )
    course_build2 = CourseBuild(
        instructor_firstname="Thomas",
        instructor_lastname="Stormrage",
        instructor_email="tstormrage@blacktemple.edu",
        course_name="Algebra 1 - Thomas Stormrage (AY 2024)",
        course_shortname="Alg1 TS AY24",
        course_category_id=6,
        course_id=None,
        course_enrollment_url=None,
        course_enrollment_key=None,
        school_district_id=school_district_id,
        academic_year="AY 2024",
        academic_year_short="AY24",
        base_course_id=70,
        status="processing",
        creator_id=user_id,
    )
    course_build3 = CourseBuild(
        instructor_firstname="Michael",
        instructor_lastname="Stormrage",
        instructor_email="mstormrage@blacktemple.edu",
        course_name="Algebra 1 - Michael Stormrage (AY 2024)",
        course_shortname="Alg1 MS AY24",
        course_category_id=6,
        course_id=None,
        course_enrollment_url=None,
        course_enrollment_key=None,
        school_district_id=school_district_id,
        academic_year="AY 2024",
        academic_year_short="AY24",
        base_course_id=70,
        status="completed",
        creator_id=user_id,
    )
    db.add(course_build)
    db.add(course_build2)
    db.add(course_build3)
    db.commit()


def test_course_build_processor(mocker, db, create_course_builds):
    sqs_client = boto3.client("sqs", region_name="azeroth")
    sqs_stubber = botocore.stub.Stubber(sqs_client)
    s3_client = boto3.client("s3")
    s3_stubber = botocore.stub.Stubber(s3_client)

    course_builds = db.query(CourseBuild).all()

    initial_course_build = course_builds[0]

    mock_sqs_data = {"course_build_id": initial_course_build.id}

    mock_settings = mocker.Mock()
    setattr(mock_settings, "SQS_QUEUE", "testqueue")
    setattr(mock_settings, "SQS_POLL_INTERVAL_MINS", "1")
    setattr(mock_settings, "COURSES_CSV_S3_BUCKET", "test-bucket")
    setattr(mock_settings, "COURSES_CSV_S3_KEY", "test-key")

    mocker.patch(
        "rope.api.processors.course_build_processor.settings",
        mock_settings,
    )

    engine = create_engine("postgresql://pguser:pgpassword@localhost/ropedb")
    mock_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    mocker.patch(
        "rope.api.processors.course_build_processor.get_db",
        lambda: mock_factory,
    )

    mocker.patch(
        "rope.api.routers.moodle.moodle_client.get_role_by_shortname",
    )
    mocker.patch(
        "rope.api.routers.moodle.moodle_client.get_user_by_email",
        return_value={
            "id": 1,
        },
    )
    mocker.patch(
        "rope.api.processors.course_build_processor.create_course",
        return_value={
            "course_id": 77,
            "course_enrolment_url": "https://enrolmenturl.com",
            "course_enrolment_key": "amazing_enrolmentkey77",
        },
    )

    sqs_stubber.add_response(
        "get_queue_url",
        {"QueueUrl": "https://testqueue"},
        expected_params={"QueueName": "testqueue"},
    )
    sqs_stubber.add_response(
        "receive_message",
        {
            "Messages": [
                {
                    "ReceiptHandle": "message1",
                    "Body": json.dumps(mock_sqs_data),
                }
            ]
        },
        expected_params={
            "QueueUrl": "https://testqueue",
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 20,
        },
    )
    sqs_stubber.add_response(
        "delete_message",
        {},
        expected_params={
            "QueueUrl": "https://testqueue",
            "ReceiptHandle": "message1",
        },
    )

    csv_data = [
        ["course_id", "district", "research_participation"],
        [21, "blacktemple_isd", 0],
    ]
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerows(csv_data)
    input_csv_data = csv_buffer.getvalue()

    output_csv_data = [
        ["course_id", "district", "research_participation"],
        [21, "blacktemple_isd", 0],
        [77, "blacktemple_isd", 0],

    ]
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerows(output_csv_data)
    output_csv_data = csv_buffer.getvalue()
    s3_stubber.add_response(
        "get_object",
        {
            "Body": io.BytesIO(input_csv_data.encode("utf-8")),
        },
        expected_params={
            "Bucket": "test-bucket",
            "Key": "test-key",
        },
    )

    s3_stubber.add_response(
        "put_object",
        {},
        expected_params={
            "Bucket": "test-bucket",
            "Key": "test-key",
            "Body": output_csv_data.encode("utf-8"),
        },
    )

    s3_stubber.activate()
    sqs_stubber.activate()
    mocker_map = {"sqs": sqs_client, "s3": s3_client}
    mocker.patch("boto3.client", lambda client: mocker_map[client])
    mocker.patch("sys.argv", [""])
    course_build_processor.main()

    db.refresh(initial_course_build)

    assert initial_course_build.status == "completed"
    assert initial_course_build.course_id == 77
    assert initial_course_build.course_enrollment_key == "amazing_enrolmentkey77"
    assert (
        initial_course_build.course_enrollment_url == "https://enrolmenturl.com"
    )
    sqs_stubber.assert_no_pending_responses()
    s3_stubber.assert_no_pending_responses()


def test_non_existing_course_build(mocker):
    sqs_client = boto3.client("sqs", region_name="azeroth")
    sqs_stubber = botocore.stub.Stubber(sqs_client)

    mock_sqs_data = {"course_build_id": 0}

    mock_settings = mocker.Mock()
    setattr(mock_settings, "SQS_QUEUE", "testqueue")
    setattr(mock_settings, "SQS_POLL_INTERVAL_MINS", "1")
    mocker.patch(
        "rope.api.processors.course_build_processor.settings",
        mock_settings,
    )

    engine = create_engine("postgresql://pguser:pgpassword@localhost/ropedb")
    mock_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    mocker.patch(
        "rope.api.processors.course_build_processor.get_db",
        lambda: mock_factory,
    )

    sqs_stubber.add_response(
        "get_queue_url",
        {"QueueUrl": "https://testqueue"},
        expected_params={"QueueName": "testqueue"},
    )
    sqs_stubber.add_response(
        "receive_message",
        {
            "Messages": [
                {
                    "ReceiptHandle": "message1",
                    "Body": json.dumps(mock_sqs_data),
                }
            ]
        },
        expected_params={
            "QueueUrl": "https://testqueue",
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 20,
        },
    )

    sqs_stubber.activate()
    mocker_map = {"sqs": sqs_client, "s3": None}
    mocker.patch("boto3.client", lambda client: mocker_map[client])
    mocker.patch("sys.argv", [""])
    course_build_processor.main()

    sqs_stubber.assert_no_pending_responses()


def test_course_build_status_processing(mocker, db, create_course_builds):
    course_builds = db.query(CourseBuild).all()

    course_build = course_builds[1]

    sqs_client = boto3.client("sqs", region_name="azeroth")
    sqs_stubber = botocore.stub.Stubber(sqs_client)
    mock_sqs_data = {"course_build_id": course_build.id}

    mock_settings = mocker.Mock()
    setattr(mock_settings, "SQS_QUEUE", "testqueue")
    setattr(mock_settings, "SQS_POLL_INTERVAL_MINS", "1")
    mocker.patch(
        "rope.api.processors.course_build_processor.settings",
        mock_settings,
    )

    engine = create_engine("postgresql://pguser:pgpassword@localhost/ropedb")
    mock_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    mocker.patch(
        "rope.api.processors.course_build_processor.get_db",
        lambda: mock_factory,
    )

    sqs_stubber.add_response(
        "get_queue_url",
        {"QueueUrl": "https://testqueue"},
        expected_params={"QueueName": "testqueue"},
    )
    sqs_stubber.add_response(
        "receive_message",
        {
            "Messages": [
                {
                    "ReceiptHandle": "message1",
                    "Body": json.dumps(mock_sqs_data),
                }
            ]
        },
        expected_params={
            "QueueUrl": "https://testqueue",
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 20,
        },
    )

    sqs_stubber.activate()
    mocker_map = {"sqs": sqs_client, "s3": None}
    mocker.patch("boto3.client", lambda client: mocker_map[client])
    mocker.patch("sys.argv", [""])
    course_build_processor.main()

    sqs_stubber.assert_no_pending_responses()


def test_course_build_status_completed(mocker, db, create_course_builds):
    course_builds = db.query(CourseBuild).all()

    course_build = course_builds[2]

    sqs_client = boto3.client("sqs", region_name="azeroth")
    sqs_stubber = botocore.stub.Stubber(sqs_client)

    mock_sqs_data = {"course_build_id": course_build.id}

    mock_settings = mocker.Mock()
    setattr(mock_settings, "SQS_QUEUE", "testqueue")
    setattr(mock_settings, "SQS_POLL_INTERVAL_MINS", "1")
    mocker.patch(
        "rope.api.processors.course_build_processor.settings",
        mock_settings,
    )

    engine = create_engine("postgresql://pguser:pgpassword@localhost/ropedb")
    mock_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    mocker.patch(
        "rope.api.processors.course_build_processor.get_db",
        lambda: mock_factory,
    )

    sqs_stubber.add_response(
        "get_queue_url",
        {"QueueUrl": "https://testqueue"},
        expected_params={"QueueName": "testqueue"},
    )
    sqs_stubber.add_response(
        "receive_message",
        {
            "Messages": [
                {
                    "ReceiptHandle": "message1",
                    "Body": json.dumps(mock_sqs_data),
                }
            ]
        },
        expected_params={
            "QueueUrl": "https://testqueue",
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 20,
        },
    )
    sqs_stubber.add_response(
        "delete_message",
        {},
        expected_params={
            "QueueUrl": "https://testqueue",
            "ReceiptHandle": "message1",
        },
    )

    sqs_stubber.activate()
    mocker_map = {"sqs": sqs_client, "s3": None}
    mocker.patch("boto3.client", lambda client: mocker_map[client])
    mocker.patch("sys.argv", [""])
    course_build_processor.main()

    sqs_stubber.assert_no_pending_responses()
