# セッションログ 012 — Sprint 4（第4部・運用）／example3 取り込みとベースライン

> - **モデルID**: claude-opus-4-8 / **日付**: 2026-07-05 / **effort**: xhigh
> - **ツール構成**: Claude Code CLI（既定/サブスク）+ gh 2.45.0 + `.venv`（ruff/mypy/pytest）+ uv 0.11.7 + Docker
> - **形式**: 編集版（要点＋採用/棄却の判断理由）

## このセッションの範囲

第4部の入口＝人間製の完成コードベース（todo-app-example3）を取り込み、
追加開発のための**リグレッション・ベースライン**を確立する。

## やったこと

- example3 を `todo-app-example3/` にコピー取り込み（`rsync`）。
  除外: `.git` / `.env`（秘密）/ `node_modules` / `.venv` / 各種キャッシュ / `dist` / `settings.local.json`。
- 我々の CI を緑に保つため **ruff の対象から `todo-app-example3` を除外**
  （mypy/pytest は `app experiments` 限定で元から対象外）。
- ベースライン確認: example3 backend テストを `uv run pytest` で実行。

## 環境（実測）

- Docker 29.6.1 / Compose v5.2.0。example3 用 postgres が稼働中
  （`todo-app-example3-db-1`, localhost:5433, `config` の既定と一致）。
- `uv` 0.11.7。`config` は `../.env` 不在時に既定値（localhost:5433, todo/todo_dev_password/todo）を使う。

## 検証結果（本物）

- 我々の検証網: ruff / mypy(gate) / pytest すべて緑（**11 passed**、example3 は除外）。
- example3 backend ベースライン: **63 passed**（＝リグレッションの基準線）。

## 判断（採用/棄却）

| 判断点 | 採用 | 理由 | 棄却 |
|--------|------|------|------|
| 取り込み方 | サブディレクトリにコピー | 000-setup の合意。追加開発・CI・AI 操作が素直 | サブモジュール（煩雑）、参照のみ（追加開発不可） |
| 秘密の扱い | `.env` を除外し `.env.example` のみ | 公開リポジトリに秘密を出さない | `.env` ごとコピー（漏洩） |
| CI 衝突回避 | example3 を ruff 除外／nested `.github` は非実行 | 二重ツールチェーンを混ぜない。GitHub は root の workflow のみ実行 | 我々の CI に example3 を混ぜる（緑が崩れる） |

## 未処理 → 次（追加開発の自律ループ）

- `Todo` に新規 `priority` を追加: **影響調査 → Alembic 移行（データ移行）→ 実装 →
  63 tests 緑（リグレッション）＋新テスト → 検収**。

## レトロ（速報）

- **Keep**: 秘密を除外して安全に取り込み、ベースライン **63緑**を実データで確立。
- **Try**: 追加開発では「**影響調査を先に書き出してから実装**」を徹底（AI の過剰実装を防ぐ）。
