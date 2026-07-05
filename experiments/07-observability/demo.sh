#!/usr/bin/env bash
# 実験07 デモ — トレースを「読む」と、どのステップが遅い/何をしたかを後から再構成できる。
# hook（第5部）→ JSONL → 集計（tools/trace_summary.py）の一本道を、本物の出力で見る。
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="$ROOT/.venv/bin/python"
SUMMARY="$ROOT/tools/trace_summary.py"

echo "########## A) サンプルトレース（再現可能な fixture） ##########"
"$PY" "$SUMMARY" "$ROOT/experiments/07-observability/sample-trace.jsonl"
echo

echo "########## B) 実トレース（このリポジトリの hook 出力・あれば） ##########"
REAL="$ROOT/docs/traces/tool-calls.jsonl"
if [ -f "$REAL" ]; then
  "$PY" "$SUMMARY" "$REAL"
else
  echo "（$REAL が無い。hook を有効にしてツールを使うと貯まる。数値は実行ごとに変わる）"
fi
