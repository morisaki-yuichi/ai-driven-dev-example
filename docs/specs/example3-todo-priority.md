# 仕様・影響調査 — example3 Todo に priority を追加（第4部・追加開発）

> 対象: `todo-app-example3/backend`（人間製の完成コードベース）。
> AI 時代の「**影響調査・データ移行・リグレッション確認**」を再演する。実装前に本書を確定する。

## Issue（ユーザーストーリー）

利用者として、TODO に優先度（low/medium/high）を付け、作成・更新できるようにしたい。

## 受け入れ条件

- **AC1** 作成時に priority を省略したら `"medium"`。
- **AC2** priority に low/medium/high を指定でき、保存・取得できる。
- **AC3** 不正な値（例 `"urgent"`）は 422。
- **AC4** PATCH で priority を変更できる。
- **AC5** 既存の TODO（priority 列が無かった行）は移行後 `"medium"` になる（**データ移行**）。
- **AC6** 既存の 63 テストは緑のまま（**リグレッションなし**）。

## 影響調査（実装前に確定）

| 対象 | 変更 | 理由 |
|------|------|------|
| `app/models.py` | `Todo` に `priority` 列（既定 `"medium"`） | 保存する形 |
| `app/schemas.py` | `TodoCreate`/`TodoUpdate` に `Literal["low","medium","high"]`、`TodoRead` に `priority` | 入り口の検証＋見せる形 |
| `app/routers/todos.py` | **変更なし** | create=`model_validate` / update=`model_dump(exclude_unset)` が汎用で priority を自動で通す |
| `migrations/` | 新規リビジョン: `todos.priority` を追加（`server_default 'medium'`） | 既存行のデータ移行 |
| `tests/` | `test_todos_priority.py` を追加 | AC1-4 の検証 |

### リグレッション見立て

既存テストは応答を**項目単位**で assert（`body["title"]` 等）しており、全体一致の assert は無い。
→ `TodoRead` に `priority` を足しても既存 assert は壊れない見込み（**実行で確認する**）。

### スコープ外（過剰実装を避ける）

- priority による絞り込み／並び替え（`list_todos` のクエリ拡張）は今回やらない。
  まず最小の追加でループを回し、必要になったら別スライスで足す。

## この題材で回すループ

影響調査（本書）→ Alembic 移行 → 実装 → `uv run alembic upgrade head`（データ移行）→
`uv run pytest`（63＋新テスト緑＝リグレッション）→ PR → 検収。
