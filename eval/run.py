"""eval ランナー CLI — プロンプト A/B を採点して回帰を検出する（第7部）。

既定は**収録フィクスチャ**で A/B を採点（コストゼロ・再現可能）。``--live`` で実 API を呼ぶ。

    python eval/run.py                                  # 収録フィクスチャ（既定）
    python eval/run.py --live --model claude-haiku-4-5  # 実 API（要 SDK＋認証・実コスト）
"""

from __future__ import annotations

import sys
from pathlib import Path

from harness import EvalResult, run_eval
from pricing import estimate_cost_usd
from prompts import PROMPT_A, PROMPT_B
from solvers import LiveSolver, recorded_solver

_FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _format_result(result: EvalResult) -> list[str]:
    lines = [f"[{result.label}] 総合スコア {result.score:.3f}"]
    for r in result.results:
        mark = "OK " if not r.failed else "NG "
        detail = "" if not r.failed else f"  失敗: {', '.join(r.failed)}"
        lines.append(f"    {mark} {r.case_id:<9} {r.score:.2f}  {r.output!r}{detail}")
    failed = result.failed_checks()
    if failed:
        worst = ", ".join(f"{name}×{n}" for name, n in sorted(failed.items(), key=lambda x: -x[1]))
        lines.append(f"    落ちた特性: {worst}")
    return lines


def _verdict(a: EvalResult, b: EvalResult) -> str:
    delta = b.score - a.score
    if delta < 0:
        return (
            f"⛔ 回帰を検出: B は A より {-delta:.3f} 悪化"
            f"（A={a.score:.3f} → B={b.score:.3f}）。vibes では気づかない。"
        )
    if delta > 0:
        return f"✅ B は A より {delta:.3f} 改善（A={a.score:.3f} → B={b.score:.3f}）。"
    return f"= 差なし（A={a.score:.3f}, B={b.score:.3f}）。"


def main(argv: list[str]) -> int:
    live = "--live" in argv
    model = "claude-haiku-4-5"
    if "--model" in argv:
        model = argv[argv.index("--model") + 1]

    if live:
        solver_a: LiveSolver = LiveSolver(model, PROMPT_A)
        solver_b: LiveSolver = LiveSolver(model, PROMPT_B)
        a = run_eval(f"prompt_A (live/{model})", solver_a)
        b = run_eval(f"prompt_B (live/{model})", solver_b)
    else:
        a = run_eval("prompt_A (recorded)", recorded_solver(_FIXTURES / "prompt_a.jsonl"))
        b = run_eval("prompt_B (recorded)", recorded_solver(_FIXTURES / "prompt_b.jsonl"))

    print("=" * 72)
    for line in _format_result(a):
        print(line)
    print("-" * 72)
    for line in _format_result(b):
        print(line)
    print("=" * 72)
    print(_verdict(a, b))

    if live:
        for solver in (solver_a, solver_b):
            cost = estimate_cost_usd(model, solver.input_tokens, solver.output_tokens)
            cost_str = "不明" if cost is None else f"${cost:.4f}"
            print(
                f"  live usage: in={solver.input_tokens} out={solver.output_tokens} "
                f"概算コスト {cost_str}"
            )
    else:
        print("  （収録フィクスチャの採点。実コストは発生しない。live は --live）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
