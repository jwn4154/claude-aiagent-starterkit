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
