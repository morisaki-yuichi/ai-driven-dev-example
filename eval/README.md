# eval — 最小 eval ハーネス（第7部）

モデル出力の**質**を、期待特性の**決定的な採点**で測る。コードの tests（実装の正しさ）とは別物。

## 中身

| ファイル | 役割 |
|----------|------|
| [`harness.py`](harness.py) | `Case`（タスク）・`Check`（期待特性）・`run_eval`（採点）。題材は make_slug。 |
| [`prompts.py`](prompts.py) | 失敗実験の主役 A/B。B は「読みやすく」の“改善”で URL 安全性を壊す。 |
| [`solvers.py`](solvers.py) | `recorded_solver`（収録フィクスチャ）／`LiveSolver`（実 API・usage 集計）。 |
| [`pricing.py`](pricing.py) | 現行モデルIDと価格の実測固定（知識の鮮度・Models API で確認）。 |
| [`run.py`](run.py) | ランナー CLI。A/B を採点し回帰を判定。 |
| [`fixtures/`](fixtures/) | 収録済みモデル出力（A=良い・B=回帰）。**live 実行時は API で再生成される**。 |

## 使い方

```bash
python eval/run.py                                  # 収録フィクスチャ（既定・コストゼロ）
python eval/run.py --live --model claude-haiku-4-5  # 実 API（要 anthropic SDK ＋認証・実コスト）
```

`--live` は `pip install anthropic` と認証（`ANTHROPIC_API_KEY` もしくは `ant login`）が要る。
モデルIDは `pricing.PRICING` のキー（`claude-haiku-4-5` / `claude-sonnet-5` / `claude-opus-4-8`）。

## 正直さ

`fixtures/*.jsonl` は各プロンプトの挙動を表す**収録（representative）出力**で、この環境に API が無いため
live では未実行。**採点（スコア）は本物**——収録出力に対して `run_eval` が実際に計算した値。
キーがあれば同じランナーを `--live` で回して実モデル出力に置き換えられる（関連: [実験08](../experiments/08-eval/)）。
