import collections
import datetime
import json
import operator
import random
import re
from typing import Any, Mapping, Tuple, List, Optional, DefaultDict

import requests

from config import (
    GITLAB_API_TOKEN, JIRA_TICKET_URL_PREFIX, DEVELEOPERS_INFO,
    GET_CORE_STAT_SHELL_COMMAND, REPO_TO_CODETYPE_MAPPING,
    COMMIT_REGEXP)
from utils.shell import run_shell_command
from utils.format import bool_display


CommitInfo = Mapping[str, Any]
CommitDiffInfo = Mapping[str, Any]
Comment = Mapping[str, Any]
GroupedCommits = Mapping[str, List[CommitInfo]]


def group_commits_by_ticket(commits_list) -> Tuple[GroupedCommits, List[CommitInfo]]:
    revert_commits = []
    commits_info: DefaultDict[str, list] = collections.defaultdict(list)

    for commit_info in commits_list:
        ticket_id = get_ticket_id(commit_info)
        if ticket_id is None:
            if is_revert_commit(commit_info):
                revert_commits.append(commit_info)
            continue
        commits_info[ticket_id].append(commit_info)
    return commits_info, revert_commits


def get_message_for_commits(
    ticket_commits: List[CommitInfo],
    ticket_id: str,
    auditors: List[str],
    project_path: str,
    project_id: int,
    with_commits_info: bool,
) -> Tuple[str, Optional[str]]:
    auditor_retries = 5
    auditor = None
    for _ in range(auditor_retries):
        if auditor is None or auditor in auditors:
            auditor = get_auditor_for_commits(ticket_commits, project_id)
    message = (
        f'<{JIRA_TICKET_URL_PREFIX}{ticket_id}|{ticket_id}> '
        f'(<@{auditor}>, сделай ревью)\n'
    )
    for commit in sorted(ticket_commits, key=operator.itemgetter('created_at'), reverse=True):
        message += make_commit_message(commit, project_path, project_id, with_commits_info)
    return message, auditor


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


def fetch_diffs(project_id: int, commit_hash: str) -> List[CommitDiffInfo]:
    return requests.get(
        f'https://gitlab.com/api/v4//projects/{project_id}/repository/commits/{commit_hash}/diff',
        params={'private_token': GITLAB_API_TOKEN},
    ).json()


def get_additions_per_file(diffs_info: List[CommitDiffInfo]) -> List[Tuple[str, int]]:
    additions_per_file: List[Tuple[str, int]] = []
    for diff in diffs_info:
        additions = sum(1 for l in diff['diff'].split('\n') if l.startswith('+'))
        additions_per_file.append(
            (diff['new_path'], additions),
        )
    return additions_per_file


def _is_commit_has_tests(commit: Mapping[str, Any], project_id: int = None) -> bool:
    test_path_parts = [
        '/tests/',
        '/__tests__/',
    ]
    min_additions_in_test_file_lines = 5
    project_id = project_id or commit['project_id']
    raw_diff_info = fetch_diffs(project_id, commit['id'])
    additions_per_file = get_additions_per_file(raw_diff_info)
    for filepath, additions_amount in additions_per_file:
        for path_part in test_path_parts:
            if path_part in filepath and additions_amount >= min_additions_in_test_file_lines:
                return True
    return False


def get_ticket_id(commit) -> Optional[str]:
    commit_message = commit['message'].split('\n')[0].strip()
    match = re.match(COMMIT_REGEXP, commit_message)
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

    commits_list: List[CommitInfo] = []
    for page_num in range(100):
        page_commits = requests.get(
            f'https://gitlab.com/api/v4//projects/{project_id}/repository/commits',
            params={
                'private_token': GITLAB_API_TOKEN,
                'since': since.strftime(date_format),
                'until': until.strftime(date_format),
                'per_page': 100,
                'page': page_num,  # type: ignore
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
            'per_page': 100,  # type: ignore
        },
    ).json()
