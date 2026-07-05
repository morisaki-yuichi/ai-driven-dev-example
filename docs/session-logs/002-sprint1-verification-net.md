# セッションログ 002 — Sprint 1（第1部・檻と土台）／git と検証網

> - **モデルID**: claude-opus-4-8
> - **日付**: 2026-07-05
> - **effort**: xhigh
> - **ツール構成**: Claude Code CLI（既定 / サブスク）+ `.venv`（ruff 0.15.20 / mypy 2.1.0 / pytest 9.1.1）
> - **形式**: 編集版（要点＋採用/棄却の判断理由）

## このセッションの範囲

Sprint 1 のうち **(a) バージョン管理の土台** と **(b) 検証網の最小構成** を敷き、
Sprint 0 の Try（型チェック網の回収）を果たす。
DevContainer と権限設計の文書化は本スプリント内の次セッションに残す。

## やったこと

1. **git 初期化と Sprint 0 成果物の取り込み**（`main` に5コミット、1コミット=1意味）。
   identity は既存 global 設定 `Yuichi Morisaki <m0ris4q1@gmail.com>` を使用。
2. フィーチャーブランチ `feat/verification-net` で検証網を構築（GitHub Flow）。
3. 検証網ツールを `.venv` に固定導入し、`pyproject.toml` / `requirements-dev.txt` /
   CI ワークフロー（`.github/workflows/ci.yml`）を用意。
4. **3層すべてを実行して観察を記録**（下表）。

## 検証網の実行結果（本物の出力）

| 網 | コマンド | 結果 |
|----|----------|------|
| lint | `ruff check .` | All checks passed（exit 0） |
| 型（ゲート） | `mypy experiments` | Success: no issues in 2 files（exit 0） |
| 型（幻覚に直当て） | `mypy .../make_slug_hallucinated.py` | `"str" has no attribute "slugify"` 他1件（exit 1） |
| テスト | `pytest -q` | 3 passed（exit 0） |

→ **Sprint 0 Try 回収**: 型チェック網が、コードを動かす前に幻覚を静的に捕まえた
（3層のうち最速・最安）。実験00 README に実演を追記。

## 判断（採用/棄却）

| 判断点 | 採用 | 理由 | 棄却 |
|--------|------|------|------|
| ツール導入方式 | `.venv` + `requirements-dev.txt` に実測バージョンを固定 | 写経者が同一構成を再現できる。バージョンは推測せず実際に入った値を記録（知識の鮮度対策） | グローバル導入（隔離・再現性が弱い）、pyproject の dependency-groups（pip 24.0 で扱いにくい） |
| 幻覚ファイルの扱い | 本体ゲートから除外し、mypy 直当てで実演 | 壊れたファイルで gate が赤になるのを避けつつ、型チェックの効果は見せる | `# type: ignore` 付与（教材の意図＝幻覚が見える、を潰す） |
| CI の網の順序 | ruff → mypy → pytest（安い網から） | 早く落ちるものほど気づくコストが低い。第0部の「早い網ほど安い」を実装で体現 | 並列一括（失敗の切り分けが鈍る） |
| 取り込み単位 | 意味ごとに分割コミット | 「1コミット=1意味」を最初から実演する教材価値 | 一括 initial commit（履歴が読めない） |

## 未処理 → Sprint 1 の残り

- **DevContainer / 最小権限・ブラスト半径の文書化**（＝檻の設計そのもの）。
- **GitHub への公開**: CI（Actions）を実際に走らせるにはリモートが要る。公開は外向きの
  操作なので、リポジトリ名・公開/非公開を人間に確認してから実施する。
- `feat/verification-net` の `main` への取り込み方（ローカル merge か、公開後に PR か）を決める。

## 検収待ち / 次の決定

- 検証網の構成（ruff/mypy/pytest・CI 定義）の妥当性。
- GitHub 公開の可否とリポジトリ名。
