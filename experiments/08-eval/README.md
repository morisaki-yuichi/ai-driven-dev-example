# 実験08 — “改善”が実は悪化（vibes を eval で捕まえる）

> 第7部の実験。形式は **予想 → 観察（本物のスコア）→ 検出網(=eval)**。
> 記録日 2026-07-05 / claude-opus-4-8 / 実行環境 bash + `.venv`(Python 3.12)。
> 関連: [`concepts/08`](../../docs/concepts/08-eval.md) / [`session-logs/017`](../../docs/session-logs/017-sprint7-eval.md) / ハーネス [`eval/`](../../eval/)。

## ねらい

プロンプトを「良くした」つもりが、**実は質を落とす**ことがある。見た目（vibes）は良く見えるので気づけない。
コードの tests は「実装の正しさ」しか測れない。モデル出力の**質**を測る網＝eval が要る。
題材は make_slug（タイトル → URL スラッグ）。期待特性を**決定的に採点**し、回帰を検出できるか確かめる。

## 予想

- プロンプト B は「読みやすく・固有名詞の大文字やアクセントを残す」と**改善したつもり**。
  出力（`Hello-World`, `Café-München-Delights`）は人間には**きれいに見える**。
- だが URL スラッグとしては**壊れている**（大文字・非ASCII＝リンクが割れる）。
- vibes では見逃す。eval（小文字・URL安全・キーワード保持を採点）は**スコア低下として検出**するはず。

## セットアップ

- ハーネス: [`eval/`](../../eval/)（`harness` 採点 / `prompts` A・B / `solvers` / `run.py`）。
- 再現: `bash experiments/08-eval/demo.sh`（＝`python eval/run.py`）。既定は**収録フィクスチャ**。
- 採点特性: `lowercase` / `url_safe`([a-z0-9-]) / `hyphen_separated` / `no_edge_hyphen` /
  `no_double_hyphen` / `keeps_keywords`（小文字キーワードが残るか） / `nonempty`。

## 観察（本物のスコア・`python eval/run.py`）

```console
========================================================================
[prompt_A (recorded)] 総合スコア 1.000
    OK  greeting  1.00  'hello-world'
    OK  tips      1.00  '10-tips-for-better-sleep'
    OK  accents   1.00  'cafe-munchen-delights'
    OK  spaces    1.00  'spaces-everywhere'
    OK  version   1.00  'python-3-12-you'
    OK  fox       1.00  'the-quick-brown-fox'
------------------------------------------------------------------------
[prompt_B (recorded)] 総合スコア 0.571
    NG  greeting  0.57  'Hello-World'  失敗: lowercase, url_safe, keeps_keywords
    NG  tips      0.57  '10-Tips-for-Better-Sleep'  失敗: lowercase, url_safe, keeps_keywords
    NG  accents   0.57  'Café-München-Delights'  失敗: lowercase, url_safe, keeps_keywords
    NG  spaces    0.57  'Spaces-Everywhere'  失敗: lowercase, url_safe, keeps_keywords
    NG  version   0.57  'Python-3.12-You'  失敗: lowercase, url_safe, keeps_keywords
    NG  fox       0.57  'The-Quick-Brown-Fox'  失敗: lowercase, url_safe, keeps_keywords
    落ちた特性: lowercase×6, url_safe×6, keeps_keywords×6
========================================================================
⛔ 回帰を検出: B は A より 0.429 悪化（A=1.000 → B=0.571）。vibes では気づかない。
  （収録フィクスチャの採点。実コストは発生しない。live は --live）
```

見た目は「B の方が読みやすい」。だが eval は **A=1.000 → B=0.571** と**0.429 の悪化**を数字で示した。
落ちた特性まで指す（`url_safe×6` 等）ので、**どこが壊れたか**まで分かる。

## 検出網（＝eval そのもの）

この実験の検出網は eval 自身。守る側を「動くはず」で終わらせないため、
[`eval/test_eval_harness.py`](../../eval/test_eval_harness.py) が採点計算・特性発火・A/B 回帰検出を固定する
（`pytest -q` の一部・mypy strict も通過。ゲートに `eval` を追加）。

```console
$ .venv/bin/pytest -q
..................................                                       [100%]
34 passed in 0.88s
```

## 結論（設計指針）

1. **eval は tests とは別の網**。tests は実装の正しさ、eval はモデル出力の質。プロンプト/ツール/ハーネスの
   変更は tests では守れない——合否を**質**で判定する網が要る。
2. **決定スコアで vibes を置き換える**。「良くなった気がする」を「A=1.000→B=0.571」に変える。
   期待特性をコードにしておけば、改善のたびに機械的に回帰を検出できる（CI に載せれば PR で止められる）。
3. **最小から始める**。LLM-as-judge やモデル階級比較は強力だが採点コスト/バイアスという別テーマ。
   まず決定スコアで土台を作る（将来 Try）。

## 正直さについて

- スコアは**本物**——収録出力に対して `run_eval` が実際に計算した値（A=1.000, B=0.571）。
- モデル出力（`fixtures/*.jsonl`）は各プロンプトの挙動を表す**収録（representative）出力**。
  この環境に API アクセスが無いため live 未実行。キーがあれば同じランナーを
  `python eval/run.py --live --model claude-haiku-4-5` で回し、実モデル出力に置き換えられる
  （その場合 usage からコストも概算する。価格は [`eval/pricing.py`](../../eval/pricing.py) で実測固定）。
- 回帰の構図（大文字/アクセント保持で URL 安全性が壊れる）は決定的で、モデルや実行に依らず再現する。
