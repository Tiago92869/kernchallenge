from datetime import date, datetime, timedelta


def test_get_notifications_by_recipient_returns_200(client, notification_factory, user_factory, project_factory):
    owner = user_factory(email="route-notification-owner@test.com", first_name="Owner", last_name="One")
    recipient = user_factory(email="route-notification-recipient@test.com")
    project = project_factory(owner=owner)

    notification_factory(
        recipient_user=recipient,
        actor_user=owner,
        project=project,
        message='"Owner One" just added you to "TimeSync"',
    )

    response = client.get(
        "/notifications",
        query_string={
            "recipient_user_id": str(recipient.id),
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["recipient_user_id"] == str(recipient.id)


def test_get_notifications_by_recipient_returns_200_with_filters(client, notification_factory, user_factory, project_factory):
    owner = user_factory(email="route-notification-owner-filter@test.com", first_name="Owner", last_name="Two")
    recipient = user_factory(email="route-notification-recipient-filter@test.com")
    project = project_factory(owner=owner)

    notification_factory(
        recipient_user=recipient,
        actor_user=owner,
        project=project,
        message="search me",
        created_at=datetime.now() - timedelta(days=1),
    )
    notification_factory(
        recipient_user=recipient,
        actor_user=owner,
        project=project,
        message="do not search me",
        created_at=datetime.now(),
    )

    response = client.get(
        "/notifications",
        query_string={
            "recipient_user_id": str(recipient.id),
            "search": "do not",
            "date": date.today().isoformat(),
            "project_id": str(project.id),
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["message"] == "do not search me"


def test_get_notifications_by_recipient_returns_400_for_invalid_date(client, user_factory):
    recipient = user_factory(email="route-notification-invalid-date@test.com")

    response = client.get(
        "/notifications",
        query_string={
            "recipient_user_id": str(recipient.id),
            "date": "2026/03/25",
        },
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid date format, expected YYYY-MM-DD"


def test_get_notifications_by_recipient_returns_404_when_user_missing(client):
    response = client.get(
        "/notifications",
        query_string={
            "recipient_user_id": "550e8400-e29b-41d4-a716-446655440000",
        },
    )

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "User not found"


def test_get_notifications_by_recipient_returns_404_when_project_missing(client, user_factory):
    recipient = user_factory(email="route-notification-missing-project@test.com")

    response = client.get(
        "/notifications",
        query_string={
            "recipient_user_id": str(recipient.id),
            "project_id": "550e8400-e29b-41d4-a716-446655440001",
        },
    )

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Project not found"


def test_mark_notification_as_read_returns_200(client, notification_factory):
    notification = notification_factory(is_read=False)

    response = client.patch(f"/notifications/{notification.id}/read")

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["is_read"] is True
    assert body["data"]["read_at"] is not None


def test_mark_notification_as_read_returns_404_when_missing(client):
    response = client.patch("/notifications/550e8400-e29b-41d4-a716-446655440003/read")

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Notification not found"
