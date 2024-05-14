import argparse
import io
import time
import boto3
import json
import logging
import csv
from functools import cache
from sqlalchemy.exc import NoResultFound

from moodlecli.utils import create_course
from rope.api.routers.moodle import moodle_client
from rope.api import database
from rope.db.schema import CourseBuild, CourseBuildStatus
from rope.api import settings

SQS_WAIT_TIME_SECS = 20
SQS_MAX_MESSAGES = 1

session_factory = database.SessionLocal


logging.basicConfig(level=logging.INFO)


class ProcessorException(Exception):
    pass


# This function allows the code to be testable and
# talk to the mocked sessionmaker in test_course_build_processor.py
def get_db():
    return session_factory  # pragma: no cover


@cache
def get_moodle_user_role_by_shortname(shortname: str):
    moodle_user_role = moodle_client.get_role_by_shortname(shortname)
    moodle_user_id = moodle_user_role["id"]
    return moodle_user_id


def process_course_build(course_build_id, s3_client):
    get_sessionmaker = get_db()
    with get_sessionmaker() as session:
        try:
            course_build = (
                session.query(CourseBuild)
                .filter(CourseBuild.id == course_build_id)
                .one()
            )
        except NoResultFound:
            raise ProcessorException(
                f"""A course build with the id: {course_build_id} does not exist in the course_build table"""  # noqa: E501
            )
        course_build_status = course_build.status.value
        if course_build_status == CourseBuildStatus.CREATED.value:
            course_build.status = CourseBuildStatus.PROCESSING.value
            session.commit()
        elif course_build_status == CourseBuildStatus.PROCESSING.value:
            raise ProcessorException(
                f"""Course build id: {course_build_id} status is processing"""  # noqa: E501
            )
        elif (
            course_build_status == CourseBuildStatus.FAILED.value
            or course_build_status == CourseBuildStatus.COMPLETED.value
        ):
            logging.info(
                f"""The SQS message for course build id: {course_build_id} \
                has been deleted because the build has a {course_build_status} status"""
            )
            return
        try:
            instructor_role_id = get_moodle_user_role_by_shortname("teacher")
            student_role_id = get_moodle_user_role_by_shortname("student")
            instructor_user = moodle_client.get_user_by_email(
                course_build.instructor_email
            )
            instructor_user_id = instructor_user["id"]
            new_course = create_course(
                moodle_client,
                course_build.base_course_id,
                course_build.course_name,
                course_build.course_shortname,
                course_build.course_category_id,
                instructor_role_id,
                instructor_user_id,
                student_role_id,
            )

            course_build.status = CourseBuildStatus.COMPLETED.value
            course_build.course_id = new_course["course_id"]
            course_build.course_enrollment_url = new_course["course_enrolment_url"]
            course_build.course_enrollment_key = new_course["course_enrolment_key"]
            session.commit()

            s3_bucket = settings.COURSES_CSV_S3_BUCKET
            s3_key = settings.COURSES_CSV_S3_KEY
            response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
            csv_data = response["Body"].read().decode("utf-8")

            csv_rows = list(csv.DictReader(io.StringIO(csv_data)))
            csv_rows.append({
                "course_id": course_build.course_id,
                "district": course_build.school_district.name,
                "research_participation": 0
            })

            updated_csv_data = io.StringIO()
            csv_writer = csv.DictWriter(
                updated_csv_data,
                fieldnames=csv_rows[0].keys()
            )
            csv_writer.writeheader()
            csv_writer.writerows(csv_rows)
            s3_client.put_object(Bucket=s3_bucket, Key=s3_key,
                                 Body=updated_csv_data.getvalue().encode("utf-8"))

        except Exception as e:
            course_build.status = CourseBuildStatus.FAILED.value
            session.commit()
            logging.error(f"Failed to build course: {e}")
            raise ProcessorException


def get_sqs_message_processor(s3_client):
    def inner(sqs_message):
        message = json.loads(sqs_message["Body"])
        build_start_time = time.perf_counter()
        process_course_build(message["course_build_id"], s3_client)
        build_completion_time = time.perf_counter()
        logging.info(
            f"The course build took: \
                      {(build_completion_time - build_start_time)} seconds"
        )

    return inner


def get_sqs_messages(sqs_client, queue_url):
    res = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=SQS_MAX_MESSAGES,
        WaitTimeSeconds=SQS_WAIT_TIME_SECS,
    )
    return res.get("Messages", [])


def processor_runner(
    sqs_client, sqs_queue_name, processor, poll_interval_mins, daemonize
):
    queue_url_data = sqs_client.get_queue_url(QueueName=sqs_queue_name)
    queue_url = queue_url_data["QueueUrl"]

    while True:
        sqs_messages = get_sqs_messages(sqs_client, queue_url)
        for message in sqs_messages:
            receipt_handle = message["ReceiptHandle"]

            try:
                processor(message)

                sqs_client.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handle,
                )
            except ProcessorException as e:
                logging.error(f"Failed processing SQS message: {e}")

        if not daemonize:
            break

        if len(sqs_messages) == 0:  # pragma: no cover
            time.sleep(poll_interval_mins * 60)
        else:  # pragma: no cover
            logging.info(f"Received {len(sqs_messages)} messages")


def main():
    logging.info("Starting processor...")
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--daemonize", action="store_true", help="Daemonize processor")
    args = parser.parse_args()
    daemonize = args.daemonize

    sqs_client = boto3.client("sqs")
    s3_client = boto3.client("s3")

    processor = get_sqs_message_processor(s3_client)

    processor_runner(
        sqs_client=sqs_client,
        sqs_queue_name=settings.SQS_QUEUE,
        processor=processor,
        poll_interval_mins=int(settings.SQS_POLL_INTERVAL_MINS),
        daemonize=daemonize,
    )


if __name__ == "__main__":
    main()  # pragma: no cover
