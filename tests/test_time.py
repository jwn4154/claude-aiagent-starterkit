"""get_current_time 도구 테스트.

zoneinfo 기반 타임존 검증이 정상 타임존은 형식에 맞게 반환하고,
존재하지 않는 타임존은 에러 메시지로 처리하는지 확인한다.
"""

import re

from src.tools.time import get_current_time

_TIME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ")


def test_default_timezone_returns_formatted_time():
    result = get_current_time.invoke({})

    assert _TIME_PATTERN.match(result)


def test_explicit_timezone_returns_formatted_time():
    result = get_current_time.invoke({"timezone": "UTC"})

    assert _TIME_PATTERN.match(result)
    assert "UTC" in result


def test_unknown_timezone_returns_error_message():
    result = get_current_time.invoke({"timezone": "Not/AZone"})

    assert "알 수 없는 타임존" in result


def test_empty_timezone_returns_error_message():
    result = get_current_time.invoke({"timezone": ""})

    assert "알 수 없는 타임존" in result
