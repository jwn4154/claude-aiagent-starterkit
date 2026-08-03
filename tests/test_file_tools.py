"""read_local_file 도구 테스트.

핵심 보안 로직인 workspace 디렉터리 이탈 방지(경로 순회 공격 차단)를
반드시 고정해둔다 — 이 로직이 깨지면 모델이 임의 파일을 읽을 수 있게 된다.
"""

import pytest

from src.tools import file_tools


@pytest.fixture(autouse=True)
def workspace_dir(tmp_path, monkeypatch):
    """WORKSPACE_DIR을 테스트용 임시 디렉터리로 바꿔서 실제 workspace/를 건드리지 않는다."""
    monkeypatch.setattr(file_tools, "WORKSPACE_DIR", tmp_path)
    return tmp_path


def test_reads_file_inside_workspace(workspace_dir):
    (workspace_dir / "sample.txt").write_text("안녕하세요", encoding="utf-8")

    result = file_tools.read_local_file.invoke({"path": "sample.txt"})

    assert result == "안녕하세요"


def test_rejects_path_traversal_outside_workspace(workspace_dir):
    result = file_tools.read_local_file.invoke({"path": "../secret.txt"})

    assert "거부됨" in result


def test_missing_file_returns_not_found_message(workspace_dir):
    result = file_tools.read_local_file.invoke({"path": "nope.txt"})

    assert "찾을 수 없습니다" in result


def test_rejects_directory_path(workspace_dir):
    (workspace_dir / "subdir").mkdir()

    result = file_tools.read_local_file.invoke({"path": "subdir"})

    assert "파일이 아닙니다" in result
