#!/usr/bin/env python3
"""トレース集計 — hook が吐いた JSONL を「後から再構成できる」形に読む（第6部・可観測性）。

入力は ``docs/traces/tool-calls.jsonl``（``.claude/hooks/trace.py`` が1行ずつ追記）。
出力は「何を・何回・どの順で・どのステップに時間がかかったか」。観測できないものは最適化できない。

使い方::

    python tools/trace_summary.py [trace.jsonl]   # 既定: docs/traces/tool-calls.jsonl

設計:
- 実トレースは async 追記で壊れた行が混じりうる。行単位で頑健にパースし、壊れた行は数えて飛ばす。
- スキーマは進化する（``ts`` の精度など）。欠けたフィールドは黙って無視する。
- 時間は ``ts`` の隣接差分＝ステップ経過（直前からの経過・ツール＋モデル＋待ち込み）として出す。
  ツール単体レイテンシやトークン/コストは hook 入力に無い（別系統。README の Try 参照）。
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

_DEFAULT = Path(__file__).resolve().parents[1] / "docs" / "traces" / "tool-calls.jsonl"


@dataclass
class Step:
    """タイムライン上の1ステップ（1レコード）と、直前からの経過秒。"""

    index: int
    tool_name: str
    label: str
    elapsed_s: float | None


@dataclass
class Summary:
    total: int = 0
    malformed: int = 0
    sessions: set[str] = field(default_factory=set)
    by_tool: Counter[str] = field(default_factory=Counter)
    files: Counter[str] = field(default_factory=Counter)
    span_s: float | None = None
    steps: list[Step] = field(default_factory=list)


def load_records(path: Path) -> tuple[list[dict[str, Any]], int]:
    """JSONL を1行ずつ読む。壊れた行は飛ばし、その数を返す（頑健パース）。"""
    records: list[dict[str, Any]] = []
    malformed = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(obj, dict):
            records.append(obj)
        else:
            malformed += 1
    return records, malformed


def _parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _label(record: dict[str, Any]) -> str:
    command = record.get("command")
    if command:
        return " ".join(str(command).split())[:60]
    file_path = record.get("file_path")
    if file_path:
        return str(file_path)
    return ""


def summarize(records: list[dict[str, Any]], malformed: int = 0) -> Summary:
    summary = Summary(total=len(records), malformed=malformed)
    prev_ts: datetime | None = None
    times: list[datetime] = []
    for i, record in enumerate(records):
        tool = str(record.get("tool_name") or "?")
        summary.by_tool[tool] += 1
        session = record.get("session_id")
        if isinstance(session, str):
            summary.sessions.add(session)
        file_path = record.get("file_path")
        if isinstance(file_path, str):
            summary.files[file_path] += 1
        ts = _parse_ts(record.get("ts"))
        elapsed = (ts - prev_ts).total_seconds() if ts and prev_ts else None
        summary.steps.append(Step(i, tool, _label(record), elapsed))
        if ts:
            times.append(ts)
            prev_ts = ts
    if len(times) >= 2:
        summary.span_s = (times[-1] - times[0]).total_seconds()
    return summary


def _bar(count: int, total: int, width: int = 24) -> str:
    filled = round(width * count / total) if total else 0
    return "#" * filled + "·" * (width - filled)


def format_report(summary: Summary, source: str) -> str:
    lines = [f"トレース集計: {source}"]
    span = f"{summary.span_s:.1f}s" if summary.span_s is not None else "不明"
    lines.append(
        f"  レコード {summary.total} 件"
        f"（session {len(summary.sessions)} / 期間 {span}"
        + (f" / 壊れた行 {summary.malformed}" if summary.malformed else "")
        + "）"
    )
    if summary.total == 0:
        lines.append("  （レコードなし）")
        return "\n".join(lines)

    namew = min(max((len(t) for t in summary.by_tool), default=4), 16)
    lines.append("  ツール別:")
    for tool, count in summary.by_tool.most_common():
        pct = 100 * count / summary.total
        bar = _bar(count, summary.total)
        lines.append(f"    {tool[:namew]:<{namew}} {count:>3}  {bar} {pct:4.0f}%")

    top_files = summary.files.most_common(5)
    if top_files:
        lines.append("  よく触ったファイル:")
        for path, count in top_files:
            lines.append(f"    {count:>3}  {path}")

    timed = [s for s in summary.steps if s.elapsed_s is not None]
    if timed:
        lines.append("  遅かったステップ（前ステップからの経過＝ツール＋モデル＋待ち込み・上位5）:")
        for step in sorted(timed, key=lambda s: s.elapsed_s or 0.0, reverse=True)[:5]:
            assert step.elapsed_s is not None
            label = f"  {step.label}" if step.label else ""
            lines.append(f"    +{step.elapsed_s:6.1f}s  #{step.index:<3} {step.tool_name}{label}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else _DEFAULT
    if not path.exists():
        print(f"トレースが見つかりません: {path}", file=sys.stderr)
        print("（hook が有効な状態でツールを使うと docs/traces/ に貯まる）", file=sys.stderr)
        return 1
    records, malformed = load_records(path)
    print(format_report(summarize(records, malformed), str(path)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
