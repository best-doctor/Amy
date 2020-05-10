import datetime

from config import PROJECTS_INFO
from pipelines import AmyPipeline
from utils.format import get_prev_workday_limits_str


def fetch_and_send_yesterday_stat() -> None:
    yesterday_str, today_str = get_prev_workday_limits_str(datetime.date.today())

    for project_id, _, slack_chat_id, project_path in PROJECTS_INFO:
        AmyPipeline().run(
            project_id=project_id,
            project_path=project_path,
            date_from=yesterday_str,
            date_to=today_str,
            slack_chat_id=slack_chat_id,
        )


if __name__ == '__main__':
    fetch_and_send_yesterday_stat()
