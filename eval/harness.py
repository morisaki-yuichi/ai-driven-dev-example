"""最小 eval ハーネス — 期待特性をコードで採点する（第7部・決定スコア中心）。

コードの tests が「実装の正しさ」を測るのに対し、eval は「モデル出力の質」を測る。
題材は make_slug（タイトル → URL スラッグ）。期待特性（小文字・URL 安全・ハイフン区切り 等）を
**決定的な述語**で採点する。LLM-as-judge とモデル階級比較は将来 Try（別テーマ）。

用語:
- ``Case``  … 1タスク（入力タイトル＋残っていてほしいキーワード）。
- ``Check`` … 出力が満たすべき期待特性（決定的な述語）。
- ``Solver``… タイトルからスラッグを得る手段（実 API or 収録フィクスチャ・``solvers`` 参照）。
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from statistics import fmean


@dataclass(frozen=True)
class Case:
    """1タスク: 入力タイトルと、出力に残っていてほしい語（内容特性の確認用）。"""

    id: str
    title: str
    keywords: tuple[str, ...]


Check = Callable[[str, Case], bool]  # (output, case) -> 満たしていれば True


def _nonempty(out: str, case: Case) -> bool:
    return bool(out.strip())


def _lowercase(out: str, case: Case) -> bool:
    return out == out.lower()


def _url_safe(out: str, case: Case) -> bool:
    return re.fullmatch(r"[a-z0-9-]+", out) is not None


def _hyphen_separated(out: str, case: Case) -> bool:
    return " " not in out and out != ""


def _no_edge_hyphen(out: str, case: Case) -> bool:
    return not (out.startswith("-") or out.endswith("-"))


def _no_double_hyphen(out: str, case: Case) -> bool:
    return "--" not in out


def _keeps_keywords(out: str, case: Case) -> bool:
    return all(k in out for k in case.keywords)


# 期待特性の一覧（名前 → 述語）。粒度を細かく保ち、どの特性で落ちたかを診断できるようにする。
CHECKS: dict[str, Check] = {
    "nonempty": _nonempty,
    "lowercase": _lowercase,
    "url_safe": _url_safe,
    "hyphen_separated": _hyphen_separated,
    "no_edge_hyphen": _no_edge_hyphen,
    "no_double_hyphen": _no_double_hyphen,
    "keeps_keywords": _keeps_keywords,
}


# 小さな eval セット。キーワードは小文字 ASCII にし、大文字化やアクセント残しを回帰として捕まえる。
SLUG_CASES: tuple[Case, ...] = (
    Case("greeting", "Hello, World!", ("hello", "world")),
    Case("tips", "10 Tips for Better Sleep", ("10", "tips", "better", "sleep")),
    Case("accents", "Café Münchën Delights", ("cafe", "munchen", "delights")),
    Case("spaces", "  Spaces   Everywhere  ", ("spaces", "everywhere")),
    Case("version", "Python 3.12 & You", ("python", "you")),
    Case("fox", "The Quick Brown Fox", ("quick", "brown", "fox")),
)


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    output: str
    passed: tuple[str, ...]
    failed: tuple[str, ...]

    @property
    def score(self) -> float:
        total = len(self.passed) + len(self.failed)
        return len(self.passed) / total if total else 0.0


@dataclass(frozen=True)
class EvalResult:
    label: str
    results: tuple[CaseResult, ...]

    @property
    def score(self) -> float:
        return fmean(r.score for r in self.results) if self.results else 0.0

    def failed_checks(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self.results:
            for name in r.failed:
                counts[name] = counts.get(name, 0) + 1
        return counts


Solver = Callable[[Case], str]


def score_output(case: Case, output: str) -> CaseResult:
    passed: list[str] = []
    failed: list[str] = []
    for name, check in CHECKS.items():
        (passed if check(output, case) else failed).append(name)
    return CaseResult(case.id, output, tuple(passed), tuple(failed))


def run_eval(label: str, solver: Solver, cases: tuple[Case, ...] = SLUG_CASES) -> EvalResult:
    return EvalResult(label, tuple(score_output(c, solver(c)) for c in cases))
