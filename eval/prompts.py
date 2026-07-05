"""失敗実験の主役: 2つのプロンプト。B は『改善』のつもりで質を落とす（第7部）。

A（基準）は URL スラッグの規約を明示する。B は「もっと読みやすく」と“改善”したつもりで、
固有名詞の大文字やアクセントを残すよう指示し、結果として URL 安全性を壊す。
vibes（見た目の読みやすさ）では気づけない回帰を、eval が決定的に検出する。
"""

# A: 小文字・ASCII・ハイフン区切りを明示（良いスラッグ）。
PROMPT_A = (
    "Convert the blog post title into a URL slug. "
    "Rules: all lowercase; ASCII only (transliterate accents); "
    "words separated by single hyphens; no leading or trailing hyphens. "
    "Output ONLY the slug, nothing else.\n\nTitle: {title}"
)

# B: 「人に優しく読みやすく」——大文字/アクセントを残す＝URL 安全性の回帰（見た目は良く見える）。
PROMPT_B = (
    "Turn the title into a clean, human-friendly slug. "
    "Keep it readable: preserve the original capitalization of proper nouns "
    "and keep accented characters as-is. Separate words with hyphens.\n\nTitle: {title}"
)
