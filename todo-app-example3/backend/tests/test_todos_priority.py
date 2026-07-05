from fastapi.testclient import TestClient


def test_create_defaults_priority_to_medium(auth_client: TestClient) -> None:
    # AC1: 省略時は medium
    body = auth_client.post("/todos", json={"title": "既定優先度"}).json()
    assert body["priority"] == "medium"


def test_create_accepts_valid_priority(auth_client: TestClient) -> None:
    # AC2: low/medium/high を指定できる
    body = auth_client.post("/todos", json={"title": "高優先", "priority": "high"}).json()
    assert body["priority"] == "high"


def test_create_rejects_invalid_priority(auth_client: TestClient) -> None:
    # AC3: 不正な値は 422
    response = auth_client.post("/todos", json={"title": "不正", "priority": "urgent"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "priority"]


def test_patch_changes_priority(auth_client: TestClient) -> None:
    # AC4: PATCH で変更できる
    created = auth_client.post("/todos", json={"title": "更新対象"}).json()
    updated = auth_client.patch(
        f"/todos/{created['id']}", json={"priority": "low"}
    ).json()
    assert updated["priority"] == "low"


def test_patch_rejects_invalid_priority(auth_client: TestClient) -> None:
    # AC3 と対: 更新でも不正値は 422
    created = auth_client.post("/todos", json={"title": "更新対象2"}).json()
    response = auth_client.patch(
        f"/todos/{created['id']}", json={"priority": "urgent"}
    )
    assert response.status_code == 422
