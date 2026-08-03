"""Streamlit 기반 웹 채팅 UI.

main.py(CLI)와 동일한 build_graph()를 사용해 로직 중복 없이, 브라우저에서
에이전트와 대화하고 도구 호출을 시각적으로 확인할 수 있게 한다.
"""

import uuid

import streamlit as st

from src.config import OPENAI_MODEL
from src.graph import build_graph


@st.cache_resource
def get_graph():
    # Streamlit은 상호작용마다 스크립트를 처음부터 다시 실행하므로,
    # 그래프(+체크포인터)를 캐싱하지 않으면 매번 새로 만들어져 대화 기록이 끊긴다.
    return build_graph()


st.set_page_config(page_title="AI Agent Starter Kit", page_icon="🤖")
st.title("🤖 AI Agent Starter Kit")

with st.sidebar:
    st.caption(f"모델: {OPENAI_MODEL}")
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    st.caption(f"세션 ID: {st.session_state.thread_id[:8]}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    graph = get_graph()
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    with st.chat_message("assistant"):
        prior_state = graph.get_state(config)
        prior_count = len(prior_state.values.get("messages", []))

        result = graph.invoke({"messages": [("user", user_input)]}, config=config)
        new_messages = result["messages"][prior_count:]

        for message in new_messages:
            tool_calls = getattr(message, "tool_calls", None)
            if tool_calls:
                for call in tool_calls:
                    with st.expander(f"🔧 도구 호출: {call['name']}"):
                        st.json(call["args"])

        final_message = result["messages"][-1]
        st.markdown(final_message.content)
        st.session_state.messages.append(
            {"role": "assistant", "content": final_message.content}
        )
