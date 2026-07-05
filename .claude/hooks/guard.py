#!/usr/bin/env python3
"""PreToolUse ガード hook — 決定的なガードレール（第5部）。

Claude Code の PreToolUse hook として stdin から JSON を受け取り、危険な操作を
「モデルの判断（確率的）」ではなく「機械的な規則（決定的）」でブロックする。

ブロックの作法（Claude Code hooks の規約）: 標準エラーに理由を出し、**exit code 2** で終える。
exit 0 は許可。JSON 解釈不能など想定外は「素通り（allow）」にして本体の作業は止めない
（fail-open。ガードの誤爆で開発を妨げない）。閉じるのは列挙した危険操作だけ。

対象:
- Bash: ``main`` ブランチ上での ``git commit`` / ``git push``（ログ013直後に実際起きた事故）。
- Bash: ``rm -rf`` 系の広域削除（ブラスト半径・実験01）。
- Write/Edit: 秘密ファイル（``.env`` / ``*.pem`` / ``*.key`` / ``credentials`` 等）への書き込み。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from typing import Any

# 秘密ファイルのパターン（``.env.example`` は雛形なので明示的に許可する）。
_SECRET_PATTERNS = (
    re.compile(r"(^|/)\.env(\.|$)"),
    re.compile(r"\.(pem|key|p12|pfx)$"),
    re.compile(r"(^|/)(id_rsa|id_ed25519)$"),
    re.compile(r"(^|/)credentials?(\.|$)"),
    re.compile(r"(^|/)\.?secrets?(\.|/|$)"),
)

# ``git commit`` / ``git push``（途中にオプションが挟まっても拾う）。
_GIT_WRITE = re.compile(r"\bgit\s+(?:-\S+\s+|--\S+\s+)*(commit|push)\b")

# ``rm`` に再帰(-r)かつ強制(-f)が付いているか（-rf / -fr / -r … -f を許容）。
_RF_COMBINED = re.compile(r"-\w*r\w*f\w*|-\w*f\w*r\w*")
_R_FLAG = re.compile(r"(?:^|\s)(?:-r|--recursive)(?:\s|$)")
_F_FLAG = re.compile(r"(?:^|\s)(?:-f|--force)(?:\s|$)")


def current_branch() -> str | None:
    """現在の git ブランチ名。取得できなければ ``None``。"""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def check_secret_write(tool_input: dict[str, Any]) -> str | None:
    """秘密ファイルへの書き込みならブロック理由を返す。"""
    path = str(tool_input.get("file_path", ""))
    if not path:
        return None
    base = path.rsplit("/", 1)[-1]
    if base == ".env.example":
        return None
    for pat in _SECRET_PATTERNS:
        if pat.search(path):
            return f"秘密ファイルへの書き込みを検出: {path}（.env/鍵/認証情報はコミットしない）"
    return None


def _is_dangerous_rm(command: str) -> bool:
    if not re.search(r"\brm\b", command):
        return False
    has_rf = bool(_RF_COMBINED.search(command)) or (
        _R_FLAG.search(command) is not None and _F_FLAG.search(command) is not None
    )
    if not has_rf:
        return False
    # 危険な対象: ルート/ホーム/ワイルドカードなど。特定サブディレクトリの削除は通す。
    return bool(
        re.search(r"(?:^|\s)/(?:\s|$)", command)
        or re.search(r"(?:^|\s)~", command)
        or "$HOME" in command
        or "*" in command
    )


def check_bash(tool_input: dict[str, Any]) -> str | None:
    """危険な Bash コマンドならブロック理由を返す。"""
    command = str(tool_input.get("command", ""))
    if not command:
        return None
    if _GIT_WRITE.search(command) and current_branch() == "main":
        return (
            "main ブランチへの直接 commit/push を検出。"
            "フィーチャーブランチを切ってから（GitHub Flow / ship-change skill）。"
        )
    if _is_dangerous_rm(command):
        return f"広域削除の疑い: {command!r}（rm -rf は檻の中でも人間に確認する）"
    return None


def evaluate(data: dict[str, Any]) -> str | None:
    """hook 入力 JSON からブロック理由を判定（無ければ ``None``）。"""
    tool_name = str(data.get("tool_name", ""))
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    if tool_name == "Bash":
        return check_bash(tool_input)
    if tool_name in ("Write", "Edit", "MultiEdit"):
        return check_secret_write(tool_input)
    return None


def main() -> int:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0  # 解釈不能は素通り（fail-open）
    if not isinstance(data, dict):
        return 0
    reason = evaluate(data)
    if reason:
        print(f"⛔ ガード hook がブロックしました: {reason}", file=sys.stderr)
        return 2  # PreToolUse を拒否（Claude Code の規約: exit 2 ＝ ブロック）
    return 0


if __name__ == "__main__":
    sys.exit(main())
