# セッションログ 014 — Sprint 4 クローズ（第4部・運用）／レトロと全体振り返り

> - **モデルID**: claude-opus-4-8 / **日付**: 2026-07-05 / **effort**: xhigh
> - **ツール構成**: Claude Code CLI（既定/サブスク）+ gh 2.45.0 + `.venv` + uv 0.11.7 + Docker
> - **形式**: 編集版（要点＋採用/棄却の判断理由）

## このセッションの範囲

Sprint 4 を締め、第0〜4部を通した全体レトロを [`docs/retrospective.md`](../retrospective.md) に集約する。

## Sprint 4 の Definition of Done（達成状況）

| 項目 | 成果物 | 状態 |
|------|--------|------|
| example3 取り込み | `todo-app-example3/`（PR#11・秘密除外） | ✅ |
| 追加開発ループ | `Todo.priority` 追加（PR#12） | ✅ |
| 影響調査 | `docs/specs/example3-todo-priority.md` | ✅ |
| データ移行 | Alembic `4d61…`（既存20行 → medium） | ✅ |
| リグレッション確認 | backend 68 passed ＋ CI `example3-backend` ジョブ | ✅ |

## Sprint 4 レトロ

- **Keep**: 影響調査を先に書き**過剰実装を回避**（routers 無変更）。データ移行を**実データ（20行）**で確認。
  CI の別ジョブで**人間製コードのリグレッションを恒久的に**守れた。
- **Problem**: 我々の教材ネット（ruff/mypy/pytest）は example3 を直接見ない（別ジョブで補完）。
  フロントへの `priority` 波及は未。
- **Try**: フロント波及／別機能でもう1ループ／保留 Try の回収（下記 retrospective 参照）。

## 全体（第0〜4部）

5部の骨格が通しで完成。地図・全編レトロ・**AI の失敗カタログ**・数字・今後を
[`docs/retrospective.md`](../retrospective.md) に集約した。
