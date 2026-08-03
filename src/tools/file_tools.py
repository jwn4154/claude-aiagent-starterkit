"""도구 예제 3: 로컬 파일 읽기.

client-side 파일 도구의 보안 패턴을 보여주는 예제 — 모델이 넘긴 경로를
그대로 신뢰하지 않고, WORKSPACE_DIR로 정규화(resolve)한 뒤 그 바깥으로
벗어나면(경로 순회 공격 등) 거부한다.
"""

from pathlib import Path

from langchain_core.tools import tool

from src.config import WORKSPACE_DIR


@tool
def read_local_file(path: str) -> str:
    """workspace 디렉터리 안의 텍스트 파일을 읽는다. 다른 경로는 접근할 수 없다.

    Args:
        path: workspace 디렉터리 기준 상대 경로. 예: "sample.txt"
    """
    # 모델이 준 경로는 신뢰할 수 없는 입력이므로, 정규화 후 루트 이탈 여부를
    # 먼저 검증한다 — 문자열 비교(startswith)가 아니라 resolve된 경로로 비교해야
    # "../" 나 심볼릭 링크를 통한 우회를 막을 수 있다.
    candidate = (WORKSPACE_DIR / path).resolve()
    if not candidate.is_relative_to(WORKSPACE_DIR):
        return f"거부됨: '{path}'는 workspace 디렉터리 밖의 경로입니다."

    if not candidate.exists():
        return f"파일을 찾을 수 없습니다: {path}"
    if not candidate.is_file():
        return f"파일이 아닙니다: {path}"

    try:
        return candidate.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"텍스트 파일이 아니라 읽을 수 없습니다: {path}"
