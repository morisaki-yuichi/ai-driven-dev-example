#!/usr/bin/env bash
# 実験08 デモ — プロンプト A/B を eval で採点し、"改善"のつもりの回帰を検出する（第7部）。
# 既定は収録フィクスチャ（コストゼロ・再現可能）。API があれば `python eval/run.py --live` で実モデル。
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
"$ROOT/.venv/bin/python" "$ROOT/eval/run.py"
