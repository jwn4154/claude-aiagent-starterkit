"""에이전트 전역 설정.

.env 파일에서 환경변수를 로드하고, 모델/도구가 공통으로 참조하는 상수를 정의한다.
CLI(main.py)와 Streamlit UI(app.py)가 이 모듈을 공용으로 import한다.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# OpenAI 설정 — 모델명은 환경변수로 오버라이드 가능하게 해서
# 크레딧/성능에 따라 gpt-4o-mini 등으로 쉽게 바꿔볼 수 있게 한다.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
MAX_TOKENS = 4096

# Tavily 웹 검색 (선택) — 키가 없으면 web_search 도구가 안내 메시지를 반환한다.
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# file_tools 도구가 접근을 허용하는 유일한 디렉터리.
# 모델이 임의 경로(../etc/passwd 등)를 요청해도 이 루트 밖으로 못 나가게 강제한다.
WORKSPACE_DIR = (Path(__file__).resolve().parent.parent / "workspace").resolve()

# call_model ↔ tools 사이를 오가는 최대 횟수. 모델이 도구 호출을 무한 반복하는
# 경우(예: 같은 도구를 계속 잘못된 인자로 호출) 대비한 안전장치다.
RECURSION_LIMIT = int(os.getenv("RECURSION_LIMIT", "25"))

# 체크포인터 백엔드 선택: "memory"(기본값, 프로세스 재시작 시 대화 소실)
# 또는 "sqlite"(로컬 파일에 영속 저장, 재시작해도 대화 유지).
CHECKPOINTER_BACKEND = os.getenv("CHECKPOINTER_BACKEND", "memory")
CHECKPOINTER_SQLITE_PATH = str(
    Path(__file__).resolve().parent.parent / "checkpoints.db"
)
