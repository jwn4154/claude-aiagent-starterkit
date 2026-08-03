"""LangGraph 기반 에이전트 정의.

모델 호출(call_model) ↔ 도구 실행(tools) 사이를 오가는 상태 그래프를 구성한다.
CLI(main.py)와 Streamlit UI(app.py)가 build_graph()를 공용으로 사용해서
에이전트 로직이 두 곳에 중복되지 않게 한다.
"""

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.config import MAX_TOKENS, OPENAI_MODEL
from src.tools import ALL_TOOLS


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

    # InMemorySaver는 프로세스 메모리에만 저장되는 데모/개발용 체크포인터다.
    # 재시작하면 대화가 사라지며, 프로덕션에서는 PostgresSaver 등으로 교체해야 한다.
    checkpointer = InMemorySaver()
    return graph_builder.compile(checkpointer=checkpointer)
