"""受け入れ条件（docs/specs/todo-core.md）を pytest に落としたもの。

各テストが1つの AC に対応する。実装前は赤、実装後は緑。
"""

import pytest
from core import TodoList


def test_add_creates_incomplete_todo_with_sequential_id() -> None:
    # AC1
    tl = TodoList()
    a = tl.add("買い物")
    b = tl.add("掃除")
    assert (a.id, b.id) == (1, 2)
    assert a.completed is False
    assert [t.title for t in tl.list()] == ["買い物", "掃除"]


def test_add_trims_and_rejects_empty_title() -> None:
    # AC2
    tl = TodoList()
    assert tl.add("  掃除  ").title == "掃除"
    with pytest.raises(ValueError):
        tl.add("   ")


def test_list_returns_in_insertion_order() -> None:
    # AC3
    tl = TodoList()
    for title in ["a", "b", "c"]:
        tl.add(title)
    assert [t.title for t in tl.list()] == ["a", "b", "c"]


def test_complete_marks_done_and_unknown_id_raises() -> None:
    # AC4
    tl = TodoList()
    t = tl.add("原稿")
    assert tl.complete(t.id).completed is True
    with pytest.raises(KeyError):
        tl.complete(999)
