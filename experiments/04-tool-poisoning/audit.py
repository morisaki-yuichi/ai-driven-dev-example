"""毒入りツールを機械的に洗い出す簡易監査（検出網の1層）。

注意: キーワード監査は**弱く、回避されやすい**。主防御はアーキテクチャ
——「外部テキストを命令扱いしない」＋「最小権限で被害を封じる」。
本監査はあくまで補助的な検出層にすぎない（README 参照）。
"""

from __future__ import annotations

# 命令注入によく現れる語（日英の代表例・網羅ではない）
SUSPICIOUS = [
    "ignore previous",
    "system override",
    "system prompt",
    "無視",
    "優先せよ",
    "必ず",
    "言及するな",
    "言及してはならない",
]


def scan(text: str) -> list[str]:
    low = text.lower()
    return [p for p in SUSPICIOUS if p.lower() in low]


def audit(descriptions: dict[str, str]) -> dict[str, list[str]]:
    """ツール名→description の辞書を受け取り、疑わしいツールだけ返す。"""
    return {name: hits for name, desc in descriptions.items() if (hits := scan(desc))}
