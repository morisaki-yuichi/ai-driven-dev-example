"""幻覚 API のデモ — 存在しない str.slugify() を使う代表例。

これは「TODO タイトルからスラッグを作る関数がほしい」という曖昧な指示に対して、
AI が自信満々に返しがちな一次出力の *再構成*（representative reconstruction）です。
なぜ「本物のセッション録」でなく再構成なのかは README.md の「正直さについて」を参照。
"""


def make_slug(title: str) -> str:
    """TODO タイトルを URL 用スラッグに変換する（つもり）。"""
    # str に slugify メソッドは存在しない（＝幻覚 API）。
    # だが、いかにも存在しそうに見えるのが厄介なところ。
    return title.strip().lower().slugify()


if __name__ == "__main__":
    print(make_slug("Buy 2 Milk!"))
