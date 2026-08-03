"""calculator 도구 테스트.

ast 기반 화이트리스트 파서가 사칙연산은 정상 계산하고, 화이트리스트에
없는 노드(함수 호출, 이름 참조 등)는 확실히 거부하는지 확인한다.
"""

from src.tools.calculator import calculator


def test_basic_arithmetic():
    assert calculator.invoke({"expression": "3 + 5 * 2"}) == "13"


def test_parentheses_and_division():
    assert calculator.invoke({"expression": "(10 - 4) / 2"}) == "3.0"


def test_power_and_unary_minus():
    assert calculator.invoke({"expression": "-2 ** 3"}) == "-8"


def test_division_by_zero_returns_error_message():
    result = calculator.invoke({"expression": "1 / 0"})
    assert "계산 실패" in result


def test_invalid_syntax_returns_error_message():
    result = calculator.invoke({"expression": "3 + "})
    assert "계산 실패" in result


def test_function_call_is_rejected():
    # __import__("os").system("...") 같은 임의 코드 실행을 막는 핵심 보안 동작
    result = calculator.invoke({"expression": "__import__('os')"})
    assert "계산 실패" in result


def test_name_reference_is_rejected():
    result = calculator.invoke({"expression": "x + 1"})
    assert "계산 실패" in result
