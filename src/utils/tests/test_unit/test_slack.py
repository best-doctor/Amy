from src.utils.slack import send_slack_message

from config import REQUESTS_TIMEOUT, SLACK_HOOK_URL


def test_send_slack_message(request_post_mock):
    message, channel_id = 'Test', 'test'
    expected_payload = {
        'text': message,
        'channel': None,
    }

    send_slack_message(message, channel_id)

    request_post_mock.assert_called_once_with(
        SLACK_HOOK_URL, json=expected_payload, timeout=REQUESTS_TIMEOUT,
    )
