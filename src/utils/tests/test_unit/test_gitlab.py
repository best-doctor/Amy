from src.utils.gitlab import is_revert_commit


def test_is_revert_commit(commit_info):
    assert is_revert_commit(commit_info) is False


def test_is_revert_commit_true_case(revert_commit_info):
    assert is_revert_commit(revert_commit_info) is True
