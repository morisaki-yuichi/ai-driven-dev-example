# セッションログ 007 — Sprint 2 クローズ（第2部・文脈と仕様）／寿命管理とレトロ

> - **モデルID**: claude-opus-4-8 / **日付**: 2026-07-05 / **effort**: xhigh
> - **ツール構成**: Claude Code CLI（既定/サブスク）+ gh 2.45.0 + `.venv`（ruff/mypy/pytest）
> - **形式**: 編集版（要点＋採用/棄却の判断理由）

## このセッションの範囲

Sprint 2 の締め＝**コンテキストの寿命管理**。概念03 ＋ 実験03（記憶の外部化）で第2部を閉じる。

## やったこと

- [`docs/concepts/03-context-lifetime.md`](../concepts/03-context-lifetime.md) — 4層記憶モデル／決定はファイルへ／圧縮の扱い。
- [実験03](../../experiments/03-context-compaction/) — 序盤（session 000）の決定が今もファイルから
  取り出せることを `grep` で確認（本物の出力）。会話側のドリフトは既知挙動として提示。

## Sprint 2 の Definition of Done（達成状況）

| 項目 | 成果物 | 状態 |
|------|--------|------|
| 常時文脈（CLAUDE.md） | `CLAUDE.md` v1 | ✅ |
| 仕様駆動（受け入れ条件つき） | `docs/specs/todo-core.md` + `app/todo/`（赤→緑・7 tests） | ✅ |
| レビュー技術／失敗カタログ | `concepts/02` §3 ＋ 各実験 | ✅ |
| コンテキスト寿命管理 | `concepts/03` ＋ 実験03 | ✅ |
| 概念解説 | `concepts/02`・`03` | ✅ |
| わざと失敗の実験 | 実験02（規約無視）・実験03（圧縮／外部化） | ✅ |

## Sprint 2 レトロ（全体）

- **Keep**: 土台の上に「流儀（CLAUDE.md）」「意図（受け入れ条件）」を載せられた。
  仕様駆動の赤→緑を実行で実演。決定の外部化を**実データ**で裏づけた。
- **Problem**: 圧縮ドリフトの「失敗側」は確実再現できず再構成に留まる（正直に明記）。
  `app` はドメインのみで、永続化／HTTP は未。
- **Try（→ Sprint 3・第3部 拡張）**
  1. **MCP 自作サーバ**＝todo API を題材に（`app/todo` を MCP 経由で叩く）。
  2. **skills 化**（運用ルールを skill に）。
  3. **sub-agents** の委譲・並列・コスト比較。
  - 別 Try（保留）: 「テストも書いて」の形骸テスト実験、DevContainer 実ビルド確認の付録化。

## 次スプリントの入口（Sprint 3・第3部 拡張）

MCP / skills / sub-agents。今作った `app/todo` が MCP サーバの格好の題材になる。
「必要時読込」の記憶層（skills）と、外部ツール接続（MCP）、委譲（sub-agents）へ。
