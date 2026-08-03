"""Streamlit 기반 웹 채팅 UI.

main.py(CLI)와 동일한 build_graph()를 사용해 로직 중복 없이, 브라우저에서
에이전트와 대화하고 도구 호출을 시각적으로 확인할 수 있게 한다.
"""

import uuid

import streamlit as st

from src.config import OPENAI_MODEL, RECURSION_LIMIT
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
    config = {
        "configurable": {"thread_id": st.session_state.thread_id},
        "recursion_limit": RECURSION_LIMIT,
    }

    with st.chat_message("assistant"):
        tool_calls_seen = []

        def _stream_tokens():
            # stream_mode="messages": call_model이 만드는 토큰을 실시간으로 yield한다.
            # chunk_position == "last"는 메시지의 마지막 조각이라는 뜻으로, 이 시점에
            # tool_calls가 완전히 조립되어 있다(LangChain 공식 스트리밍 패턴).
            pending_call = None
            for chunk, metadata in graph.stream(
                {"messages": [("user", user_input)]},
                config=config,
                stream_mode="messages",
            ):
                if metadata.get("langgraph_node") != "call_model":
                    continue
                pending_call = chunk if pending_call is None else pending_call + chunk
                if chunk.content:
                    yield chunk.content
                if chunk.chunk_position == "last":
                    tool_calls_seen.extend(pending_call.tool_calls)
                    pending_call = None

        final_text = st.write_stream(_stream_tokens)

        for call in tool_calls_seen:
            with st.expander(f"🔧 도구 호출: {call['name']}"):
                st.json(call["args"])

        st.session_state.messages.append({"role": "assistant", "content": final_text})
