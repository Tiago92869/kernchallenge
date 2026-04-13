from datetime import date, timedelta

from app.models.time_entry import TimeEntry


def test_create_time_entry_returns_201(client, user_factory, project_factory):
    user = user_factory(email="route-time-entry-create-user@test.com")
    project = project_factory()

    response = client.post(
        "/time-entries",
        json={
            "user_id": str(user.id),
            "project_id": str(project.id),
            "description": "Worked on route",
            "date": date.today().isoformat(),
            "hours": 90,
        },
    )

    assert response.status_code == 201

    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["user_id"] == str(user.id)
    assert body["data"]["project_id"] == str(project.id)
    assert body["data"]["description"] == "Worked on route"
    assert body["data"]["hours"] == 90


def test_create_time_entry_returns_400_for_invalid_date(client, user_factory, project_factory):
    user = user_factory(email="route-time-entry-invalid-date-user@test.com")
    project = project_factory()

    response = client.post(
        "/time-entries",
        json={
            "user_id": str(user.id),
            "project_id": str(project.id),
            "description": "Worked on route",
            "date": "31-12-2026",
            "hours": 90,
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid date format, expected YYYY-MM-DD"


def test_create_time_entry_returns_400_for_invalid_hours(client, user_factory, project_factory):
    user = user_factory(email="route-time-entry-invalid-hours-user@test.com")
    project = project_factory()

    response = client.post(
        "/time-entries",
        json={
            "user_id": str(user.id),
            "project_id": str(project.id),
            "description": "Worked on route",
            "date": date.today().isoformat(),
            "hours": 0,
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Hours should be a positive number"


def test_create_time_entry_returns_400_for_future_date(client, user_factory, project_factory):
    user = user_factory(email="route-time-entry-future-date-user@test.com")
    project = project_factory()

    response = client.post(
        "/time-entries",
        json={
            "user_id": str(user.id),
            "project_id": str(project.id),
            "description": "Worked on route",
            "date": (date.today() + timedelta(days=1)).isoformat(),
            "hours": 30,
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Date should not be in the future"


def test_create_time_entry_returns_404_for_archived_project(client, user_factory, project_factory):
    user = user_factory(email="route-time-entry-archived-project-user@test.com")
    project = project_factory(is_archived=True)

    response = client.post(
        "/time-entries",
        json={
            "user_id": str(user.id),
            "project_id": str(project.id),
            "description": "Worked on route",
            "date": date.today().isoformat(),
            "hours": 30,
        },
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Project not found or is archived"


def test_create_time_entry_returns_404_for_inactive_user(client, user_factory, project_factory):
    user = user_factory(email="route-time-entry-inactive-user@test.com", is_active=False)
    project = project_factory()

    response = client.post(
        "/time-entries",
        json={
            "user_id": str(user.id),
            "project_id": str(project.id),
            "description": "Worked on route",
            "date": date.today().isoformat(),
            "hours": 30,
        },
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == f"User with id {user.id} not found or is not active"


def test_get_time_entry_by_id_returns_200(client, time_entry_factory):
    time_entry = time_entry_factory(description="Get by id")

    response = client.get(f"/time-entries/{time_entry.id}")

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["id"] == str(time_entry.id)
    assert body["data"]["description"] == "Get by id"


def test_get_time_entry_by_id_returns_404(client):
    response = client.get("/time-entries/550e8400-e29b-41d4-a716-446655440000")

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Time entry not found"


def test_get_time_entries_with_filters_returns_200(
    client, time_entry_factory, user_factory, project_factory
):
    user = user_factory(email="route-time-entry-filter-user@test.com")
    project = project_factory()
    time_entry_factory(
        user=user, project=project, work_date=date.today() - timedelta(days=2), description="Older"
    )
    time_entry_factory(
        user=user, project=project, work_date=date.today() - timedelta(days=1), description="Newer"
    )

    response = client.get(
        "/time-entries",
        query_string={
            "user_id": str(user.id),
            "project_id": str(project.id),
            "start_date": (date.today() - timedelta(days=3)).isoformat(),
            "end_date": date.today().isoformat(),
        },
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 2


def test_get_time_entries_with_filters_returns_400_for_invalid_start_date(client):
    response = client.get(
        "/time-entries",
        query_string={
            "start_date": "2026/03/25",
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid start_date format, expected YYYY-MM-DD"


def test_get_time_entries_with_filters_returns_400_for_invalid_end_date(client):
    response = client.get(
        "/time-entries",
        query_string={
            "end_date": "2026/03/25",
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid end_date format, expected YYYY-MM-DD"


def test_get_time_entries_with_filters_returns_400_for_start_after_end(client):
    response = client.get(
        "/time-entries",
        query_string={
            "start_date": date.today().isoformat(),
            "end_date": (date.today() - timedelta(days=1)).isoformat(),
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Start date should be before end date"


def test_get_time_entries_with_filters_returns_404_for_archived_project(client, project_factory):
    project = project_factory(is_archived=True)

    response = client.get(
        "/time-entries",
        query_string={
            "project_id": str(project.id),
        },
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Project not found or is archived"


def test_get_time_entries_with_filters_returns_404_for_inactive_user(client, user_factory):
    user = user_factory(email="route-time-entry-filter-inactive-user@test.com", is_active=False)

    response = client.get(
        "/time-entries",
        query_string={
            "user_id": str(user.id),
        },
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == f"User with id {user.id} not found or is not active"


def test_update_time_entry_returns_200(client, time_entry_factory):
    time_entry = time_entry_factory(description="Before update", duration_minutes=60)

    response = client.put(
        f"/time-entries/{time_entry.id}",
        json={
            "user_id": str(time_entry.user_id),
            "project_id": str(time_entry.project_id),
            "description": "After update",
            "date": date.today().isoformat(),
            "hours": 120,
        },
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["description"] == "After update"
    assert body["data"]["hours"] == 120


def test_update_time_entry_returns_403_when_different_user(
    client, time_entry_factory, user_factory
):
    time_entry = time_entry_factory(description="Before update")
    different_user = user_factory(email="route-time-entry-update-different-user@test.com")

    response = client.put(
        f"/time-entries/{time_entry.id}",
        json={
            "user_id": str(different_user.id),
            "project_id": str(time_entry.project_id),
            "description": "Unauthorized update",
            "date": date.today().isoformat(),
            "hours": 60,
        },
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert "permission" in body["error"]["message"].lower()


def test_delete_time_entry_by_id_returns_200(client, time_entry_factory):
    time_entry = time_entry_factory(description="Delete from route")

    response = client.delete(
        f"/time-entries/{time_entry.id}", json={"user_id": str(time_entry.user_id)}
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["message"] == "Time entry deleted successfully"

    refreshed = TimeEntry.query.filter_by(id=time_entry.id).first()
    assert refreshed.deleted_at is not None


def test_delete_time_entry_by_id_returns_404(client):
    response = client.delete(
        "/time-entries/550e8400-e29b-41d4-a716-446655440000",
        json={"user_id": "550e8400-e29b-41d4-a716-446655440001"},
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Time entry not found"


def test_delete_time_entry_by_id_returns_403_when_different_user(
    client, time_entry_factory, user_factory
):
    time_entry = time_entry_factory(description="Delete from route")
    different_user = user_factory(email="route-time-entry-delete-different-user@test.com")

    response = client.delete(
        f"/time-entries/{time_entry.id}", json={"user_id": str(different_user.id)}
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert "permission" in body["error"]["message"].lower()
