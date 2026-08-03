"""도구 예제 1: 산술 계산기.

외부 API나 패키지 의존성 없이 LangChain @tool 데코레이터 패턴만 보여주는
가장 단순한 예제. eval()은 임의 코드 실행 위험이 있어 사용하지 않고,
ast로 파싱한 뒤 허용된 연산자만 재귀적으로 계산한다.
"""

import ast
import operator

from langchain_core.tools import tool

# 허용할 연산자만 화이트리스트로 명시 — 여기 없는 연산은 전부 거부된다.
_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _ALLOWED_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_eval_node(node.operand))
    # 화이트리스트에 없는 노드(함수 호출, 이름 참조 등)는 전부 차단한다.
    raise ValueError(f"허용되지 않은 수식 요소입니다: {ast.dump(node)}")


@tool
def calculator(expression: str) -> str:
    """산술 표현식을 계산한다. 사칙연산과 거듭제곱을 지원한다.

    Args:
        expression: 계산할 수식 문자열. 예: "3 + 5 * 2", "(10 - 4) / 2"
    """
    try:
        parsed = ast.parse(expression, mode="eval")
        result = _eval_node(parsed.body)
        return str(result)
    except (SyntaxError, ValueError, ZeroDivisionError, TypeError) as e:
        return f"계산 실패: {e}"
