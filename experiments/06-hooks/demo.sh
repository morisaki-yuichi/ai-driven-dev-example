#!/usr/bin/env bash
# 実験06 デモ — hook の決定的ブロック/記録を「本物の出力」で見る。
#
# なぜスクリプト(ファイル)にするか: payload をインラインの Bash で打つと、その Bash 自身が
# PreToolUse ガードに評価され、payload 内の "rm -rf" 等でガードが二重発火する（実際に起きた）。
# ファイルの中に閉じ込めて呼べば、ハーネスが見るのは "bash demo.sh" だけ。実験01と同じ作法。
set -u

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY="$ROOT/.venv/bin/python"
GUARD="$ROOT/.claude/hooks/guard.py"
TRACE="$ROOT/.claude/hooks/trace.py"
RUFF_FIX="$ROOT/.claude/hooks/ruff_fix.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

guard() {  # 期待, payload
  printf '%s\n' "$2" | "$PY" "$GUARD"
  echo "→ exit=$?（期待: $1）"
  echo
}

echo "########## PreToolUse ガード（exit 2 = ブロック / 0 = 許可） ##########"
echo "--- 1) 秘密ファイル .env への書き込み ---"
guard "2=block" '{"tool_name":"Write","tool_input":{"file_path":".env"}}'

echo "--- 2) 雛形 .env.example への書き込み ---"
guard "0=allow" '{"tool_name":"Write","tool_input":{"file_path":".env.example"}}'

echo "--- 3) 広域削除 rm -rf ~/ ---"
guard "2=block" '{"tool_name":"Bash","tool_input":{"command":"rm -rf ~/"}}'

echo "--- 4) 特定サブディレクトリ削除 rm -rf node_modules ---"
guard "0=allow" '{"tool_name":"Bash","tool_input":{"command":"rm -rf node_modules"}}'

# main 直コミット: 一時 git リポジトリを main ブランチで作り、その cwd で評価する。
git -C "$TMP" init -q -b main
git -C "$TMP" -c user.email=t@example -c user.name=t commit -q --allow-empty -m init
echo "--- 5) main ブランチでの git commit（一時リポジトリで評価） ---"
( cd "$TMP" && printf '%s\n' '{"tool_name":"Bash","tool_input":{"command":"git commit -m x"}}' | "$PY" "$GUARD" )
echo "→ exit=$?（期待: 2=block, branch=main）"
echo

git -C "$TMP" branch -m feat/x
echo "--- 6) フィーチャーブランチ feat/x での同じ git commit ---"
( cd "$TMP" && printf '%s\n' '{"tool_name":"Bash","tool_input":{"command":"git commit -m x"}}' | "$PY" "$GUARD" )
echo "→ exit=$?（期待: 0=allow, branch=feat/x）"
echo

echo "########## PostToolUse トレース（第6部の入力） ##########"
export CLAUDE_TRACE_LOG="$TMP/trace-demo.jsonl"
printf '%s\n' '{"session_id":"demo","tool_name":"Read","tool_input":{"file_path":"README.md"}}' | "$PY" "$TRACE"
printf '%s\n' '{"session_id":"demo","tool_name":"Bash","tool_input":{"command":"pytest -q"}}' | "$PY" "$TRACE"
echo "--- 追記された JSONL（1行1ツール呼び出し） ---"
cat "$CLAUDE_TRACE_LOG"
echo

echo "########## PostToolUse 自動整形（ruff --fix） ##########"
BAD="$TMP/bad_style.py"
printf '%s\n' 'import sys' 'import os' 'print(os.getcwd(), sys.argv)' > "$BAD"
echo "--- 整形前（import 未整列） ---"; cat "$BAD"
printf '%s\n' "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$BAD\"}}" | "$PY" "$RUFF_FIX"
echo "--- ruff_fix hook 通過後 ---"; cat "$BAD"
