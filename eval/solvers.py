"""Solver — タスク（Case）からスラッグ出力を得る手段（第7部）。

2種類:
- ``recorded_solver`` … 収録フィクスチャ（JSONL）を読む。コストゼロ・完全再現可能。
- ``LiveSolver``      … 実 Claude API を呼ぶ。usage を集計しコスト概算に使う（要 SDK＋認証）。

live は API のある環境で走らせる。モデルIDは ``pricing`` で実測固定した現行IDを使う。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from harness import Case, Solver


def _read_recorded(path: Path) -> dict[str, str]:
    outputs: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        outputs[str(record["id"])] = str(record["output"])
    return outputs


def recorded_solver(path: Path) -> Solver:
    """収録済みモデル出力（JSONL: {id, output}）を返す Solver。"""
    outputs = _read_recorded(path)

    def solve(case: Case) -> str:
        return outputs.get(case.id, "")

    return solve


def _anthropic_client() -> Any:
    import anthropic  # 遅延 import: live 実行時のみ必要（フィクスチャ採点には不要）

    return anthropic.Anthropic()


def _first_text(response: Any) -> str:
    for block in response.content:
        if getattr(block, "type", None) == "text":
            return str(block.text)
    return ""


class LiveSolver:
    """実 API を呼ぶ Solver。usage を累積し、コスト概算に使う。

    モデルIDは pricing.PRICING のキー（現行の実測固定ID）を渡す。max_tokens は小さくてよい
    （出力はスラッグ1行）。要 ``pip install anthropic`` ＋ 認証（ANTHROPIC_API_KEY / ant login）。
    """

    def __init__(self, model: str, prompt_template: str, max_tokens: int = 64) -> None:
        self.model = model
        self.prompt_template = prompt_template
        self.max_tokens = max_tokens
        self.input_tokens = 0
        self.output_tokens = 0
        self._client = _anthropic_client()

    def __call__(self, case: Case) -> str:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": self.prompt_template.format(title=case.title)}],
        )
        usage = response.usage
        self.input_tokens += int(usage.input_tokens)
        self.output_tokens += int(usage.output_tokens)
        return _first_text(response).strip()
