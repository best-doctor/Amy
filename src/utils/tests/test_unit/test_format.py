import datetime

import pytest

from src.utils.format import get_prev_workday_limits_str, bool_display


def test_get_prev_workday_limits_str():
    today_date = datetime.date(2020, 5, 10)

    yesterday_str, today_str = get_prev_workday_limits_str(today_date)

    assert yesterday_str == '2020-05-09T00:00:00Z'
    assert today_str == '2020-05-10T00:00:00Z'


@pytest.mark.parametrize('value, expected_result', [
    (True, '✅'),
    (False, '⛔'),
])
def test_bool_display(value, expected_result):
    assert bool_display(value) == expected_result
