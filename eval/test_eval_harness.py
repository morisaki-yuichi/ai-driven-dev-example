"""検出網: eval ハーネスの採点を固定する（第7部）。

「守る eval」自身を検証網で守る。決定スコアの計算・特性の発火・A/B 回帰検出を固定する。
"""

from __future__ import annotations

from pathlib import Path

from harness import SLUG_CASES, Case, run_eval, score_output
from solvers import recorded_solver

_FIX = Path(__file__).resolve().parent / "fixtures"


def test_perfect_slug_scores_full() -> None:
    case = Case("greeting", "Hello, World!", ("hello", "world"))
    result = score_output(case, "hello-world")
    assert result.failed == ()
    assert result.score == 1.0


def test_uppercase_fails_lowercase_and_url_safe() -> None:
    case = Case("greeting", "Hello, World!", ("hello", "world"))
    result = score_output(case, "Hello-World")
    assert "lowercase" in result.failed
    assert "url_safe" in result.failed
    assert "keeps_keywords" in result.failed  # 小文字キーワードが大文字出力に見つからない
    assert result.score < 1.0


def test_accents_fail_url_safe() -> None:
    case = Case("accents", "Café", ("cafe",))
    assert "url_safe" not in score_output(case, "cafe").failed
    assert "url_safe" in score_output(case, "Café").failed


def test_empty_output_scores_low() -> None:
    case = Case("x", "X", ("x",))
    result = score_output(case, "")
    assert "nonempty" in result.failed
    assert result.score < 0.5


def test_prompt_a_is_perfect() -> None:
    a = run_eval("A", recorded_solver(_FIX / "prompt_a.jsonl"))
    assert a.score == 1.0
    assert len(a.results) == len(SLUG_CASES)


def test_prompt_b_regresses_below_a() -> None:
    a = run_eval("A", recorded_solver(_FIX / "prompt_a.jsonl"))
    b = run_eval("B", recorded_solver(_FIX / "prompt_b.jsonl"))
    # B は「読みやすい」が URL 安全性を壊す → 決定スコアは明確に悪化
    assert b.score < a.score
    assert "url_safe" in b.failed_checks()
    assert "lowercase" in b.failed_checks()
