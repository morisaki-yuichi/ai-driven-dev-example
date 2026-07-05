"""tool poisoning: 監査が毒入りを検出し、健全な説明文を誤検出しないこと。"""

import asyncio

from audit import audit
from mcp.server.fastmcp import FastMCP
from poisoned_server import poisoned


def _descriptions(server: FastMCP) -> dict[str, str]:
    tools = asyncio.run(server.list_tools())
    return {t.name: (t.description or "") for t in tools}


def test_audit_flags_poisoned_tool() -> None:
    flagged = audit(_descriptions(poisoned))
    assert "list_todos" in flagged
    assert flagged["list_todos"]  # 何らかの注入語がヒット


def test_audit_passes_clean_descriptions() -> None:
    clean = {"add_todo": "TODO を1件追加する。", "list_todos": "TODO を一覧で返す。"}
    assert audit(clean) == {}
