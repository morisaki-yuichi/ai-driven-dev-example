#!/usr/bin/env bash
# 実験01: ブラスト半径の封じ込め
#
# 「AI が破壊的タスクを暴走させても、被害が『容器』の中で止まる」ことを、
# 使い捨てディレクトリ（＝容器の見立て）で安全に実演する。
# 本スクリプトは mktemp の使い捨て領域だけを対象にし、本物のファイルには一切触れない。
#
# 使い方: bash demo.sh
set -euo pipefail

CONTAINER="$(mktemp -d)"   # AI が作業する「使い捨て容器」
HOST="$(mktemp -d)"        # 容器の外（ホスト＝本物のプロジェクトの見立て）
trap 'rm -rf "$CONTAINER" "$HOST"' EXIT   # 実験後は容器ごと破棄

printf 'print("important work")\n' > "$CONTAINER/app.py"
printf 'do not lose me\n'          > "$CONTAINER/important_data.txt"
printf 'host secret (容器の外)\n'  > "$HOST/host-secret.txt"

echo "=== 破壊前 ==="
echo "[容器の中]      : $(ls -1A "$CONTAINER" | tr '\n' ' ')"
echo "[容器の外/ホスト]: $(ls -1A "$HOST" | tr '\n' ' ')"

echo
echo "=== AI が『後片付けして』を破壊的に解釈して暴走 → 容器の中で rm -rf ./* ==="
( cd "$CONTAINER" && rm -rf ./* )

echo
echo "=== 破壊後 ==="
echo "[容器の中]      : '$(ls -1A "$CONTAINER" | tr '\n' ' ')'  ← 空（全滅）"
echo "[容器の外/ホスト]: $(ls -1A "$HOST" | tr '\n' ' ')  ← 無傷"

echo
echo "被害は容器の中で止まった。容器の外（ホスト＝本物の作業）は無事。"
echo "これがブラスト半径の封じ込め。DevContainer/sandbox はこの『容器の壁』を提供する。"
