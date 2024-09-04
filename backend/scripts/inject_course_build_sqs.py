import json
import argparse
from rope.api import settings, utils


def inject_course_build(sqs_client, sqs_queue_name, course_build_id):
    queue_url = utils.get_sqs_queue_url(sqs_client, sqs_queue_name)
    message_body = {
        "course_build_id": course_build_id
    }
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body)
    )


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("course_build_id", type=str, help="Course build id")
    args = parser.parse_args()
    course_build_id = args.course_build_id

    sqs_client = utils.get_sqs_client()
    sqs_queue_name = settings.SQS_QUEUE
    inject_course_build(sqs_client, sqs_queue_name, course_build_id)


if __name__ == "__main__":
    main()  # pragma: no cover
