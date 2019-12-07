import collections
import datetime
import json
import operator
import random
import re
from typing import Any, Mapping, Tuple, List, Optional

import requests

from config import (
    GITLAB_API_TOKEN, JIRA_TICKET_URL_PREFIX, DEVELEOPERS_INFO,
    GET_CORE_STAT_SHELL_COMMAND, REPO_TO_CODETYPE_MAPPING,
)
from utils.shell import run_shell_command
from utils.format import bool_display


CommitInfo = Mapping[str, Any]
Comment = Mapping[str, Any]


def get_message_for_commits_grouped_by_tickets(
        commits_list: List[Mapping[str, Any]],
        project_id: int,
        project_path: str,
        with_commits_info: bool = True,
        with_repo_stat: bool = True,
        auditor_retries: int = 5,
) -> Optional[List[str]]:
    commits_info = collections.defaultdict(list)
    messages = ['']
    revert_commits = []

    for commit_info in commits_list:
        ticket_id = get_ticket_id(commit_info)
        if ticket_id is None:
            if is_revert_commit(commit_info):
                revert_commits.append(commit_info)
            continue
        commits_info[ticket_id].append(commit_info)
    if not commits_info:
        return None

    auditors = []
    for ticket_id, ticket_commits in commits_info.items():
        auditor = None
        for _ in range(auditor_retries):
            if auditor is None or auditor in auditors:
                auditor = get_auditor_for_commits(ticket_commits, project_id)
        auditors.append(auditor)
        message = (
            f'<{JIRA_TICKET_URL_PREFIX}{ticket_id}|{ticket_id}> '
            f'(<@{auditor}>, сделай ревью)\n'
        )
        for commit in sorted(ticket_commits, key=operator.itemgetter('created_at'), reverse=True):
            message += make_commit_message(commit, project_path, project_id, with_commits_info)
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
    if with_repo_stat:
        messages.append(get_core_stat_message())

    return messages


def get_core_stat_message():
    repo_stat = json.loads(
        run_shell_command(GET_CORE_STAT_SHELL_COMMAND),
    )
    return (
        '*Статистика*\n'
        f'\tLOC внутри новой структуры пакетов: {repo_stat["structure_coverage"]:.2f}%\n'
        f'\tДоля чистых функций от всех функций: '
        f'{repo_stat["clean_functions_code_coverage"]:.2f}%\n'
        f'\tДоля чистых функций, которая полностью покрыта тестами: '
        f'{repo_stat["clean_functions_test_coverage"]:.2f}%'
    )


def make_commit_message(
        commit: Mapping[str, Any],
        project_path: str,
        project_id: int,
        with_commits_info: bool,
        strip_commit_message: bool = True,
) -> str:
    message = commit['message'].split('\n')[0].strip()
    commit_message = ': '.join(message.split(': ')[1:]) if strip_commit_message else message
    username = commit['author_email'].split('@')[0]
    extra_info = ''
    if with_commits_info:
        has_tests = bool_display(_is_commit_has_tests(commit, project_id))
        extra_info = f', тесты: {has_tests}'
    return (
        f'    <https://gitlab.com{project_path}/commit/{commit["id"]}|{commit_message}> '
        f'(автор: {username}{extra_info})\n'
    )


def _is_commit_has_tests(commit: Mapping[str, Any], project_id: int = None) -> bool:
    test_path_parts = [
        '/tests/',
        '/__tests__/',
    ]
    min_additions_in_test_file_lines = 5
    project_id = project_id or commit['project_id']
    raw_diff_info = requests.get(
        f'https://gitlab.com/api/v4//projects/{project_id}/repository/commits/{commit["id"]}/diff',
        params={'private_token': GITLAB_API_TOKEN},
    ).json()
    additions_per_file: List[Tuple[str, int]] = []
    for diff in raw_diff_info:
        additions = sum(1 for l in diff['diff'].split('\n') if l.startswith('+'))
        additions_per_file.append(
            (diff['new_path'], additions),
        )
    for filepath, additions_amount in additions_per_file:
        for path_part in test_path_parts:
            if path_part in filepath and additions_amount >= min_additions_in_test_file_lines:
                return True
    return False


def get_ticket_id(commit) -> Optional[str]:
    commit_regexp = r'^(Revert .+|Merge .+|((RET|INT|MOD|AUT|ONB|PLAT|MED)-\d{1,4}): .+)'
    commit_message = commit['message'].split('\n')[0].strip()
    match = re.match(commit_regexp, commit_message)
    return match.groups()[1] if match else None


def is_revert_commit(commit: Mapping[str, Any]) -> bool:
    commit_message = commit['message'].split('\n')[0].strip()
    return commit_message.startswith('Revert ')


def get_auditor_for_commits(commits: List[Mapping[str, Any]], project_id: int) -> str:
    authors = [c['author_email'] for c in commits]
    author_with_max_commits = collections.Counter(authors).most_common()[0][0]
    author_group = REPO_TO_CODETYPE_MAPPING[project_id]
    audit_nominants = [
        e for e in dict(DEVELEOPERS_INFO)[author_group]
        if e[0] != author_with_max_commits
    ]
    return random.choice(audit_nominants)[1]


def get_commits_in_last_n_days(project_id: int, n_days: int) -> List[CommitInfo]:
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    until = datetime.datetime.now()
    since = until - datetime.timedelta(days=n_days)

    commits_list = []
    for page_num in range(100):
        page_commits = requests.get(
            f'https://gitlab.com/api/v4//projects/{project_id}/repository/commits',
            params={
                'private_token': GITLAB_API_TOKEN,
                'since': since.strftime(date_format),
                'until': until.strftime(date_format),
                'per_page': 100,
                'page': page_num,
                'with_stats': True,
            },
        ).json()
        if not page_commits:
            break
        commits_list += page_commits
    return commits_list


def get_comments_for(commit_sha: str, project_id: int) -> List[Comment]:
    return requests.get(
        f'https://gitlab.com/api/v4//projects/{project_id}/repository/'
        f'commits/{commit_sha}/discussions',
        params={
            'private_token': GITLAB_API_TOKEN,
            'per_page': 100,
        },
    ).json()
