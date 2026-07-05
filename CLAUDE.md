# CLAUDE.md

この AI（Claude Code 等）向けのオンボーディング資料。**このリポジトリで作業する前に読むこと。**
人間の新メンバー向け資料と同じ役割を、AI に対して果たす（＝常時文脈）。

## このリポジトリは何か

AI 駆動開発の実践**教材**。姉妹作 todo-app-example2/3 の第3周として、同じ TODO アプリを
AI 駆動で作り直し、人間が書いた場合との差分を比較できるようにする。
統括仕様は [`docs/initial-prompt.md`](docs/initial-prompt.md)。
**私（AI）の役割＝シニアエンジニア兼スクラムマスター**。

## 最優先の原則

1. **なぜそうするかを毎回説明する**（教材なので、判断の言語化が成果物の一部）。
2. **会話を信頼の源泉にしない。決定はファイルへ**（`docs/session-logs/` に外部化）。
3. **AI の出力はそのままでは信頼しない**。検証網と受け入れ条件で必ず受け止める。
4. **知識の鮮度**: バージョン・モデルID・価格を推測で書かない。実測を固定するか公式ドキュメントへ誘導。

## ディレクトリ構成と規約

- `docs/concepts/NN-*.md` — 概念解説。**3点形式**（①一言定義 ②なぜ必要か・事故例 ③このリポジトリでの実例）。
- `docs/session-logs/NNN-*.md` — **編集版**セッションログ。冒頭にモデルID・日付・effort・ツール構成。
  本文は「要点＋採用/棄却の判断理由」。生ログ全文は残さない。
- `experiments/NN-*/` — 「わざと失敗を見る」実験。**予想 → 観察 → 検出網**の3点セット。
  観察は必ず**実行して本物の出力**を貼る。再構成なら明記する。
- `.devcontainer/` — 隔離環境（檻）。`.claude/settings.json` — 最小権限（allow は検証コマンドのみ）。
- **文書は日本語**。見出し・トーンは既存ファイルに合わせる。

## 開発ワークフロー（GitHub Flow）

- `main` から**フィーチャーブランチ**を切る。`main` へ直接コミットしない。
- **1コミット=1意味**。メッセージは `型: 要約`（例 `docs(concept): …` / `test(experiment): …`）。日本語可。
- **PR → CI 緑 → マージ（merge commit で履歴保持）→ マージ後 main で動作確認**。
- コミット前に生成物を校正し、直後に確認する。
- 出荷手順の詳細は skill `ship-change`（`.claude/skills/ship-change/`・必要時読込）に切り出してある。

## 検証網（コマンド）

ローカルは `.venv`。実行時依存は `requirements.txt`、検証網ツールは `requirements-dev.txt` に固定。

```bash
.venv/bin/ruff check .            # lint
.venv/bin/mypy app experiments tools eval   # 型（ゲート。*_hallucinated.py は除外）
.venv/bin/pytest -q               # テスト
```

CI（`.github/workflows/ci.yml`）は **ruff → mypy → pytest**（安い網から）。
`*_hallucinated.py` は**わざと壊した教材ファイル**なのでゲートから除外している（`pyproject.toml`）。

## モデルとコスト

- 著者は Claude Code の**既定構成**（執筆時点 Opus 4.8）。比較の節でのみ上位モデルを使う。
- コード例で API を呼ぶ場合、モデルIDは `claude-opus-4-8` と明記し「Models API で最新を確認」注記を添える。

## やってはいけない / 確認を要する

- `main` への直コミット、破壊的コマンド（`rm -rf` 等）の無確認実行、秘密情報のコミット。
- 外向きの操作（`git push`・公開・外部送信）は**人間に確認**してから。
