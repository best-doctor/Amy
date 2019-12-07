import collections
import datetime

import requests

from config import PROJECTS_INFO, GITLAB_API_TOKEN
from utils.format import get_prev_workday_limits_str
from utils.gitlab import get_message_for_commits_grouped_by_tickets, get_ticket_id
from utils.slack import send_slack_message


def fetch_and_send_yesterday_stat():
    yesterday_str, today_str = get_prev_workday_limits_str(datetime.date.today())

    for project_id, project_name, slack_chat_id, project_path in PROJECTS_INFO:
        commits_list = requests.get(
            f'https://gitlab.com/api/v4//projects/{project_id}/repository/commits',
            params={
                'private_token': GITLAB_API_TOKEN,
                'since': yesterday_str,
                'until': today_str,
                'per_page': 100,
                'with_stats': True,
            },
        ).json()

        show_core_stat = False  # disable for now, need to make it universal and reenable
        messages = get_message_for_commits_grouped_by_tickets(
            commits_list,
            project_id,
            project_path,
            with_repo_stat=show_core_stat,
        )
        if messages is None:
            continue

        commits_info = collections.defaultdict(list)

        for commit_info in commits_list:
            ticket_id = get_ticket_id(commit_info)
            if ticket_id is None:
                continue  # коммит с мерджем или ревертом
            commits_info[ticket_id].append(commit_info)
        if not commits_info:
            continue

        messages = [f'*{project_name} за вчера*'] + messages

        for message in messages:
            send_slack_message(
                message,
                slack_chat_id,
                username='Пёс, который любит смотреть',
                icon_emoji=':gooddogie:',
            )


if __name__ == '__main__':
    fetch_and_send_yesterday_stat()
