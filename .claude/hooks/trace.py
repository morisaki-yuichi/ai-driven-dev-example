#!/usr/bin/env python3
"""PostToolUse トレース hook — 可観測性の入力（第5〜6部）。

全ツール呼び出しを 1 行 1 レコードの JSONL で ``docs/traces/tool-calls.jsonl`` に追記する。
第6部の集計（``tools/trace_summary.py``）がこれを読む。hook は本体を止めないよう、
失敗しても常に exit 0（fail-open）。
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# 既定はリポジトリ内 docs/traces。テスト/デモは CLAUDE_TRACE_LOG で退避先を差し替えられる。
_DEFAULT_LOG = Path(__file__).resolve().parents[2] / "docs" / "traces" / "tool-calls.jsonl"
_LOG = Path(os.environ.get("CLAUDE_TRACE_LOG", str(_DEFAULT_LOG)))


def build_record(data: dict[str, Any]) -> dict[str, Any]:
    ti = data.get("tool_input")
    tool_input: dict[str, Any] = ti if isinstance(ti, dict) else {}
    command = tool_input.get("command")
    return {
        "ts": datetime.now(UTC).isoformat(timespec="seconds"),
        "session_id": data.get("session_id"),
        "tool_name": data.get("tool_name"),
        "file_path": tool_input.get("file_path"),
        "command": str(command)[:200] if command else None,
    }


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    if not isinstance(data, dict):
        return 0
    try:
        _LOG.parent.mkdir(parents=True, exist_ok=True)
        with _LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(build_record(data), ensure_ascii=False) + "\n")
    except OSError:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
