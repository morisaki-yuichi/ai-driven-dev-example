"""make_slug の正しい実装（標準ライブラリのみ・追加依存なし）。

幻覚版（make_slug_hallucinated.py）を、受け入れ条件を満たすよう作り直したもの。
"""

import re
import unicodedata


def make_slug(title: str) -> str:
    """TODO タイトルを URL 用スラッグに変換する。

    - Unicode を NFKD 正規化し、ASCII に落とす
    - 英数字以外の連続を1つの '-' にまとめる
    - 先頭・末尾の '-' を除く
    """
    normalized = unicodedata.normalize("NFKD", title)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug


if __name__ == "__main__":
    print(make_slug("Buy 2 Milk!"))
