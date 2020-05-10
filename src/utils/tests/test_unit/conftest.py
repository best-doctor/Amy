import pytest


@pytest.fixture
def request_post_mock(mocker):
    return mocker.patch('requests.post')


@pytest.fixture
def commit_info():
    return {
        'id': '4f4d0753c9b26eee8c0820ebd1210bf360ab08cc',
        'short_id': '4f4d0752',
        'created_at': '2020-05-09T23:36:25.000+03:00',
        'parent_ids': ['2093c0c2631cc669680b8b2e73b8a713ed6767be'],
        'title': 'Test',
        'message': 'Test\n',
        'author_name': 'Test Test',
        'author_email': 'test@test.com',
        'authored_date': '2020-05-09T23:36:25.000+03:00',
        'committer_name': 'Test Test',
        'committer_email': 'test@test.com',
        'committed_date': '2020-05-09T23:36:25.000+03:00',
        'web_url': 'https://gitlab.com/test-group/test-repo/-/commit/4f4d0753c0bf360ab08cc',
        'stats': {'additions': 0, 'deletions': 0, 'total': 0},
    }


@pytest.fixture
def revert_commit_info():
    return {
        'id': '4f4d0753c9b26eee8c0820ebd1210bf360ab08cc',
        'short_id': '4f4d0752',
        'created_at': '2020-05-09T23:36:25.000+03:00',
        'parent_ids': ['2093c0c2631cc669680b8b2e73b8a713ed6767be'],
        'title': 'Revert Test',
        'message': 'Revert Test\n',
        'author_name': 'Test Test',
        'author_email': 'test@test.com',
        'authored_date': '2020-05-09T23:36:25.000+03:00',
        'committer_name': 'Test Test',
        'committer_email': 'test@test.com',
        'committed_date': '2020-05-09T23:36:25.000+03:00',
        'web_url': 'https://gitlab.com/test-group/test-repo/-/commit/4f4d0753c91210bf360ab08cc',
        'stats': {'additions': 0, 'deletions': 0, 'total': 0},
    }
