import datetime
from typing import Tuple


def get_prev_workday_limits_str(today_date: datetime.date) -> Tuple[str, str]:
    # if today is monday, return commits for friday
    days_offset = 3 if not today_date.weekday() else 1

    yesterday_str = (today_date - datetime.timedelta(days=days_offset))
    today_str = (yesterday_str + datetime.timedelta(days=1))

    return yesterday_str.strftime('%Y-%m-%dT00:00:00Z'), today_str.strftime('%Y-%m-%dT00:00:00Z')


def bool_display(bool_value: bool) -> str:
    return {True: '✅', False: '⛔'}[bool_value]
