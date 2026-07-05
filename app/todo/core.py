"""TODO ドメインコア（純ロジック・Web 非依存）。

受け入れ条件は docs/specs/todo-core.md、テストは test_core.py。
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import count


@dataclass
class Todo:
    id: int
    title: str
    completed: bool = False


class TodoList:
    """TODO の集合を保持し、追加・一覧・完了を提供する（メモリ内）。"""

    def __init__(self) -> None:
        self._todos: list[Todo] = []
        self._ids = count(1)

    def add(self, title: str) -> Todo:
        title = title.strip()
        if not title:
            raise ValueError("title must not be empty")
        todo = Todo(id=next(self._ids), title=title)
        self._todos.append(todo)
        return todo

    def list(self) -> list[Todo]:
        return list(self._todos)  # 追加順・防御的コピー

    def complete(self, todo_id: int) -> Todo:
        for todo in self._todos:
            if todo.id == todo_id:
                todo.completed = True
                return todo
        raise KeyError(f"todo not found: {todo_id}")
