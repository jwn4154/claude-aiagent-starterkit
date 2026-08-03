"""CLI로 에이전트와 대화하는 진입점.

streamlit UI(app.py)와 동일한 build_graph()를 사용해 로직이 중복되지 않는다.
"""

from src.config import RECURSION_LIMIT
from src.graph import build_graph

THREAD_ID = "cli-session"


def main() -> None:
    graph = build_graph()
    config = {
        "configurable": {"thread_id": THREAD_ID},
        "recursion_limit": RECURSION_LIMIT,
    }

    print("에이전트와 대화를 시작합니다. 종료하려면 'exit' 또는 'quit'을 입력하세요.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("종료합니다.")
            break
        if not user_input:
            continue

        # stream_mode="messages": 모델이 토큰을 만들어내는 즉시 화면에 출력한다.
        # 도구 호출을 요청하는 메시지는 content가 비어 있으므로 아무것도 찍히지
        # 않고, 도구 실행 뒤 최종 답변을 만드는 call_model 호출부터 텍스트가 보인다.
        print("Agent: ", end="", flush=True)
        pending_call = None
        for chunk, metadata in graph.stream(
            {"messages": [("user", user_input)]}, config=config, stream_mode="messages"
        ):
            if metadata.get("langgraph_node") != "call_model":
                continue
            pending_call = chunk if pending_call is None else pending_call + chunk
            if chunk.content:
                print(chunk.content, end="", flush=True)
            # chunk_position == "last": 이 메시지의 마지막 조각이라는 뜻이므로
            # 이 시점에 tool_calls가 완전히 조립되어 있다 (LangChain 공식 패턴).
            if chunk.chunk_position == "last":
                for call in pending_call.tool_calls:
                    print(f"\n  🔧 도구 호출: {call['name']}({call['args']})")
                pending_call = None
        print("\n")


if __name__ == "__main__":
    main()
