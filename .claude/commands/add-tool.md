---
description: LangGraph 에이전트에 새 도구(tool)를 스캐폴딩하고 ALL_TOOLS에 등록한다
argument-hint: <tool_name> <이 도구가 하는 일에 대한 설명>
---

전달받은 인자: "$ARGUMENTS"

이 문자열의 **첫 번째 단어(공백 기준)를 도구 이름**으로, **그 뒤에 오는 나머지 전체를 도구 설명**으로 직접 파싱한다 (위치 인자 `$1`/`$2` 치환에 의존하지 말 것 — 따옴표로 감싼 인자가 있으면 오동작한 전례가 있다). 도구 이름은 파일명이자 Python 함수명으로 쓰이므로 `snake_case` 영문 식별자여야 한다. 만약 첫 단어가 유효한 Python 식별자가 아니면(공백, 한글, 특수문자 등) 진행을 멈추고 사용자에게 올바른 이름을 물어본다.

파싱한 도구 이름을 이후 지시에서 `<tool_name>`으로 표기한다. 다음 순서로 진행한다:

1. **기존 패턴 파악**: `src/tools/calculator.py`, `src/tools/web_search.py`, `src/tools/file_tools.py` 를 모두 읽고 이 프로젝트의 도구 작성 관례를 파악한다.
   - 파일 맨 위에 "도구 예제 N: ..." 형식의 한국어 docstring으로 이 도구가 무엇이고 어떤 설계 결정을 담고 있는지 설명
   - `@tool` 데코레이터를 쓰고, 함수 docstring에 `Args:` 섹션으로 파라미터를 설명 (모델이 이 docstring을 보고 언제/어떻게 호출할지 판단하므로 명확하게 작성)
   - 에러 상황에서 예외를 그대로 던지지 않고 사람이 읽을 수 있는 한국어 에러 메시지 문자열을 반환 (예: calculator의 `f"계산 실패: {e}"`)
   - 외부 API 키가 필요하면 `src/config.py`에서 가져오고, 키가 없을 때는 안내 메시지를 반환하도록 처리 (`web_search.py` 참고)
   - 신뢰할 수 없는 입력(경로, 임의 코드 등)을 다룬다면 `file_tools.py`의 화이트리스트/샌드박싱 패턴 참고
   - 표준 라이브러리만으로 충분하면 외부 의존성을 추가하지 않는다

2. **`src/tools/<tool_name>.py` 생성**: 위 관례를 따라 함수를 `@tool`로 정의한다. 함수 이름은 도구 이름 그대로 쓰거나(`calculator`, `web_search`처럼), 더 명확한 동사구가 있다면 그것을 쓴다(`file_tools.py`의 `read_local_file`처럼 파일명과 함수명이 다를 수 있음). 설명에 맞는 파라미터와 로직을 구현한다.

3. **`src/tools/__init__.py` 갱신**: `from src.tools.<tool_name> import <함수명>`을 추가하고, `ALL_TOOLS` 리스트 끝에 `<함수명>`을 추가한다. 이 외에는 아무것도 수정하지 않는다 — `graph.py`는 `ALL_TOOLS`를 그대로 참조하므로 별도 수정이 필요 없다.

4. **`tests/test_<tool_name>.py` 작성**: `tests/test_calculator.py`, `tests/test_file_tools.py`를 참고해서 최소 2~3개의 테스트 케이스를 작성한다 (정상 동작 1개 + 에러/경계 케이스 1개 이상). 도구가 파일시스템이나 외부 상태를 건드린다면 `test_file_tools.py`의 `monkeypatch` 픽스처 패턴을 참고해 격리한다.

5. **검증**: `pytest tests/test_<tool_name>.py -v`, 전체 `pytest -q`, `ruff check .`를 실행해서 통과하는지 확인하고, 가능하면 `build_graph()`로 실제 모델이 도구를 호출하는지까지 확인한 뒤 결과를 보고한다.
