# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소에서 작업할 때 참고하는 가이드다.

**한국어로 응답한다** — 로컬 세션이든 클라우드/Slack/모바일 세션이든 동일하게 적용된다. 클라우드 세션은 로컬 `~/.claude/settings.json`을 읽지 못하고 이 저장소의 CLAUDE.md만 보므로, 이 지시문을 지우면 클라우드 세션이 영어로 응답하게 된다. 코드·식별자·기술 용어는 원어(영어) 유지.

## 이 저장소는

LangGraph + OpenAI 기반 에이전트 스타터킷이다. CLI(`main.py`)와 Streamlit 웹 UI(`app.py`) 두 진입점을 제공한다. 저장소 이름은 "claude"지만 현재 구현은 **OpenAI**가 기본값이다 — Claude로 전환하는 법은 README.md "나중에 Claude로 전환하는 법" 참고. 설치·실행·개별 도구 소개 같은 사용법 전반은 README.md에 있다.

## 자주 쓰는 명령어

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # OPENAI_API_KEY 채우기 (TAVILY_API_KEY는 선택)
```

```bash
python main.py           # CLI
streamlit run app.py     # 웹 UI
```

검증은 `/verify`(pytest + ruff + 그래프 빌드 스모크 테스트를 한 번에 실행)를 우선 쓴다. 개별 실행:
```bash
pytest -v
pytest tests/test_calculator.py::test_basic_arithmetic -v   # 단일 테스트
ruff check .
ruff check . --fix
```
CI(`.github/workflows/ci.yml`)는 **Python 3.12** 고정이다 — 로컬 `.venv`가 다른 버전(예: 3.14)이면 CI와 동작이 갈릴 수 있다.

## 커스텀 명령어와 서브에이전트

- `/add-tool <이름> <설명>` — 새 도구를 이 저장소 관례대로 스캐폴딩하고 `ALL_TOOLS`에 등록, 테스트까지 생성한다. **새 도구를 추가할 땐 손으로 하지 말고 이걸 먼저 쓴다.**
- `/verify` — pytest + ruff + `build_graph()` 스모크 테스트를 한 번에 실행.
- `/inspect-thread <thread_id>` — `checkpoints.db`(sqlite 체크포인터)의 대화 기록을 사람이 읽을 수 있게 출력. **`checkpoints.db`는 직렬화된 바이너리라 sqlite CLI로 직접 열어도 못 읽는다** — 반드시 이 명령어(내부적으로 `SqliteSaver` API 사용)를 쓴다.
- `code-reviewer` 서브에이전트 — 의미 있는 코드 변경을 마친 직후에는 사용자가 요청하지 않아도 먼저 이걸로 스스로 검토한다.
- `debugger` 서브에이전트 — 에러/예상과 다른 동작의 근본 원인 조사용.

## 아키텍처

`call_model ↔ tools` 사이를 오가는 LangGraph `StateGraph`:
```
call_model → (tool_calls 있음?) → tools → call_model → ... → END
```
- `src/graph.py`의 `build_graph()`가 그래프 정의의 단일 출처다. `main.py`/`app.py` 둘 다 이 함수를 호출해 그래프 자체는 중복 정의되지 않는다. **다만 그래프를 소비하는 스트리밍 청크 누적 루프(`pending_call` 패턴, `main.py:33-47` / `app.py:56-69`)는 두 파일에 그대로 복제되어 있다** — 스트리밍 동작을 고칠 땐 두 곳 다 손봐야 한다.
- 그래프는 앱 수명 동안 한 번만 만들고 재사용해야 한다(요청마다 재생성 금지) — 체크포인터가 그래프 인스턴스에 물려 있어서 재생성하면 대화 기록이 끊긴다.
- 라우팅은 커스텀 조건 함수 대신 LangGraph의 `tools_condition` prebuilt 헬퍼를 쓴다.
- 대화 상태는 `thread_id` 기준 체크포인터가 관리한다. CLI는 고정값 `"cli-session"`, Streamlit은 브라우저 세션마다 새 UUID.
- `RECURSION_LIMIT`은 그래프 자체의 속성이 아니라 **호출자**(`main.py`/`app.py`)가 `config["recursion_limit"]`로 주입한다. `build_graph()`를 새 진입점(테스트, 서버 등)에서 쓰면 이 안전장치가 자동으로 따라오지 않으니 직접 넣어야 한다.
- 시스템 프롬프트는 **없다**. `call_model`은 `model.invoke(state["messages"])`를 그대로 호출한다 — 에이전트 성격/지침을 넣으려면 `graph.py`의 `call_model`을 직접 고쳐야 한다.
- `main.py`/`app.py`는 `graph.invoke()` 대신 `graph.stream(..., stream_mode="messages")`를 써서 토큰이 생성되는 즉시 출력한다. `(chunk, metadata)` 중 `metadata["langgraph_node"] == "call_model"`인 것만 골라 `+`로 누적하고, `chunk.chunk_position == "last"`가 되는 시점에 누적된 메시지의 `.tool_calls`가 완전히 조립된다 — LangChain 공식 문서(docs.langchain.com/oss/python/langchain/streaming)의 패턴이다. 더 새로운 `stream_events(version="v3")` + `ToolCallTransformer` API도 설치된 버전에 있지만 아직 experimental이라 의도적으로 안 썼다.

## 도구 (`src/tools/`)

`src/tools/__init__.py`의 `ALL_TOOLS`에 4개 등록: `calculator`, `web_search`, `read_local_file`, `get_current_time`. 전부 `@tool` 데코레이터 + 실패 시 예외를 던지지 않고 한국어 안내 문자열을 반환하는 공통 패턴을 따른다 — 손으로 새 도구를 만들 때도 이 패턴을 유지한다(가급적 `/add-tool` 사용). 개별 도구 설명은 README.md "예제 도구 4개" 참고.

## 함정과 제약

**미해결 결함** (알려진 것, 고치는 건 별도 요청 시)
- `web_search`(`src/tools/web_search.py`)는 `TAVILY_API_KEY`가 없을 때만 안내 메시지를 반환한다. 키가 있는데 Tavily가 401/타임아웃/rate limit을 내면 try/except가 없어 예외가 그대로 전파되어 그래프가 죽는다 — 다른 3개 도구와 다른 유일한 예외.
- `_build_checkpointer()`(`src/graph.py`)는 `CHECKPOINTER_BACKEND == "sqlite"` **완전일치**만 검사한다. `SQLITE`, 오타, 공백이 섞이면 경고 없이 조용히 `InMemorySaver`로 폴백한다 — "sqlite로 설정했는데 재시작하니 대화가 날아갔다"의 흔한 원인.
- sqlite 커넥션(`sqlite3.connect(...)`)을 close하지 않는다.
- `calculator`는 `ast.Pow`를 허용해 `9**9**9` 같은 입력으로 느려질 수 있다.
- `web_search`만 유닛 테스트가 없다(외부 API 의존 때문으로 보임). 나머지 3개 도구는 있다.
- ruff 설정 파일(`pyproject.toml`/`ruff.toml`)이 없어 **기본 룰셋만** 동작한다(pycodestyle 일부 + Pyflakes). import 정렬 같은 건 강제되지 않는다 — 의도적으로 안 만든 건지 아직 손을 안 댄 건지는 코드만으로 알 수 없다.

**의도적 설계** (버그 아님)
- Claude Opus 5로 전환 시 `temperature`/`top_p`/`top_k`를 설정하면 400 에러가 난다 — 두 프로바이더 모두 이 파라미터를 아예 안 쓴다.
- `MAX_TOKENS`(4096), `WORKSPACE_DIR`, `CHECKPOINTER_SQLITE_PATH`는 `src/config.py`에 하드코딩되어 있어 환경변수로 못 바꾼다. (`OPENAI_MODEL`/`RECURSION_LIMIT`/`CHECKPOINTER_BACKEND`/API 키들은 `.env`로 오버라이드된다.)
- 기본 `InMemorySaver`는 데모/개발용 — 프로세스 재시작하면 대화가 사라진다. `CHECKPOINTER_BACKEND=sqlite`는 로컬 단일 프로세스 영속화만 해결한다(다중 인스턴스는 `PostgresSaver` 필요).
- 도구 호출 여부는 비결정적이다 — "오늘 날씨 어때"처럼 위치 등이 빠진 모호한 질문엔 모델이 `web_search`를 호출할 때도, 안 할 때도 있다. 그래프/스트리밍 코드 버그가 아니라 LLM 특성이다.
- Slack 알림 hook(`.claude/settings.json` + `.claude/hooks/notify-slack.sh`)이 저장소에 커밋되어 있다. 실제로 동작하려면 `.claude/hooks/.env.example`을 복사해 `SLACK_WEBHOOK_URL`을 채운 `.claude/hooks/.env`가 필요한데, 이건 gitignore 대상이라 새로 클론한 환경엔 없다 — 없어도 hook은 에러 없이 조용히 아무것도 안 하고 넘어간다.

## 커밋 관행

한국어 제목 + (필요시) "왜"를 설명하는 한국어 본문. `feat:`/`fix:` 같은 Conventional Commits 접두사는 쓰지 않는다.
