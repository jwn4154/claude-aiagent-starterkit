"""CLI로 에이전트와 대화하는 진입점.

streamlit UI(app.py)와 동일한 build_graph()를 사용해 로직이 중복되지 않는다.
"""

from src.graph import build_graph

THREAD_ID = "cli-session"


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": THREAD_ID}}

    print("에이전트와 대화를 시작합니다. 종료하려면 'exit' 또는 'quit'을 입력하세요.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("종료합니다.")
            break
        if not user_input:
            continue

        # checkpointer가 전체 대화를 누적하므로, 이번 턴에 새로 추가된
        # 메시지만 구분해서 도구 호출 로그를 보여주기 위해 호출 전 개수를 기록한다.
        prior_state = graph.get_state(config)
        prior_count = len(prior_state.values.get("messages", []))

        result = graph.invoke({"messages": [("user", user_input)]}, config=config)
        new_messages = result["messages"][prior_count:]

        for message in new_messages:
            tool_calls = getattr(message, "tool_calls", None)
            if tool_calls:
                for call in tool_calls:
                    print(f"  🔧 도구 호출: {call['name']}({call['args']})")

        final_message = result["messages"][-1]
        print(f"Agent: {final_message.content}\n")


if __name__ == "__main__":
    main()
