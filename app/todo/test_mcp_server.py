"""MCP サーバ（app/todo を公開）の受け入れ条件テスト。

- ツールが MCP に登録されていること（list_tools）
- 各ツールがドメインを正しく叩くこと（デコレートされた関数を直接呼ぶ）

call_tool 経由の end-to-end 往復は SDK の戻り値型が緩い（(content, structured) のタプル）ため、
その実出力はセッションログに probe として残し、テストは関数と登録で固定する。
"""

import asyncio

from mcp_server import add_todo, complete_todo, list_todos, mcp


def test_tools_registered() -> None:
    tools = asyncio.run(mcp.list_tools())
    assert {t.name for t in tools} == {"add_todo", "list_todos", "complete_todo"}
    # 説明文が付いていること（レビュー時の手がかり・tool poisoning 実験の下地）
    assert all(t.description for t in tools)


def test_tool_functions_wrap_domain() -> None:
    added = add_todo("牛乳")
    assert added["completed"] is False
    tid = added["id"]
    assert any(t["id"] == tid and t["title"] == "牛乳" for t in list_todos())
    assert complete_todo(tid)["completed"] is True
