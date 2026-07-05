# セッションログ 006 — Sprint 2（第2部）／仕様駆動で TODO ドメインコア

> - **モデルID**: claude-opus-4-8 / **日付**: 2026-07-05 / **effort**: xhigh
> - **ツール構成**: Claude Code CLI（既定/サブスク）+ gh 2.45.0 + `.venv`（ruff/mypy/pytest）
> - **形式**: 編集版（要点＋採用/棄却の判断理由）

## このセッションの範囲

仕様駆動の実演。**受け入れ条件 → テスト（赤）→ 実装（緑）** で TODO ドメインコアを作り、
受け入れ条件を検証網に接続する（Sprint 1 Try② の回収）。スライスは「ドメインコア（純ロジック）」を選択。

## やったこと

- [`docs/specs/todo-core.md`](../specs/todo-core.md) — US ＋ 受け入れ条件 AC1–AC4。
- [`app/todo/test_core.py`](../../app/todo/test_core.py) — 各 AC を1テストに。
- [`app/todo/core.py`](../../app/todo/core.py) — 実装（`Todo` dataclass ＋ `TodoList`: add/list/complete、メモリ内）。
- 検証網に `app/` を接続: pytest `testpaths` に `app`、CI と CLAUDE.md の mypy を `app experiments` に拡張。

## 赤 → 緑（本物の出力）

- **実装前** `pytest`: `ModuleNotFoundError: No module named 'core'`（collection error / exit 2）＝**赤**。
- **実装後**: `ruff --fix` OK ／ `mypy app experiments` Success(4 files) ／ `pytest` **7 passed** ＝**緑**。

## 受け入れ条件 ↔ テスト対応

| AC | テスト |
|----|--------|
| AC1 追加・連番 id | `test_add_creates_incomplete_todo_with_sequential_id` |
| AC2 trim・空拒否 | `test_add_trims_and_rejects_empty_title` |
| AC3 追加順一覧 | `test_list_returns_in_insertion_order` |
| AC4 完了・不明idはKeyError | `test_complete_marks_done_and_unknown_id_raises` |

## 判断（採用/棄却）

| 判断点 | 採用 | 理由 | 棄却 |
|--------|------|------|------|
| 最初のスライス | ドメインコア（純ロジック） | Web 依存ゼロで「仕様駆動」に集中、既存 pytest 網に即接続 | API 先行（FastAPI 依存追加）、両方（分量） |
| 進め方 | 受け入れ条件 → テスト（赤）→ 実装（緑） | 合否をテストで判定＝非決定性への対処。赤を必ず観察 | 実装先行（形骸テストになりやすい） |
| 配置 | `app/todo/` | AI 駆動リビルド本体は `app/`。example3 は後で参照用に取り込み | — |

## 未処理 → Sprint 2 の残り

- **コンテキストの寿命管理**（圧縮実験）。
- 後続スライス: 永続化 / FastAPI API 層（別スプリント候補）。

## レトロ（速報）

- **Keep**: 赤 → 緑を実行で見せ、AC ↔ テストの対応を明示。検証網が `app` に広がった。
- **Try**: 「テストも書いて」で実装に合わせた**形骸テスト**が出る失敗（第2部の別実験候補）を次に。
