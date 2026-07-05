"""実験06 — hook を検証網に載せる。

決定的なガード（guard.py）とトレース（trace.py）を subprocess で駆動し、
exit code / 追記結果を assert する。「検証網を守る hook」自身を検証網で守る。
guard の作法: exit 2 = ブロック、exit 0 = 許可。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_GUARD = _ROOT / ".claude" / "hooks" / "guard.py"
_TRACE = _ROOT / ".claude" / "hooks" / "trace.py"


def _run_guard(payload: dict[str, object], cwd: Path | None = None) -> int:
    proc = subprocess.run(
        [sys.executable, str(_GUARD)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return proc.returncode


def _bash(command: str) -> dict[str, object]:
    return {"tool_name": "Bash", "tool_input": {"command": command}}


def _write(file_path: str) -> dict[str, object]:
    return {"tool_name": "Write", "tool_input": {"file_path": file_path}}


# --- 秘密ファイル ---------------------------------------------------------


def test_secret_env_blocked() -> None:
    assert _run_guard(_write(".env")) == 2


def test_secret_pem_blocked() -> None:
    assert _run_guard(_write("certs/server.pem")) == 2


def test_env_example_allowed() -> None:
    assert _run_guard(_write(".env.example")) == 0


def test_normal_file_allowed() -> None:
    assert _run_guard(_write("app/todo/core.py")) == 0


# --- rm -rf ---------------------------------------------------------------


def test_rm_rf_home_blocked() -> None:
    assert _run_guard(_bash("rm -rf ~/")) == 2


def test_rm_rf_wildcard_blocked() -> None:
    assert _run_guard(_bash("rm -rf ./*")) == 2


def test_rm_rf_subdir_allowed() -> None:
    assert _run_guard(_bash("rm -rf node_modules")) == 0


def test_rm_f_single_file_allowed() -> None:
    assert _run_guard(_bash("rm -f build.log")) == 0


# --- main 直コミット（一時 git リポジトリで分岐名を制御） -----------------


def _init_repo(path: Path, branch: str) -> None:
    subprocess.run(["git", "init", "-q", "-b", branch, str(path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.email=t@example", "-c", "user.name=t",
         "commit", "-q", "--allow-empty", "-m", "init"],
        check=True,
        capture_output=True,
    )


def test_git_commit_on_main_blocked(tmp_path: Path) -> None:
    _init_repo(tmp_path, "main")
    assert _run_guard(_bash("git commit -m x"), cwd=tmp_path) == 2


def test_git_commit_on_feature_allowed(tmp_path: Path) -> None:
    _init_repo(tmp_path, "feat/x")
    assert _run_guard(_bash("git commit -m x"), cwd=tmp_path) == 0


# --- トレース（JSONL 追記） ----------------------------------------------


def test_trace_appends_jsonl(tmp_path: Path) -> None:
    log = tmp_path / "trace.jsonl"
    env = {**os.environ, "CLAUDE_TRACE_LOG": str(log)}
    payload = {"session_id": "s", "tool_name": "Read", "tool_input": {"file_path": "README.md"}}
    subprocess.run(
        [sys.executable, str(_TRACE)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
        check=True,
    )
    lines = log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["tool_name"] == "Read"
    assert record["file_path"] == "README.md"
    assert record["ts"]
