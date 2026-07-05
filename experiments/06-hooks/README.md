# 実験06 — hook は確率でなく機械で止める（決定的ガードレール）

> 第5部の実験。形式は **予想 → 観察（本物の出力）→ 検出網(=hook)**。
> 記録日 2026-07-05 / claude-opus-4-8 / 実行環境 bash + `.venv`(Python 3.12)。
> 関連: [`concepts/06`](../../docs/concepts/06-hooks.md) / [`session-logs/015`](../../docs/session-logs/015-sprint5-hooks.md)。

## ねらい

CLAUDE.md や skill で「main に直コミットするな」「秘密を書くな」と**指示**しても、それは
モデルへのお願い＝**確率的**で、疲れた文脈・長い会話・圧縮のあとで破られる。実際、
[`session-logs/013`](../../docs/session-logs/013-sprint4-priority.md) の直後に**main への直コミット事故**が起きた。
そこで保証を**ハーネス側の hook（決定的）**へ移す。予想 → 本物の出力 → 「検出網＝hook」で確かめる。

## 予想

- 指示だけ（hook 無し）なら、main 直コミット/秘密書き込み/検証忘れは**すり抜けうる**（現に起きた）。
- PreToolUse hook を置けば、危険操作は**モデルの気分に関係なく** exit 2 で機械的に止まる。
- ただし機械的な規則は**取りこぼしと誤爆**の綱引き。文字列一致は「言及しただけ」でも過剰反応する。

## セットアップ

- 実装は [`.claude/hooks/`](../../.claude/hooks/)（`guard.py` / `trace.py` / `ruff_fix.py`）＋
  [`.claude/settings.json`](../../.claude/settings.json) の配線。
- 再現: `bash experiments/06-hooks/demo.sh`（payload はスクリプト内に閉じ込めてある — 下記「正直さ」）。
- ブロックの作法（Claude Code hooks の規約）: 標準エラーに理由、**exit 2 でブロック**、exit 0 で許可。

## 観察（本物の出力・`bash experiments/06-hooks/demo.sh`）

```console
########## PreToolUse ガード（exit 2 = ブロック / 0 = 許可） ##########
--- 1) 秘密ファイル .env への書き込み ---
⛔ ガード hook がブロックしました: 秘密ファイルへの書き込みを検出: .env（.env/鍵/認証情報はコミットしない）
→ exit=2（期待: 2=block）

--- 2) 雛形 .env.example への書き込み ---
→ exit=0（期待: 0=allow）

--- 3) 広域削除 rm -rf ~/ ---
⛔ ガード hook がブロックしました: 広域削除の疑い: 'rm -rf ~/'（rm -rf は檻の中でも人間に確認する）
→ exit=2（期待: 2=block）

--- 4) 特定サブディレクトリ削除 rm -rf node_modules ---
→ exit=0（期待: 0=allow）

--- 5) main ブランチでの git commit（一時リポジトリで評価） ---
⛔ ガード hook がブロックしました: main ブランチへの直接 commit/push を検出。フィーチャーブランチを切ってから（GitHub Flow / ship-change skill）。
→ exit=2（期待: 2=block, branch=main）

--- 6) フィーチャーブランチ feat/x での同じ git commit ---
→ exit=0（期待: 0=allow, branch=feat/x）

########## PostToolUse トレース（第6部の入力） ##########
--- 追記された JSONL（1行1ツール呼び出し） ---
{"ts": "2026-07-05T12:22:34+00:00", "session_id": "demo", "tool_name": "Read", "file_path": "README.md", "command": null}
{"ts": "2026-07-05T12:22:34+00:00", "session_id": "demo", "tool_name": "Bash", "file_path": null, "command": "pytest -q"}

########## PostToolUse 自動整形（ruff --fix） ##########
--- 整形前（import 未整列） ---
import sys
import os
print(os.getcwd(), sys.argv)
--- ruff_fix hook 通過後 ---
import os
import sys

print(os.getcwd(), sys.argv)
```

同じ「git commit」でも、**ブランチ名という機械的事実**だけで 5)=block / 6)=allow に分かれた点が肝。
モデルは一切判断していない。

## 生きた観察 — hook は「私（AI）自身」も縛った

この実験の最初、payload をインラインの Bash で流そうとした瞬間、**その Bash コマンド自身**が
PreToolUse ガードに評価され、コマンド文字列に含まれる `rm -rf ~/` に反応してブロックされた（実録）:

```text
PreToolUse:Bash hook error: [.venv/bin/python .claude/hooks/guard.py]:
⛔ ガード hook がブロックしました: 広域削除の疑い: '…rm -rf ~/…'（rm -rf は檻の中でも人間に確認する）
```

- **良い面**: hook が本物に生きていて、書いた本人（AI）も例外なく止めた＝決定的ガードの証明。
- **悪い面（誤爆）**: 実際には `rm` を**実行していない**。payload に文字列として**書いただけ**で反応した
  （文字列一致の過剰反応）。だから以降のデモは payload を**スクリプトの中に閉じ込め**、
  ハーネスが見るコマンドを `bash demo.sh` だけにした（実験01と同じ作法）。

## 検出網（＝hook 自身を検証網に載せる）

保証の要である hook を「動いてるはず」で終わらせない。[`test_hooks.py`](test_hooks.py) が guard/trace を
subprocess で駆動し exit code と追記を assert する（`pytest -q` の一部・mypy strict も通過）。

```console
$ .venv/bin/pytest -q
......................                                                   [100%]
22 passed in 0.92s
```

## 結論（設計指針）

1. **確率（指示）で守れないものは、決定（hook）で守る**。「main に直コミットしない」は CLAUDE.md では
   お願い、PreToolUse では**通らない経路**になる。保証したい不変条件はハーネス側へ落とす。
2. **決定的ゆえに誤爆する**。文字列一致は「言及しただけ」でも反応する。ガードは
   **取りこぼし（false negative）より誤爆（false positive）側に倒す**のが安全側だが、
   誤爆で開発を止めすぎない設計（fail-open・対象の限定）が要る。
3. **真の封じ込めは檻（第1部）**。guard の `rm -rf` 判定は保守的なヒューリスティックにすぎない。
   最終防壁は DevContainer による隔離（[実験01](../01-blast-radius/)）で、hook はその手前の**決定的な足場**。

## 正直さについて

- 観察はすべて `demo.sh` の**実行時の生出力**（`ts` は実行時刻）。ruff の整形結果もその場の実物。
- 5)/6) の main 判定は**使い捨ての一時 git リポジトリ**でブランチ名を制御して見せた
  （本物の `main` を汚さない）。guard は cwd の `git rev-parse` で分岐名を読む。
- 「生きた観察」のブロックは、実験を準備している最中に**偶発的に**起きた本物のイベントを採録した。
- hook のセッション中の反映（即時に効くか、`/hooks`・再起動が要るか）は環境差がある。
  本環境では**即時に有効**だった（上記のとおり自分の操作が止まった）。設定スキーマは
  `update-config` skill / 公式ドキュメントで確認した（知識の鮮度）。
