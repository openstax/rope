import json
import boto3
from rope.api import database
from rope.api.settings import SQS_QUEUE

sqs_client = boto3.client('sqs')

queue_url_data = sqs_client.get_queue_url(
        QueueName=SQS_QUEUE
    )
queue_url = queue_url_data["QueueUrl"]


def create_course_name(instructor_firstname, instructor_lastname, academic_year):
    course_name = (
        f"Algebra 1 - {instructor_firstname} {instructor_lastname} ({academic_year})"
    )
    return course_name


def create_course_shortname(
    instructor_firstname, instructor_lastname, academic_year_short, nonce=None
):
    course_shortname = (
        f"Alg1 {instructor_firstname[0]}{instructor_lastname[0]} {academic_year_short}"
    )
    if nonce is not None:
        course_shortname = f"Alg1 {instructor_firstname[0]}{instructor_lastname[0]}{nonce} {academic_year_short}"  # noqa: E501
    return course_shortname


def check_course_shortname_uniqueness(db, moodle_client, course_shortname):
    moodle_course_shortname = moodle_client.get_course_by_shortname(course_shortname)
    db_course_shortname = database.get_course_by_shortname(db, course_shortname)
    if len(moodle_course_shortname["courses"]) > 0:
        return False
    if db_course_shortname is not None:
        return False
    return True


def send_message_to_sqs(message_body):
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body)
    )
