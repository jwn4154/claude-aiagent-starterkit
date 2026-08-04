---
description: pytest, ruff, 그래프 빌드 스모크 테스트를 한 번에 실행해 로컬 상태를 검증한다
---

이 프로젝트의 전체 로컬 검증을 순서대로 실행하고 결과를 요약한다. 하나라도 실패하면 멈추지 말고 끝까지 실행한 뒤, 마지막에 통과/실패 항목을 표로 정리해서 보고한다.

1. `.venv`가 있는지 확인하고, 있으면 `.venv/bin/pytest`, `.venv/bin/ruff`를 쓴다. 없으면 시스템 `pytest`/`ruff`를 시도하되, 없다면 `pip install -r requirements-dev.txt`가 필요하다고 안내한다.
2. `pytest -v` 실행 — `src/tools`의 순수 함수 테스트. API 키 없이도 통과해야 정상이다.
3. `ruff check .` 실행 — 실패하면 자동수정 가능한 항목이 있는지 확인하고(`ruff check . --fix`), 수정 후 파일 diff를 보여준다.
4. 그래프 빌드 스모크 테스트: `python -c "from src.graph import build_graph; build_graph(); print('OK')"` 실행 — 실제 모델을 호출하지 않고 그래프 구성 자체(노드/엣지/체크포인터)가 깨지지 않았는지만 확인한다.
5. 위 3단계에서 새로 생성된 파일(`checkpoints.db` 등)이 있다면 정리한다.

마지막으로 pytest 통과 개수, ruff 통과 여부, 그래프 빌드 성공 여부를 한 줄씩 요약해서 보고한다.
