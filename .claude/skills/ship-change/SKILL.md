---
name: ship-change
description: このリポジトリで変更を出荷する標準手順。フィーチャーブランチ作成 → 検証網 → 1コミット=1意味 → PR → CI緑 → マージ → main確認。コードやドキュメントを追加・修正して取り込むときに使う。
---

# 変更を出荷する（GitHub Flow ＋ 検証網）

このリポジトリの標準の出荷手順。**`main` へ直接コミットしない。**

## 手順

1. **ブランチ**: `git switch -c <type>/<topic>`（`main` から切る）。
2. **変更**: 実装／ドキュメントを書く。実験なら「予想 → 観察 → 検出網」、
   観察は**実行して本物の出力**を貼る（再構成なら明記）。
3. **検証網（緑を確認）**:
   ```bash
   .venv/bin/ruff check --fix .
   .venv/bin/mypy app experiments tools eval
   .venv/bin/pytest -q
   ```
4. **コミット**: 1コミット=1意味。メッセージは `型: 要約`（`docs`/`feat`/`test`/`ci`/`chore`/`build`、日本語可）。
5. **PR**: `gh pr create --base main --title … --body …`。
6. **CI**: `gh pr checks <n> --watch` で緑を確認。
7. **マージ**: `gh pr merge <n> --merge --delete-branch`（履歴保持のマージコミット）。
8. **main 確認**: マージ後、ローカルで検証網を再実行し、`gh run watch <run-id>` で main の CI 緑も確認。

## 原則

- 合否は**受け入れ条件とテスト**で判定（出力の一致では判定しない）。
- `*_hallucinated.py` は意図的に壊した教材ファイル。ゲート（`mypy app experiments tools eval`）から除外済み。
- 外向き操作（`git push`・マージ・公開）は最小権限では確認対象。**判断を説明してから**行う。
- 決定はセッションログ（`docs/session-logs/NNN-*.md`）に外部化する。
