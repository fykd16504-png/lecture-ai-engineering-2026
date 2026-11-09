from pathlib import Path

import pytest
from pydantic_ai.models.test import TestModel

from app.agent import agent, run_with_approval


@pytest.mark.parametrize("reply,expected_files", [("y", 1), ("yes", 1), ("n", 0), ("", 0)])
def test_learning_log_waits_for_approval(tmp_path, monkeypatch, reply, expected_files):
    monkeypatch.chdir(tmp_path)
    confirmations = []

    def confirm(prompt):
        # 承認前には保存先フォルダも作られていない。
        assert not Path("learning_log").exists()
        confirmations.append(prompt)
        return reply

    monkeypatch.setattr("builtins.input", confirm)
    model = TestModel(call_tools=["save_learning_log"], custom_output_text="完了")
    result = run_with_approval(agent, "学習記録を保存して", model)
    assert result.output == "完了"
    assert len(confirmations) == 1
    files = list(Path("learning_log").glob("*.md"))
    assert len(files) == expected_files
    if files:
        content = files[0].read_text(encoding="utf-8")
        assert "# 学習記録" in content
        assert "## トピック" in content
        assert "## 振り返り" in content
