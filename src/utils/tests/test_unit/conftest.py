import pytest


@pytest.fixture
def request_post_mock(mocker):
    return mocker.patch('requests.post')
