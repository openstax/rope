import boto3
import botocore.stub
import json
from rope.scripts import inject_course_build_sqs


def test_inject_course_build(mocker):
    sqs_client = boto3.client("sqs", region_name="azeroth")
    stubber = botocore.stub.Stubber(sqs_client)

    mock_settings = mocker.Mock()
    setattr(mock_settings, 'SQS_QUEUE', 'testqueue')
    mocker.patch(
        "rope.scripts.inject_course_build_sqs.settings",
        mock_settings
    )
    sqs_client = boto3.client("sqs", region_name="nor-cal")
    stubber = botocore.stub.Stubber(sqs_client)

    expected_params = {
        'QueueUrl': 'https://testqueue',
        'MessageBody': json.dumps({"course_build_id": "42"})
    }

    stubber.add_response('get_queue_url', {'QueueUrl': 'https://testqueue'},
                                          {'QueueName': 'testqueue'})

    stubber.add_response('send_message', {}, expected_params)
    stubber.activate()
    mocker_map = {"sqs": sqs_client}
    mocker.patch("boto3.client", lambda client: mocker_map[client])
    mocker.patch("sys.argv", ["", "42"])
    inject_course_build_sqs.main()

    stubber.assert_no_pending_responses()
