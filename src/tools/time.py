"""도구 예제 4: 현재 날짜와 시간 조회.

외부 API 없이 표준 라이브러리(datetime, zoneinfo)만으로 구현하는 예제.
zoneinfo는 Python 3.9+ 표준 라이브러리라 별도 의존성 추가가 필요 없다.
"""

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain_core.tools import tool

_DEFAULT_TIMEZONE = "Asia/Seoul"


@tool
def get_current_time(timezone: str = _DEFAULT_TIMEZONE) -> str:
    """현재 날짜와 시간을 지정한 타임존 기준으로 반환한다.

    Args:
        timezone: IANA 타임존 이름. 예: "Asia/Seoul", "UTC", "America/New_York".
            생략하면 기본값 "Asia/Seoul"을 사용한다.
    """
    # 모델이 준 타임존 문자열은 신뢰할 수 없는 입력이므로, ZoneInfo 생성
    # 시점에 검증한다. 빈 문자열은 ValueError, 존재하지 않는 이름은
    # ZoneInfoNotFoundError로 각각 다르게 실패하므로 둘 다 잡아야 한다.
    try:
        tz = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        return (
            f"알 수 없는 타임존입니다: '{timezone}'. "
            "예: 'Asia/Seoul', 'UTC', 'America/New_York'"
        )

    now = datetime.now(tz)
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")
