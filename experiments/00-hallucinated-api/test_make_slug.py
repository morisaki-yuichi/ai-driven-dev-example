"""検出網: make_slug の受け入れ条件をテストで固定する。

追加依存なしで実行できる:
    python -m unittest -v

このテストを make_slug（正しい実装）に向ければ緑になり、
幻覚版に向ければ import/実行の時点で落ちる。テストは「幻覚が
仕様に届いていないこと」を機械的に検出する検証網である。
"""

import unittest

from make_slug import make_slug


class TestMakeSlug(unittest.TestCase):
    def test_basic(self) -> None:
        # 記号や空白を跨いでも、英数字だけの slug になる
        self.assertEqual(make_slug("Buy 2 Milk!"), "buy-2-milk")

    def test_collapses_separators(self) -> None:
        # 連続する空白は1つの '-' にまとまる
        self.assertEqual(make_slug("  Hello   World  "), "hello-world")

    def test_strips_edges(self) -> None:
        # 先頭・末尾の記号は落ちる
        self.assertEqual(make_slug("!!!Wow!!!"), "wow")


if __name__ == "__main__":
    unittest.main()
