import os
from typing import Final, List, Tuple, Mapping

GITLAB_API_TOKEN: str = os.environ['GITLAB_API_TOKEN']
DOGGIE_SLACK_TOKEN = os.environ.get('DOGGIE_SLACK_TOKEN')
JIRA_TICKET_URL_PREFIX = os.environ.get('JIRA_TICKET_URL_PREFIX')
SLACK_HOOK_URL = os.environ['SLACK_HOOK_URL']
COMMIT_REGEXP = os.environ['COMMIT_REGEXP']  # should fetch from repo settings

PROJECTS_INFO: Final[List[Tuple[int, str, str, str]]] = [
    # (
    #   project_id,
    #   project_human_name,
    #   slack_channel_to_notify,
    #   gitlab_project_url,
    # ),
    # ...
]

DEVELEOPERS_INFO: Final[List[Tuple[str, List]]] = [
    # (dev_group_name, [(dev_commit_email, dev_slack_id), ...]),
    # ...
]

REPO_TO_CODETYPE_MAPPING: Mapping[int, str] = {
    # gitlab_project_id: dev_group_name,
    # ...
}

DEVELEOPERS_EMAILS = [d[0] for g in DEVELEOPERS_INFO for d in g[1]]

# this should be taken from gitlab repo settings
MASTER_BRANCH_NAME = 'devel'


DEBUG = os.environ.get('DOGGIE_DEBUG', 'True') == 'True'
DEBUG_SLACK_CHANNEL_ID = os.environ.get('DEBUG_SLACK_CHANNEL_ID')


BASE_CORE_DIR = os.environ.get('BASE_CORE_DIR', '/var/www/core/')
GET_CORE_STAT_SHELL_COMMAND = os.environ.get('GET_CORE_STAT_SHELL_COMMAND')

try:
    from local_config import *  # noqa: F401, F403
except ModuleNotFoundError:
    pass
