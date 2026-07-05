# 実験07 — 観測できないものは最適化できない（トレースを読む）

> 第6部の実験。形式は **予想 → 観察（本物の出力）→ 検出網(=可観測性)**。
> 記録日 2026-07-05 / claude-opus-4-8 / 実行環境 bash + `.venv`(Python 3.12)。
> 関連: [`concepts/07`](../../docs/concepts/07-observability.md) / [`session-logs/016`](../../docs/session-logs/016-sprint6-observability.md)。
> 前提: 第5部の [`trace.py`](../../.claude/hooks/trace.py)（PostToolUse hook が JSONL を吐く）。

## ねらい

「セッションが遅かった / 失敗した」——それだけでは**どのステップが**原因か分からない。
第5部の hook が吐いた JSONL を [`tools/trace_summary.py`](../../tools/trace_summary.py) で**読み**、
行動・時間を後から再構成できるかを比較する。hook → JSONL → 集計の**一本道**を本物の出力で見る。

## 予想

- トレースが無ければ、遅さ/失敗は「体感」でしか語れず、**どこを直せばいいか分からない**。
- トレースを集計すれば、ツール別の内訳と**遅かったステップ**が数字で出て、狙いを絞れる。
- ただし「ステップ経過」は純粋なツール単体時間ではない（モデル思考や人間の待ちを含む）。トークン/コストは hook 入力に無い。

## 観察（本物の出力・`bash experiments/07-observability/demo.sh`）

### A) 再現可能な fixture（[`sample-trace.jsonl`](sample-trace.jsonl)）

```console
トレース集計: experiments/07-observability/sample-trace.jsonl
  レコード 8 件（session 1 / 期間 79.9s）
  ツール別:
    Bash    4  ############············   50%
    Edit    2  ######··················   25%
    Read    1  ###·····················   12%
    Write   1  ###·····················   12%
  よく触ったファイル:
      3  app/todo/core.py
      1  app/todo/test_core.py
  遅かったステップ（前ステップからの経過＝ツール＋モデル＋待ち込み・上位5）:
    +  42.5s  #3   Bash  pytest -q
    +  26.3s  #7   Bash  git commit -m done
    +   3.1s  #1   Edit  app/todo/core.py
    +   2.3s  #2   Write  app/todo/test_core.py
    +   2.3s  #6   Bash  mypy app experiments tools
```

**同じ「遅かった」でも、集計は迷わず `#3 pytest -q（+42.5s）`を指す。** どこを速くすべきかが確定する。

### B) 実トレース（このセッションの hook 出力・数値は実行ごとに変わる）

集計器は fixture だけでなく、この教材を作っている**当セッションのトレース**もそのまま読めた（抜粋・実録）:

```console
トレース集計: docs/traces/tool-calls.jsonl
  レコード 26 件（session 1 / 期間 1103.3s）
  ツール別:
    Bash    14  #############···········   54%
    Write    8  #######·················   31%
    Edit     3  ###·····················   12%
    AskUserQuestion   1  #·······················    4%
  遅かったステップ（前ステップからの経過＝ツール＋モデル＋待ち込み・上位5）:
    + 287.0s  #23  Bash  cd … git switch -c fea…
    + 127.0s  #15  AskUserQuestion
    …
```

`#15 AskUserQuestion（+127s）` は、まさに**人間が出荷可否を決めていた時間**。トレースは
「壁時計の時間がどこへ行ったか」を正直に写す（＝モデルだけでなく人間の待ちも含む・下記正直さ）。

## 検出網（＝可観測性そのもの）

トレースと集計こそがこの実験の「検出網」。集計器は保証の一部なので**検証網に載せる**:
[`tools/test_trace_summary.py`](../../tools/test_trace_summary.py) が counts / span / ステップ経過 /
壊れた行 / 旧新スキーマ混在を固定する（`pytest -q` の一部・mypy strict も通過。gate に `tools` を追加）。

## 結論（設計指針）

1. **観測が先、最適化は後**。「遅い」の体感を、集計は `#3 pytest` のような**具体的な標的**に変える。
   一本道（hook → JSONL → 集計）が通っていれば、後からいくらでも再構成できる。
2. **ステップ経過 ≠ ツール単体レイテンシ**。隣接差分はモデル思考・人間の待ちも含む。正確な単体時間は
   Pre/Post のペア計測が要る（Try）。粗くても「どこに時間が寄っているか」は十分見える。
3. **コストは別系統**。トークン/価格は hook 入力に無い。OpenTelemetry の usage メトリクス等が本筋
   （第7部 eval のモデル階級比較で必要になる）。ここでは「取れるもの（行動・時間）」を確実に計上した。

## 正直さについて

- A) の出力は `demo.sh` の**実行時の生出力**で、fixture は固定なので**誰でも再現できる**。
- B) は当セッションの**実トレース**の実録抜粋。件数・秒数は実行ごとに変わる（固定できるのは「読める」構造）。
- 「ステップ経過」は隣接 `ts` の差分。ツール実行・モデル思考・**人間の待ち**（AskUserQuestion 等）を含む。
- トレースは async 追記で**壊れた行が混じりうる**。集計器は行単位で頑健に飛ばし、その数を報告する。
