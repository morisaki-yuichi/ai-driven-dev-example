# docs/traces — hook のトレース出力

`.claude/hooks/trace.py`（PostToolUse hook）が、ツール呼び出しを 1 行 1 レコードの JSONL で
`tool-calls.jsonl` に追記する場所。**第6部（可観測性）の入力**になる。

- `tool-calls.jsonl` は**実行時の生成物**なので `.gitignore` 済み（この README だけ追跡する）。
- 1 レコードの形（例）:

  ```json
  {"ts": "2026-07-05T12:22:34+00:00", "session_id": "demo", "tool_name": "Read", "file_path": "README.md", "command": null}
  ```

- 退避先はテスト/デモ用に `CLAUDE_TRACE_LOG` 環境変数で差し替えられる
  （[`experiments/06-hooks/test_hooks.py`](../../experiments/06-hooks/test_hooks.py) で使用）。
