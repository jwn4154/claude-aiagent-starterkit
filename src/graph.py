"""LangGraph 기반 에이전트 정의.

모델 호출(call_model) ↔ 도구 실행(tools) 사이를 오가는 상태 그래프를 구성한다.
CLI(main.py)와 Streamlit UI(app.py)가 build_graph()를 공용으로 사용해서
에이전트 로직이 두 곳에 중복되지 않게 한다.
"""

import sqlite3

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.config import (
    CHECKPOINTER_BACKEND,
    CHECKPOINTER_SQLITE_PATH,
    MAX_TOKENS,
    OPENAI_MODEL,
)
from src.tools import ALL_TOOLS


def _build_checkpointer():
    """CHECKPOINTER_BACKEND 설정에 따라 체크포인터를 만든다.

    "sqlite"면 로컬 파일(checkpoints.db)에 영속 저장해 재시작해도 대화가
    유지된다. check_same_thread=False가 필요한 이유: Streamlit은 요청마다
    다른 스레드에서 이 커넥션을 재사용하기 때문이다.
    기본값 "memory"는 프로세스 메모리에만 저장되는 데모/개발용이다.
    """
    if CHECKPOINTER_BACKEND == "sqlite":
        conn = sqlite3.connect(CHECKPOINTER_SQLITE_PATH, check_same_thread=False)
        return SqliteSaver(conn)
    return InMemorySaver()


def build_graph():
    """컴파일된 LangGraph 에이전트를 반환한다.

    thread_id별 대화 맥락이 유지되려면 이 함수가 반환한 그래프 인스턴스를
    (매 요청마다 새로 만들지 말고) 앱 수명 동안 재사용해야 한다 — 체크포인터가
    그래프 인스턴스에 물려 있기 때문이다.
    """
    model = ChatOpenAI(model=OPENAI_MODEL, max_tokens=MAX_TOKENS).bind_tools(ALL_TOOLS)

    def call_model(state: MessagesState):
        response = model.invoke(state["messages"])
        return {"messages": [response]}

    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("call_model", call_model)
    graph_builder.add_node("tools", ToolNode(ALL_TOOLS))

    graph_builder.set_entry_point("call_model")
    # tools_condition(공식 prebuilt 헬퍼): 마지막 메시지에 tool_calls가 있으면
    # "tools" 노드로, 없으면 END로 라우팅한다. 직접 조건 함수를 짤 필요가 없다.
    graph_builder.add_conditional_edges("call_model", tools_condition)
    graph_builder.add_edge("tools", "call_model")

    checkpointer = _build_checkpointer()
    return graph_builder.compile(checkpointer=checkpointer)
