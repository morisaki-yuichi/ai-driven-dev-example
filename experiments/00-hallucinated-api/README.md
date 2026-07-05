# 実験00 — 幻覚 API を検証網で捕まえる

> 第0部（概念）の目玉実験。形式は **予想 → 観察 → 検出網**。
> 実行環境: Python 3.12.3 / 記録日 2026-07-05 / 著者モデル claude-opus-4-8。
> 関連: [`docs/concepts/00-llm-nature.md`](../../docs/concepts/00-llm-nature.md) の「2. 幻覚」。

## ねらい

LLM の **幻覚（hallucination）** ——「存在しない API を、もっともらしく自信満々に使う」——
を体験し、それを **検証網（実行・テスト・型チェック）が機械的に捕まえる**構図を、
最短の1ファイルで確認する。狙いは「AI を疑うこと」ではなく、
**疑わなくて済むように検証網を先に置く**発想を身につけること。

## 予想（実験前に立てる仮説）

「TODO タイトルからスラッグを作る関数がほしい」という**曖昧な指示**だけを与えると、
AI は `python-slugify` のような便利ライブラリの存在を暗黙に仮定し、
`str.slugify()` のような **存在しないメソッド**を使うコードを、
きれいな見た目で返す可能性が高い。そしてそれは**読んだだけでは気づきにくい**。

代表的な一次出力を [`make_slug_hallucinated.py`](./make_slug_hallucinated.py) に置いた:

```python
def make_slug(title: str) -> str:
    return title.strip().lower().slugify()   # ← str に slugify は無い
```

## 観察（実際に動かした結果）

```console
$ python3 make_slug_hallucinated.py
Traceback (most recent call last):
  File ".../make_slug_hallucinated.py", line 17, in <module>
    print(make_slug("Buy 2 Milk!"))
          ^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../make_slug_hallucinated.py", line 13, in make_slug
    return title.strip().lower().slugify()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'slugify'
```

コードは自然に読めるのに、**動かした瞬間に崩れる**。
これが「間違いに自信が伴う」幻覚の怖さ。

## 検出網（何が、どれだけ早く捕まえるか）

同じ幻覚を、複数の網が別々の速さで捕まえる。**早い網ほど安い**（気づくコストが低い）。

| 網 | 捕まえ方 | 速さ／コスト |
|----|----------|--------------|
| **型チェック（mypy/pyright）** | `str` に `slugify` 属性が無い、とコードを動かす前に静的に指摘 | 最速・最安（実行不要） |
| **実行 / import** | 上記のとおり `AttributeError` で即停止 | 速い（該当行に到達すれば） |
| **テスト** | 受け入れ条件を固定しておけば、幻覚版に向けた瞬間に赤 | CI で自動・恒久 |

### 型チェック網の実演（Sprint 1 で回収）

Sprint 0 時点では追加依存なしで再現できる **実行 と テスト** のみ実演した。
Sprint 1 で mypy を導入し、幻覚ファイルに直接当てると、**実行する前に**静的に捕まえる:

```console
$ .venv/bin/mypy experiments/00-hallucinated-api/make_slug_hallucinated.py
.../make_slug_hallucinated.py:13: error: "str" has no attribute "slugify"  [attr-defined]
.../make_slug_hallucinated.py:13: error: Returning Any from function declared to return "str"  [no-any-return]
Found 2 errors in 1 file (checked 1 source file)
```

3層のうち **型チェックが最速**——コードを動かさずに幻覚を指摘する。だから CI は
`ruff → mypy → pytest` の順に、安い網から当てる（[`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)）。
なおこの幻覚ファイルは意図的に壊してあるため、本体ゲート（`mypy experiments`）からは
除外している（設定は [`pyproject.toml`](../../pyproject.toml)）。

## 修正（仕様を足して作り直す）

幻覚に気づいたら、**曖昧だった指示に受け入れ条件を足して**作り直す。
「英数字以外は `-` にまとめ、両端の `-` は除く」を仕様として明文化し、
標準ライブラリだけで実装したのが [`make_slug.py`](./make_slug.py)、
その受け入れ条件を固定したのが [`test_make_slug.py`](./test_make_slug.py)。

```console
$ python3 -m unittest -v test_make_slug
test_basic ... ok
test_collapses_separators ... ok
test_strips_edges ... ok
----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

赤（幻覚）→ 仕様追加 → 緑（検証網が通る）の一往復。これが以降の全スプリントの最小単位。

## 教訓

1. **AI の出力は、そのままでは信頼できない**——読みやすさは正しさの保証ではない。
2. **信頼できないことは、使えないことではない**——検証網で受け止めれば戦力になる。
3. **検証網は「後で」ではなく「先に」**——網が無い状態で幻覚を出させると、誰も気づけない
   （テストのない部分を大改修させる実験＝第1部で、この裏返しを見る）。

## 自分でやってみる

```console
cd experiments/00-hallucinated-api
python3 make_slug_hallucinated.py     # 幻覚が実行で崩れるのを見る
python3 -m unittest -v test_make_slug # 検証網が緑になるのを見る
```

## 正直さについて（この実験の作り方）

上の「予想」に出てくる幻覚コードは、**その場の一発生成をそのまま貼ったものではなく、
よく観測される失敗モードを再構成した代表例**である。理由は第0部で学ぶ性質そのもの——
**非決定性**。「自然な幻覚をオンデマンドで確実に1回出す」こと自体が保証できない。
だからこの教材では、**再現できる部分（検証網が捕まえること）を実行で固定**し、
**再現が保証できない部分（幻覚が出る瞬間）は代表例として明示**する。
写経者の手元では、同じ曖昧プロンプトから別の幻覚（別の存在しない関数名や引数）が
出るかもしれない——それは失敗ではなく、非決定性の実物である。
