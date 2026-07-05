# セッションログ 003 — Sprint 1（第1部・檻と土台）／檻と権限

> - **モデルID**: claude-opus-4-8 / **日付**: 2026-07-05 / **effort**: xhigh
> - **ツール構成**: Claude Code CLI（既定/サブスク）+ gh 2.45.0 + `.venv`（ruff/mypy/pytest）
> - **形式**: 編集版（要点＋採用/棄却の判断理由）

## このセッションの範囲

Sprint 1 の残り＝**檻の設計（DevContainer）と権限設計の文書化**。
（検証網は 002 で完了、GitHub Flow で `main` へマージ済み。）

## やったこと

1. `.devcontainer/devcontainer.json` — Python 3.12 + Node の隔離環境。
   検証網ツールを `postCreate` で導入（＝ブラスト半径を容器内に限定）。
2. `.claude/settings.json` — **最小権限の実演**。安全な検証コマンドのみ `allow`、
   破壊的/外向き操作（`rm`・`git push` 等）は既定のまま確認を要求。
3. `docs/concepts/01-cage-and-permissions.md` — ブラスト半径 / 最小権限 / sandbox の3概念。
4. フィーチャーブランチ `feat/cage-and-permissions` → PR → CI 緑 → マージ。

## 判断（採用/棄却）

| 判断点 | 採用 | 理由 | 棄却 |
|--------|------|------|------|
| DevContainer の作り | image + node feature | 標準・保守が楽・写経者が再現しやすい | 自作 Dockerfile（保守コスト増） |
| 権限の実演範囲 | `allow` リストのみコミット | 追加は安全（自動許可を絞るだけ）。攻めた設定を凍結しない | `deny`/`ask` を本体に記載（構文のバージョン依存で陳腐化・誤ブロックの恐れ） |
| 権限構文の扱い | 公式ドキュメントへ誘導 | 知識の鮮度：構文は変わりうる | 本文に構文を確定記載 |

## 未処理 → Sprint 1 の締めに必要

- **Sprint 1 の「わざと失敗を見る」実験が未実施**（各スプリント1回以上の原則）。
  候補: sandbox 内で境界外への書き込みを試み、檻が被害を止めることを観察（**安全に設計する**）。
- DevContainer の**実ビルド確認**は本セッション環境では未実施（Docker 不使用）。
  写経者/著者の DevContainer 環境で確認する前提。

## レトロ（速報）

- **Keep**: GitHub Flow が板についた（PR→CI→マージ→main 確認）。1コミット=1意味を維持。
- **Try（→ Sprint 1 締め）**: 檻の「実感」は文書だけでは弱い。sandbox 実験で体験に変える。
