"""app/todo のドメインコアを MCP ツールとして公開するサーバ（自作 MCP サーバの題材）。

起動: python app/todo/mcp_server.py  （stdio トランスポート）
スクリプトを直接実行すると、その置き場所(app/todo)が sys.path に載るため
`from core import TodoList` が解決される。

SDK: mcp 1.28.1（バージョンは実測。API は knowledge-freshness の原則で introspection 確認）。
"""

from __future__ import annotations

from typing import Any

from core import TodoList
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("todo")
_store = TodoList()


@mcp.tool(description="TODO を1件追加し、作成された TODO を返す。")
def add_todo(title: str) -> dict[str, Any]:
    todo = _store.add(title)
    return {"id": todo.id, "title": todo.title, "completed": todo.completed}


@mcp.tool(description="登録済みの TODO を追加順に一覧で返す。")
def list_todos() -> list[dict[str, Any]]:
    return [{"id": t.id, "title": t.title, "completed": t.completed} for t in _store.list()]


@mcp.tool(description="指定した id の TODO を完了状態にして返す。")
def complete_todo(todo_id: int) -> dict[str, Any]:
    todo = _store.complete(todo_id)
    return {"id": todo.id, "title": todo.title, "completed": todo.completed}


if __name__ == "__main__":
    mcp.run(transport="stdio")
