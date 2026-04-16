from datetime import date, timedelta

from app.models.time_entry import TimeEntry


def _login_and_get_access_token(client, email, password="password123"):
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.get_json()["data"]["auth_token"]


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


def test_get_time_entries_by_project_owner_sees_all(
    client, time_entry_factory, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="route-project-owner-all@test.com")
    member = user_factory(email="route-project-member-all@test.com")
    project = project_factory(owner=owner)
    project_member_factory(project=project, user=member)

    time_entry_factory(user=owner, project=project, description="Owner entry")
    time_entry_factory(user=member, project=project, description="Member entry")

    response = client.get(
        f"/time-entries/project/{project.id}",
        query_string={"user_id": str(owner.id)},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    descriptions = {e["description"] for e in body["data"]}
    assert "Owner entry" in descriptions
    assert "Member entry" in descriptions


def test_get_time_entries_by_project_member_sees_own_only(
    client, time_entry_factory, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="route-project-owner-member@test.com")
    member1 = user_factory(email="route-project-member1-view@test.com")
    member2 = user_factory(email="route-project-member2-view@test.com")
    project = project_factory(owner=owner)
    project_member_factory(project=project, user=member1)
    project_member_factory(project=project, user=member2)

    time_entry_factory(user=owner, project=project, description="Owner entry")
    time_entry_factory(user=member1, project=project, description="Member1 entry 1")
    time_entry_factory(user=member1, project=project, description="Member1 entry 2")
    time_entry_factory(user=member2, project=project, description="Member2 entry")

    response = client.get(
        f"/time-entries/project/{project.id}",
        query_string={"user_id": str(member1.id)},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    descriptions = {e["description"] for e in body["data"]}
    assert "Member1 entry 1" in descriptions
    assert "Member1 entry 2" in descriptions
    assert "Owner entry" not in descriptions
    assert "Member2 entry" not in descriptions


def test_get_time_entries_by_project_denies_non_member(client, user_factory, project_factory):
    owner = user_factory(email="route-project-owner-deny@test.com")
    non_member = user_factory(email="route-project-non-member@test.com")
    project = project_factory(owner=owner)

    response = client.get(
        f"/time-entries/project/{project.id}",
        query_string={"user_id": str(non_member.id)},
    )

    assert response.status_code == 403
    body = response.get_json()
    assert body["success"] is False
    assert "access" in body["error"]["message"].lower()


def test_get_time_entries_by_project_with_date_filter(
    client, time_entry_factory, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="route-project-owner-date@test.com")
    member = user_factory(email="route-project-member-date@test.com")
    project = project_factory(owner=owner)
    project_member_factory(project=project, user=member)

    early = date.today() - timedelta(days=5)
    middle = date.today() - timedelta(days=2)

    time_entry_factory(user=member, project=project, work_date=early, description="Early")
    time_entry_factory(user=member, project=project, work_date=middle, description="Middle")
    time_entry_factory(user=member, project=project, work_date=date.today(), description="Recent")

    response = client.get(
        f"/time-entries/project/{project.id}",
        query_string={
            "user_id": str(member.id),
            "start_date": (date.today() - timedelta(days=3)).isoformat(),
            "end_date": date.today().isoformat(),
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    descriptions = {e["description"] for e in body["data"]}
    assert "Middle" in descriptions
    assert "Recent" in descriptions
    assert "Early" not in descriptions


def test_get_time_entries_by_project_with_search_filter(
    client, time_entry_factory, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="route-project-owner-search@test.com")
    member = user_factory(email="route-project-member-search@test.com")
    project = project_factory(owner=owner)
    project_member_factory(project=project, user=member)

    time_entry_factory(user=member, project=project, description="Fixed dashboard bug")
    time_entry_factory(user=member, project=project, description="Implemented API")
    time_entry_factory(user=member, project=project, description="Updated docs")

    response = client.get(
        f"/time-entries/project/{project.id}",
        query_string={
            "user_id": str(member.id),
            "search": "dashboard",
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["description"] == "Fixed dashboard bug"


def test_get_time_entries_by_project_excludes_deleted(
    client, time_entry_factory, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="route-project-owner-deleted@test.com")
    member = user_factory(email="route-project-member-deleted@test.com")
    project = project_factory(owner=owner)
    project_member_factory(project=project, user=member)

    active = time_entry_factory(user=member, project=project, description="Active")
    deleted = time_entry_factory(user=member, project=project, description="Deleted")

    # Delete one entry via the delete endpoint
    client.delete(f"/time-entries/{deleted.id}", json={"user_id": str(member.id)})

    response = client.get(
        f"/time-entries/project/{project.id}",
        query_string={"user_id": str(member.id)},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["description"] == "Active"


def test_get_time_entries_by_project_returns_400_missing_user_id(client, project_factory):
    project = project_factory()

    response = client.get(f"/time-entries/project/{project.id}")

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert "user_id" in body["error"]["message"].lower()


def test_get_time_entries_by_project_returns_400_invalid_user_id(client, project_factory):
    project = project_factory()

    response = client.get(
        f"/time-entries/project/{project.id}",
        query_string={"user_id": "not-a-uuid"},
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert "user_id" in body["error"]["message"].lower()


def test_get_time_entries_by_project_returns_404_archived_project(
    client, user_factory, project_factory
):
    owner = user_factory(email="route-project-owner-archived@test.com")
    project = project_factory(owner=owner, is_archived=True)

    response = client.get(
        f"/time-entries/project/{project.id}",
        query_string={"user_id": str(owner.id)},
    )

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert "archived" in body["error"]["message"].lower()


def test_get_project_member_time_aggregation_week_returns_200(
    client, time_entry_factory, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="route-aggregation-owner-week@test.com")
    member = user_factory(email="route-aggregation-member-week@test.com")
    project = project_factory(owner=owner)
    project_member_factory(project=project, user=member)

    time_entry_factory(
        user=member,
        project=project,
        work_date=date(2026, 4, 14),
        duration_minutes=60,
        description="W1-A",
    )
    time_entry_factory(
        user=member,
        project=project,
        work_date=date(2026, 4, 15),
        duration_minutes=90,
        description="W1-B",
    )

    response = client.get(
        f"/time-entries/project/{project.id}/aggregation",
        query_string={"user_id": str(owner.id), "period": "week"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["total_minutes"] == 150
    assert body["data"][0]["period"] == "week"


def test_get_project_member_time_aggregation_month_returns_200(
    client, time_entry_factory, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="route-aggregation-owner-month@test.com")
    member = user_factory(email="route-aggregation-member-month@test.com")
    project = project_factory(owner=owner)
    project_member_factory(project=project, user=member)

    time_entry_factory(
        user=member,
        project=project,
        work_date=date(2026, 4, 10),
        duration_minutes=50,
        description="APR",
    )
    time_entry_factory(
        user=member,
        project=project,
        work_date=date(2026, 5, 5),
        duration_minutes=70,
        description="MAY",
    )

    response = client.get(
        f"/time-entries/project/{project.id}/aggregation",
        query_string={"user_id": str(owner.id), "period": "month"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    assert {item["period_start"] for item in body["data"]} == {"2026-04-01", "2026-05-01"}


def test_get_project_member_time_aggregation_denies_non_owner(
    client, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="route-aggregation-owner-deny@test.com")
    member = user_factory(email="route-aggregation-member-deny@test.com")
    project = project_factory(owner=owner)
    project_member_factory(project=project, user=member)

    response = client.get(
        f"/time-entries/project/{project.id}/aggregation",
        query_string={"user_id": str(member.id), "period": "week"},
    )

    assert response.status_code == 403
    body = response.get_json()
    assert body["success"] is False
    assert "owner" in body["error"]["message"].lower()


def test_get_project_member_time_aggregation_excludes_deleted(
    client, time_entry_factory, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="route-aggregation-owner-deleted@test.com")
    member = user_factory(email="route-aggregation-member-deleted@test.com")
    project = project_factory(owner=owner)
    project_member_factory(project=project, user=member)

    time_entry_factory(
        user=member,
        project=project,
        work_date=date(2026, 4, 14),
        duration_minutes=100,
        description="Active",
    )
    deleted = time_entry_factory(
        user=member,
        project=project,
        work_date=date(2026, 4, 15),
        duration_minutes=25,
        description="Deleted",
    )

    client.delete(f"/time-entries/{deleted.id}", json={"user_id": str(member.id)})

    response = client.get(
        f"/time-entries/project/{project.id}/aggregation",
        query_string={"user_id": str(owner.id), "period": "week"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["total_minutes"] == 100


def test_get_project_member_time_aggregation_returns_400_missing_period(
    client, user_factory, project_factory
):
    owner = user_factory(email="route-aggregation-owner-missing-period@test.com")
    project = project_factory(owner=owner)

    response = client.get(
        f"/time-entries/project/{project.id}/aggregation",
        query_string={"user_id": str(owner.id)},
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert "period" in body["error"]["message"].lower()


def test_get_project_member_time_aggregation_returns_400_invalid_period(
    client, user_factory, project_factory
):
    owner = user_factory(email="route-aggregation-owner-invalid-period@test.com")
    project = project_factory(owner=owner)

    response = client.get(
        f"/time-entries/project/{project.id}/aggregation",
        query_string={"user_id": str(owner.id), "period": "year"},
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert "expected 'week' or 'month'" in body["error"]["message"].lower()


def test_get_time_entry_summary_returns_200_with_expected_metrics(
    client, time_entry_factory, user_factory, project_factory
):
    user = user_factory(email="route-summary-user@test.com")
    project = project_factory(owner=user)
    today = date.today()

    time_entry_factory(
        user=user,
        project=project,
        description="Today entry",
        work_date=today,
        duration_minutes=120,
    )
    time_entry_factory(
        user=user,
        project=project,
        description="Month entry",
        work_date=today.replace(day=1),
        duration_minutes=30,
    )

    response = client.get(
        "/time-entries/summary",
        query_string={"user_id": str(user.id), "project_id": str(project.id)},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["total_entries"] == 2
    assert body["data"]["total_minutes"] == 150
    assert body["data"]["entries_today"] == 1
    assert body["data"]["minutes_today"] == 120
    assert body["data"]["hours_today"] == 2.0


def test_get_time_entry_summary_updates_with_filters(
    client, time_entry_factory, user_factory, project_factory
):
    user = user_factory(email="route-summary-filter-user@test.com")
    project = project_factory(owner=user)

    time_entry_factory(
        user=user,
        project=project,
        description="Dashboard fix",
        work_date=date.today(),
        duration_minutes=90,
    )
    time_entry_factory(
        user=user,
        project=project,
        description="Other task",
        work_date=date.today(),
        duration_minutes=40,
    )

    all_response = client.get(
        "/time-entries/summary",
        query_string={"user_id": str(user.id), "project_id": str(project.id)},
    )
    filtered_response = client.get(
        "/time-entries/summary",
        query_string={
            "user_id": str(user.id),
            "project_id": str(project.id),
            "search": "dashboard",
        },
    )

    assert all_response.status_code == 200
    assert filtered_response.status_code == 200
    all_data = all_response.get_json()["data"]
    filtered_data = filtered_response.get_json()["data"]

    assert all_data["total_entries"] == 2
    assert filtered_data["total_entries"] == 1
    assert all_data["total_minutes"] == 130
    assert filtered_data["total_minutes"] == 90


def test_get_time_entry_summary_excludes_deleted_entries(
    client, time_entry_factory, user_factory, project_factory
):
    user = user_factory(email="route-summary-deleted-user@test.com")
    project = project_factory(owner=user)

    time_entry_factory(
        user=user,
        project=project,
        description="Active",
        work_date=date.today(),
        duration_minutes=30,
    )
    deleted = time_entry_factory(
        user=user,
        project=project,
        description="Deleted",
        work_date=date.today(),
        duration_minutes=60,
    )
    client.delete(f"/time-entries/{deleted.id}", json={"user_id": str(user.id)})

    response = client.get(
        "/time-entries/summary",
        query_string={"user_id": str(user.id), "project_id": str(project.id)},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["total_entries"] == 1
    assert body["data"]["total_minutes"] == 30


def test_get_dashboard_activity_returns_200_for_7d(
    client, time_entry_factory, user_factory, project_factory
):
    user = user_factory(email="route-dashboard-7d@test.com", password="password123")
    project = project_factory(owner=user)

    time_entry_factory(user=user, project=project, work_date=date.today(), duration_minutes=120)
    time_entry_factory(
        user=user,
        project=project,
        work_date=date.today() - timedelta(days=6),
        duration_minutes=60,
    )

    access_token = _login_and_get_access_token(client, email=user.email)

    response = client.get(
        "/time-entries/dashboard/activity",
        query_string={"period": "7d"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["period"] == "7d"
    assert len(body["data"]["points"]) == 7
    assert body["data"]["total_minutes"] == 180


def test_get_dashboard_activity_returns_200_for_30d(
    client, time_entry_factory, user_factory, project_factory
):
    user = user_factory(email="route-dashboard-30d@test.com", password="password123")
    project = project_factory(owner=user)

    time_entry_factory(
        user=user,
        project=project,
        work_date=date.today() - timedelta(days=29),
        duration_minutes=30,
    )

    access_token = _login_and_get_access_token(client, email=user.email)

    response = client.get(
        "/time-entries/dashboard/activity",
        query_string={"period": "30d"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["period"] == "30d"
    assert len(body["data"]["points"]) == 30


def test_get_dashboard_activity_uses_authenticated_user_entries_only(
    client, time_entry_factory, user_factory, project_factory
):
    user_a = user_factory(email="route-dashboard-user-a@test.com", password="password123")
    user_b = user_factory(email="route-dashboard-user-b@test.com", password="password123")
    project_a = project_factory(owner=user_a)
    project_b = project_factory(owner=user_b)

    time_entry_factory(user=user_a, project=project_a, work_date=date.today(), duration_minutes=50)
    time_entry_factory(user=user_b, project=project_b, work_date=date.today(), duration_minutes=200)

    access_token = _login_and_get_access_token(client, email=user_a.email)

    response = client.get(
        "/time-entries/dashboard/activity",
        query_string={"period": "7d"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["total_minutes"] == 50


def test_get_dashboard_activity_excludes_deleted_entries(
    client, time_entry_factory, user_factory, project_factory
):
    user = user_factory(email="route-dashboard-deleted@test.com", password="password123")
    project = project_factory(owner=user)

    time_entry_factory(user=user, project=project, work_date=date.today(), duration_minutes=30)
    deleted = time_entry_factory(
        user=user, project=project, work_date=date.today(), duration_minutes=70
    )
    client.delete(f"/time-entries/{deleted.id}", json={"user_id": str(user.id)})

    access_token = _login_and_get_access_token(client, email=user.email)

    response = client.get(
        "/time-entries/dashboard/activity",
        query_string={"period": "7d"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["total_minutes"] == 30


def test_get_dashboard_activity_returns_401_without_token(client):
    response = client.get(
        "/time-entries/dashboard/activity",
        query_string={"period": "7d"},
    )

    assert response.status_code == 401
