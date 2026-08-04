---
description: CHECKPOINTER_BACKEND=sqlite로 저장된 checkpoints.db에서 특정 thread_id의 대화 기록을 읽어서 보여준다
argument-hint: <thread_id> [db_path (기본값: checkpoints.db)]
---

`checkpoints.db`(sqlite 체크포인터)에 저장된 대화 중 `thread_id`가 `$1`인 세션의 전체 메시지 기록을 사람이 읽을 수 있는 형태로 출력한다. 원시 테이블(`checkpoints`, `writes`)은 직렬화된 바이너리라 sqlite CLI로 직접 봐도 못 읽으므로, 반드시 LangGraph의 `SqliteSaver` API로 디코딩해야 한다.

DB 파일 경로는 두 번째 인자가 있으면 그 값을, 없으면 프로젝트 루트의 `checkpoints.db`를 사용한다.

다음 파이썬 코드를 실행한다 (thread_id와 db 경로만 채워서):

```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

conn = sqlite3.connect("<db_path>", check_same_thread=False)
saver = SqliteSaver(conn)

config = {"configurable": {"thread_id": "<thread_id>"}}
checkpoint = saver.get(config)

if checkpoint is None:
    print(f"'<thread_id>'에 해당하는 저장된 대화가 없습니다.")
else:
    messages = checkpoint["channel_values"].get("messages", [])
    print(f"저장된 메시지 {len(messages)}개:")
    for m in messages:
        role = type(m).__name__
        content = m.content if m.content else getattr(m, "tool_calls", "")
        print(f"  [{role}] {content}")
```

DB 파일이 존재하지 않으면, `CHECKPOINTER_BACKEND=sqlite`로 앱을 실행한 적이 없다는 뜻이므로 그렇게 안내한다. 저장된 `thread_id` 목록이 궁금하다고 하면 `SELECT DISTINCT thread_id FROM checkpoints`로 조회해서 보여준다.
