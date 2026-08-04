"""도구 목록을 한곳에 모아 graph.py에서 가져다 쓸 수 있게 한다.

새 도구를 추가하려면: 1) 이 디렉터리에 @tool로 함수를 정의한 파일을 만들고
2) 아래 import와 ALL_TOOLS 리스트에 추가하면 된다.
"""

from src.tools.calculator import calculator
from src.tools.file_tools import read_local_file
from src.tools.time import get_current_time
from src.tools.web_search import web_search

ALL_TOOLS = [calculator, web_search, read_local_file, get_current_time]
