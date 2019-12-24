import collections
from typing import DefaultDict, List

import requests
from super_mario import BasePipeline, input_pipe, process_pipe, output_pipe

from config import GITLAB_API_TOKEN, REQUESTS_TIMEOUT
from utils.gitlab import (
    _is_commit_has_tests, get_ticket_id, is_revert_commit,
    get_message_for_commits, make_commit_message,
)
from utils.slack import send_slack_message


class AmyPipeline(BasePipeline):
    pipeline = [
        'fetch_commits',
        'fetch_test_coverage',
        'group_commits_by_ticket',
        'generate_message',
        'send_messages',
    ]

    @input_pipe
    def fetch_commits(project_id, date_from: str, date_to: str):
        commits_list = requests.get(
            f'https://gitlab.com/api/v4/projects/{project_id}/repository/commits',
            params={
                'private_token': GITLAB_API_TOKEN,  # type: ignore
                'since': date_from,
                'until': date_to,
                'per_page': 100,
                'with_stats': True,
            },
            timeout=REQUESTS_TIMEOUT,
        ).json()
        return {'raw_commits': commits_list}

    @input_pipe
    def fetch_test_coverage(raw_commits, project_id):
        commits_test_info = {}
        for commit in raw_commits:
            has_tests = _is_commit_has_tests(commit, project_id)
            commits_test_info[commit['id']] = has_tests
        return {'commits_has_tests_info': commits_test_info}

    @process_pipe
    def group_commits_by_ticket(raw_commits):
        revert_commits = []
        commits_info: DefaultDict[str, list] = collections.defaultdict(list)

        for commit_info in raw_commits:
            ticket_id = get_ticket_id(commit_info)
            if ticket_id is None:
                if is_revert_commit(commit_info):
                    revert_commits.append(commit_info)
                continue
            commits_info[ticket_id].append(commit_info)

        return {
            'commits_grouped_by_ticket': commits_info,
            'revert_commits': revert_commits,
        }

    @process_pipe
    def generate_message(
        project_id,
        project_path,
        commits_grouped_by_ticket,
        commits_has_tests_info,
        revert_commits,
    ):
        messages = ['']
        auditors: List[str] = []
        for ticket_id, ticket_commits in commits_grouped_by_ticket.items():
            message, auditor = get_message_for_commits(
                ticket_commits,
                ticket_id,
                auditors,
                project_path,
                project_id,
                with_commits_info=True,
            )
            if auditor:
                auditors.append(auditor)
            messages.append(message)
        if revert_commits:
            message = 'Ревертнутые коммиты:\n'
            for commit in revert_commits:
                message += make_commit_message(
                    commit,
                    project_path,
                    project_id,
                    with_commits_info=False,
                    strip_commit_message=False,
                )
            messages.append(message)
        return {'messages': messages}

    @output_pipe
    def send_messages(messages, slack_chat_id):
        for message in messages:
            send_slack_message(
                message,
                slack_chat_id,
                username='Пёс, который любит смотреть',
                icon_emoji=':gooddogie:',
            )
