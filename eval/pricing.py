"""モデル価格の実測固定（知識の鮮度）。

価格・モデルIDは推測しない。値は 2026-06-24 時点の claude-api skill / 公式価格表を固定したもの。
**最新は Models API（`client.models.retrieve`）／公式価格ページで確認して差し替える**。
単位は USD / 100万トークン (input, output)。Sonnet 5 は 2026-08-31 まで intro $2.00/$10.00。
"""

from __future__ import annotations

# (input $/1M, output $/1M)
PRICING: dict[str, tuple[float, float]] = {
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-sonnet-5": (3.00, 15.00),
    "claude-opus-4-8": (5.00, 25.00),
}


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float | None:
    """usage からコスト概算。未知モデルは None（推測で埋めない）。"""
    price = PRICING.get(model)
    if price is None:
        return None
    return input_tokens / 1_000_000 * price[0] + output_tokens / 1_000_000 * price[1]
