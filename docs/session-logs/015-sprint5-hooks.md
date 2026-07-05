# セッションログ 015 — Sprint 5（第5部・hooks）／決定的な足場を組む

> - **モデルID**: claude-opus-4-8 / **日付**: 2026-07-05 / **effort**: xhigh
> - **ツール構成**: Claude Code CLI（既定/サブスク）+ gh 2.45.0 + `.venv`（ruff/mypy/pytest）+ git
> - **形式**: 編集版（要点＋採用/棄却の判断理由）

## このセッションの範囲

[`docs/roadmap-v2.md`](../roadmap-v2.md) 第5部。「skill/CLAUDE.md（確率的）→ hook（決定的）」を実装し、
保証をハーネス側へ移す。生きた素材は [`013`](013-sprint4-priority.md) 直後に起きた **main 直コミット事故**。

## 着手前に確定したこと（知識の鮮度）

- hooks の正確な設定スキーマ・ブロックの作法（**exit 2 = block**）・セッション反映挙動を
  `update-config` skill で確認してから実装（推測で書かない）。
- ブロック実演は「本物の出力」を要件にする（DoD）。

## 成果物（DoD 達成状況）

| 項目 | 成果物 | 状態 |
|------|--------|------|
| hook 群 | [`.claude/hooks/`](../../.claude/hooks/) guard / trace / ruff_fix ＋ [`settings.json`](../../.claude/settings.json) 配線 | ✅ |
| ブロック実演（本物） | [`experiments/06-hooks/`](../../experiments/06-hooks/) 予想→観察→検出網 | ✅ |
| 概念06 | [`docs/concepts/06-hooks.md`](../concepts/06-hooks.md) | ✅ |
| セッションログ | 本ファイル | ✅ |
| 検証網に載せる | [`test_hooks.py`](../../experiments/06-hooks/test_hooks.py)（pytest 22 passed / mypy strict 緑） | ✅ |

## hook の配線（settings.json）

- **PreToolUse**(Bash|Write|Edit) → `guard.py`：main 直コミット/push・秘密書き込み・広域 `rm -rf` を exit 2。
- **PostToolUse**(Edit|Write) → `ruff_fix.py`：`ruff --fix` で自動整形（検証網の自動化）。
- **PostToolUse**(全ツール, async) → `trace.py`：1行1呼び出しの JSONL（第6部の入力）。
- **Stop** → `pytest -q`：赤なら停止をブロック（検証の取りこぼし防止）。

## 実行結果（本物）

- デモ6ケースが期待どおり block/allow に分岐（`.env`=block, `.env.example`=allow, `rm -rf ~/`=block,
  `rm -rf node_modules`=allow, main の commit=block, feat/x の commit=allow）。同じ commit がブランチ名だけで割れた。
- **hook が私（AI）自身も縛った**：準備中、payload をインラインで打った Bash が、文字列 `rm -rf ~/` に
  反応して**実行前にブロック**された（実録）。決定的ガードの証明であり、同時に**文字列一致の誤爆**の実例。
- 検証網: `ruff check .` / `mypy app experiments`（10 files）/ `pytest -q`（22 passed）すべて緑。
  hook スクリプト3本も `mypy --strict` 単体で緑。

## 判断（採用/棄却）

| 判断点 | 採用 | 理由 | 棄却 |
|--------|------|------|------|
| ブロック手段 | **exit 2 + stderr** | Claude Code hooks の規約・最も再現性が高く実演しやすい | JSON `permissionDecision`（新しめだが実演が重い） |
| hook 実装言語 | Python（`.venv`） | リポジトリ標準・型検査/テスト可能・jq 等の隠れ依存を避ける | jq インライン（依存が増え検証しづらい） |
| ブロック実演 | payload を**ファイル**に閉じ込め `bash demo.sh` | インラインだと外側 Bash 自身がガードに評価され二重発火 | インラインで payload を流す（誤爆で実演不能） |
| main 判定の再現 | 使い捨て一時 git リポジトリ | 本物の `main` を汚さずブランチ名を制御 | 実 `main` に切替えて試す（危険・副作用） |
| 誤爆方針 | 安全側（誤爆＞取りこぼし）＋ fail-open | ガードは閉じ、想定外入力は素通りで開発を止めない | 何でも厳格にブロック（作業が止まる） |
| ガード自身 | `test_hooks.py` で検証網に載せる | 「守る hook」を「動くはず」で終わらせない | 手動確認のみ（回帰で静かに壊れる） |
| Stop の pytest | 赤のときだけ exit 2 | 緑なら無害・取りこぼしだけ止める | 常時ブロック（緑でも停止を妨げる） |

## 検収観点

- 同じ操作がブランチ名という**機械的事実**だけで block/allow に割れているか（モデル判断の排除）。
- 誤爆と fail-open の綱引きが設計に現れているか（対象の限定・解釈不能は素通り）。
- hook が**決定的な足場**であって最終防壁ではない位置づけ（真の封じ込め＝檻）が言語化されているか。

## レトロ（速報）

- **Keep**: スキーマを skill で先に確定（知識の鮮度）。**偶発的な自己ブロック**を隠さず教材化できた
  （決定的ガードの証明＋誤爆の実例が同時に手に入った）。守る側の hook を検証網に載せた。
- **Problem**: guard の文字列一致は誤爆する（言及=実行と誤認）。`rm` 判定は保守的ヒューリスティック止まり。
  hook スクリプトは CI の mypy ゲート（`app experiments`）の外（今は手動 strict で担保）。
- **Try**: 第6部で `trace.py` の JSONL を集計（`tools/trace_summary.py`）し可観測性へ。
  余力で hook ゲートを CI に接続 / `PreCompact` で圧縮前に決定を退避。
