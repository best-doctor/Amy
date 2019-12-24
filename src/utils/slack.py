from typing import Any

import requests

from config import DEBUG, DEBUG_SLACK_CHANNEL_ID, REQUESTS_TIMEOUT, SLACK_HOOK_URL


def send_slack_message(message: str, channel_id: str = None, **kwargs: Any) -> None:
    payload = {
        'text': message,
        'channel': DEBUG_SLACK_CHANNEL_ID if DEBUG else channel_id,
        **kwargs,
    }
    requests.post(SLACK_HOOK_URL, json=payload, timeout=REQUESTS_TIMEOUT)
