"""도구 예제 2: 웹 검색 (Tavily).

외부 서비스를 호출하는 도구의 예제. TAVILY_API_KEY가 없어도 스타터킷 실행
자체는 깨지지 않도록, 키가 없을 때는 에러 대신 안내 메시지를 반환한다.
"""

from langchain_core.tools import tool

from src.config import TAVILY_API_KEY


@tool
def web_search(query: str) -> str:
    """최신 정보나 인터넷 검색이 필요한 질문에 사용한다.

    Args:
        query: 검색어
    """
    if not TAVILY_API_KEY:
        return (
            "web_search 도구를 사용하려면 .env에 TAVILY_API_KEY를 설정해야 합니다. "
            "https://tavily.com 에서 무료로 발급받을 수 있습니다."
        )

    # 지연 import: 키가 없는 환경에서는 tavily-python이 아예 필요 없게 한다.
    from tavily import TavilyClient

    client = TavilyClient(api_key=TAVILY_API_KEY)
    response = client.search(query, max_results=5)

    results = response.get("results", [])
    if not results:
        return f"'{query}'에 대한 검색 결과가 없습니다."

    lines = [f"- {r['title']}: {r['content'][:200]} ({r['url']})" for r in results]
    return "\n".join(lines)
