# セッションログ 008 — Sprint 3（第3部・拡張）／自作 MCP サーバ（todo）

> - **モデルID**: claude-opus-4-8 / **日付**: 2026-07-05 / **effort**: xhigh
> - **ツール構成**: Claude Code CLI（既定/サブスク）+ gh 2.45.0 + `.venv`（ruff/mypy/pytest）+ mcp 1.28.1
> - **形式**: 編集版（要点＋採用/棄却の判断理由）

## このセッションの範囲

第3部の第一歩＝**MCP**。`app/todo` のドメインコアを MCP ツールとして公開する自作サーバを作り、検証網に接続する。

## 「知識の鮮度」の実践（記憶で書かず実測）

MCP SDK は変化が速いので、実装前に実測で API を確認した:

- **バージョン**: `mcp 1.28.1`（`importlib.metadata.version`）
- **API**: `FastMCP` に `@tool` デコレータ、`call_tool`/`list_tools` は async、`run(transport="stdio")`（introspection）
- **`call_tool` の戻り値**: `(content_blocks, structured_result)` の**タプル**（probe で確認）

## やったこと

- [`app/todo/mcp_server.py`](../../app/todo/mcp_server.py) — `FastMCP("todo")` に `add_todo`/`list_todos`/`complete_todo` を登録。ドメイン（`core.TodoList`）を叩く。
- [`app/todo/test_mcp_server.py`](../../app/todo/test_mcp_server.py) — 登録確認（`list_tools`）＋各ツール関数の挙動。
- `requirements.txt`（実行時依存 `mcp`）を追加し、CI / DevContainer / CLAUDE.md に接続。
- [`.mcp.json`](../../.mcp.json) で todo サーバを Claude Code に登録。

## end-to-end の実出力（probe）

```text
list_tools() -> ['add_todo', 'list_todos', 'complete_todo']
call add_todo({"title":"牛乳"})
  -> ([TextContent(text='{"id":1,"title":"牛乳","completed":false}')], {"id":1,"title":"牛乳","completed":false})
call list_todos({})
  -> (..., {"result":[{"id":1,"title":"牛乳","completed":false}]})
```

→ `list_tools` は3ツールを返し、`call_tool` は content＋structured のタプルを返す。

## 検証結果

`ruff` / `mypy app experiments`（6 files）/ `pytest`（**9 passed**）すべて緑。

## 判断（採用/棄却）

| 判断点 | 採用 | 理由 | 棄却 |
|--------|------|------|------|
| SDK API の確定 | introspection ＋ probe で実測 | 知識の鮮度。記憶の API は古い恐れ | 記憶で実装（幻覚 API の温床） |
| テストの粒度 | 登録（`list_tools`）＋関数直呼び | `call_tool` の戻り値型が緩く mypy strict と相性が悪い。end-to-end は probe をログに残す | `call_tool` 往復を全部テスト化（型で消耗、`# type: ignore` 乱発） |
| 配置 | `app/todo/mcp_server.py`（core と同居） | スクリプト直実行で sys.path が通り import が素直 | 別パッケージ（import 設定が煩雑） |

## 未処理 → Sprint 3 の残り

- **tool poisoning 実験**（ツールの説明文/戻り値に指示を混入 → 従いかけるか観察・防御側教材）。
- **skills 化**（運用ルールを skill に）。
- **sub-agents**（委譲・並列・コスト比較）。

## レトロ（速報）

- **Keep**: 「記憶で書かず実測」を実演。`app/todo` が MCP の題材として機能。
- **Try**: tool poisoning は防御教材。実害なく安全に観察できる設計にする。
