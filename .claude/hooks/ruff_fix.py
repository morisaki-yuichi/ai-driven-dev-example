#!/usr/bin/env python3
"""PostToolUse 自動整形 hook — 検証網の自動化（第5部）。

Edit/Write された Python ファイルに ``ruff check --fix`` を当てる。整形は本体を止めないよう
常に exit 0（fail-open）。ruff が無い/対象外（非 .py）なら黙って通す。jq 等の外部依存を
避けるため、パス抽出も Python 側で行う。
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

_RUFF = Path(__file__).resolve().parents[2] / ".venv" / "bin" / "ruff"


def target_path(data: dict[str, Any]) -> str:
    ti = data.get("tool_input")
    return str(ti.get("file_path", "")) if isinstance(ti, dict) else ""


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    if not isinstance(data, dict):
        return 0
    path = target_path(data)
    if not path.endswith(".py") or not _RUFF.exists():
        return 0
    try:
        subprocess.run([str(_RUFF), "check", "--fix", path], capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
