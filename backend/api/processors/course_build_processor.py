import argparse
from datetime import timedelta
import time
import boto3
import json
import logging
from functools import cache

from moodlecli.utils import create_course
from rope.api.routers.moodle import moodle_client
from rope.api import database
from rope.db.schema import CourseBuild, CourseBuildStatus
from rope.api import settings

SQS_WAIT_TIME_SECS = 20
SQS_MAX_MESSAGES = 10

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


def process_course_build(course_build_id):
    get_sessionmaker = get_db()
    with get_sessionmaker() as session:
        course_build = (
            session.query(CourseBuild)
            .filter(CourseBuild.id == course_build_id["course_build_id"])
            .all()
        )
        if not course_build:
            raise Exception(
                f"""A course build with the id: {course_build_id["course_build_id"]} does not exist in the course_build table"""  # noqa: E501
            )
        course_build_status = course_build[0].status.value
        if course_build_status == "created":
            course_build[0].status = CourseBuildStatus.PROCESSING.value
            session.commit()
        elif course_build_status == "processing":
            raise Exception(
                f"""Course build id: {course_build_id["course_build_id"]} status is processing"""  # noqa: E501
            )
        elif course_build_status == "failed" or course_build_status == "completed":
            logging.info(
                f"""Course build id: {course_build_id["course_build_id"]}
                build status is {course_build_status}"""
            )
            return
        base_course_id = course_build[0].base_course_id
        try:
            instructor_role_id = get_moodle_user_role_by_shortname("teacher")
            student_role_id = get_moodle_user_role_by_shortname("student")
            instructor_user = moodle_client.get_user_by_email(
                course_build[0].instructor_email
            )
            instructor_user_id = instructor_user["id"]
            new_course = create_course(
                moodle_client,
                base_course_id,
                course_build[0].course_name,
                course_build[0].course_shortname,
                course_build[0].course_category,
                instructor_role_id,
                instructor_user_id,
                student_role_id,
            )

            course_build[0].status = CourseBuildStatus.COMPLETED.value
            course_build[0].course_id = new_course["course_id"]
            course_build[0].course_enrollment_url = new_course["course_enrolment_url"]
            course_build[0].course_enrollment_key = new_course["course_enrolment_key"]
            session.commit()
        except Exception as e:
            course_build[0].status = CourseBuildStatus.FAILED.value
            session.commit()
            logging.error(f"Failed to build course: {e}")
            raise


def get_sqs_message_processor():
    def inner(sqs_message):
        course_build_id = json.loads(sqs_message["Body"])
        build_start_time = time.perf_counter()
        process_course_build(course_build_id)
        build_completion_time = timedelta(
            seconds=time.perf_counter() - build_start_time
        )
        logging.info("The course build took:", build_completion_time)

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
                raise Exception from e

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

    processor = get_sqs_message_processor()

    processor_runner(
        sqs_client=sqs_client,
        sqs_queue_name=settings.SQS_QUEUE,
        processor=processor,
        poll_interval_mins=int(settings.SQS_POLL_INTERVAL_MINS),
        daemonize=daemonize,
    )


if __name__ == "__main__":
    main()  # pragma: no cover
