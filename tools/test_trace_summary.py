"""検出網: trace_summary の集計を固定する（第6部・可観測性）。

集計器は「後から再構成できる」ことの要。壊れた行・欠けたフィールド・時間差分の扱いを
テストで固定し、静かな回帰を防ぐ。
"""

from __future__ import annotations

from pathlib import Path

from trace_summary import Summary, format_report, load_records, summarize

_FIXTURE = (
    Path(__file__).resolve().parents[1] / "experiments" / "07-observability" / "sample-trace.jsonl"
)


def _record(ts: str, tool: str, **extra: str) -> dict[str, object]:
    return {"ts": ts, "session_id": "s1", "tool_name": tool, **extra}


def test_counts_by_tool() -> None:
    records = [
        _record("2026-07-05T00:00:00+00:00", "Bash", command="pytest -q"),
        _record("2026-07-05T00:00:01+00:00", "Bash", command="ruff check ."),
        _record("2026-07-05T00:00:02+00:00", "Read", file_path="README.md"),
    ]
    s = summarize(records)
    assert s.total == 3
    assert s.by_tool["Bash"] == 2
    assert s.by_tool["Read"] == 1


def test_span_and_step_elapsed() -> None:
    records = [
        _record("2026-07-05T00:00:00+00:00", "Read", file_path="a.py"),
        _record("2026-07-05T00:00:10+00:00", "Bash", command="slow step"),  # 10s ギャップ
        _record("2026-07-05T00:00:11+00:00", "Edit", file_path="a.py"),
    ]
    s = summarize(records)
    assert s.span_s == 11.0
    # 最初のステップは前が無いので None、2番目が最大の 10s
    assert s.steps[0].elapsed_s is None
    slowest = max((x for x in s.steps if x.elapsed_s is not None), key=lambda x: x.elapsed_s or 0.0)
    assert slowest.elapsed_s == 10.0
    assert slowest.tool_name == "Bash"


def test_malformed_lines_are_counted_not_fatal(tmp_path: Path) -> None:
    log = tmp_path / "t.jsonl"
    log.write_text(
        '{"ts":"2026-07-05T00:00:00+00:00","tool_name":"Bash"}\n'
        "this is not json\n"
        "\n"
        '{"ts":"2026-07-05T00:00:01+00:00","tool_name":"Read","file_path":"x"}\n',
        encoding="utf-8",
    )
    records, malformed = load_records(log)
    assert len(records) == 2
    assert malformed == 1


def test_mixed_schema_tolerated() -> None:
    # 旧スキーマ（ts が秒精度・command 欠落）と新スキーマが混ざっても落ちない
    records = [
        {"ts": "2026-07-05T00:00:00+00:00", "tool_name": "Bash"},
        {"tool_name": "Edit", "file_path": "a.py"},  # ts 欠落
        {"ts": "not-a-timestamp", "tool_name": "Read"},  # 壊れた ts
    ]
    s = summarize(records)
    assert s.total == 3
    assert s.by_tool["Edit"] == 1
    # span は有効な ts が1つしか無いので None
    assert s.span_s is None


def test_report_renders_without_crash() -> None:
    empty = format_report(Summary(), "none")
    assert "レコード 0 件" in empty


def test_fixture_summarizes() -> None:
    assert _FIXTURE.exists(), "サンプルトレースが必要（実験07）"
    records, malformed = load_records(_FIXTURE)
    s = summarize(records, malformed)
    assert s.total >= 5
    report = format_report(s, str(_FIXTURE))
    assert "ツール別" in report
    assert "遅かったステップ" in report
