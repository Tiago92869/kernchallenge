from datetime import datetime

from app.models.notification import Notification, NotificationType
from app.models.project_member import ProjectMember


def _login_and_get_access_token(client, email, password="password123"):
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.get_json()["data"]["auth_token"]


def test_get_currently_active_members_returns_200_with_expected_body(
    client, project_factory, user_factory, project_member_factory
):
    owner = user_factory(email="route-active-members-owner@test.com")
    project = project_factory(owner=owner)
    active_user = user_factory(
        email="route-active-member@test.com", first_name="Active", last_name="Member"
    )
    inactive_user = user_factory(
        email="route-inactive-member@test.com",
        first_name="Inactive",
        last_name="Member",
        is_active=False,
    )
    removed_user = user_factory(
        email="route-removed-member@test.com", first_name="Removed", last_name="Member"
    )

    project_member_factory(project=project, user=active_user)
    project_member_factory(project=project, user=inactive_user)
    project_member_factory(project=project, user=removed_user, removed_at=datetime.now())

    access_token = _login_and_get_access_token(client, email=owner.email)
    response = client.get(
        f"/project-members/{project.id}/active",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["data"] == [
        {
            "id": str(active_user.id),
            "firstname": "Active",
            "lastname": "Member",
        }
    ]


def test_get_currently_active_members_returns_empty_list_when_no_active_members(
    client, project_factory, user_factory, project_member_factory
):
    owner = user_factory(email="route-empty-active-members-owner@test.com")
    project = project_factory(owner=owner)
    removed_user = user_factory(
        email="route-only-removed-member@test.com", first_name="Removed", last_name="Only"
    )

    project_member_factory(project=project, user=removed_user, removed_at=datetime.now())

    access_token = _login_and_get_access_token(client, email=owner.email)
    response = client.get(
        f"/project-members/{project.id}/active",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["data"] == []


def test_get_currently_active_members_returns_404_when_project_is_archived(client, project_factory):
    project = project_factory(is_archived=True)
    access_token = _login_and_get_access_token(client, email=project.owner.email)

    response = client.get(
        f"/project-members/{project.id}/active",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Project not found or is archived"


def test_get_currently_active_members_returns_404_when_project_is_missing(client, user_factory):
    missing_project_id = "550e8400-e29b-41d4-a716-446655440000"
    owner = user_factory(email="route-missing-project-owner@test.com")
    access_token = _login_and_get_access_token(client, email=owner.email)

    response = client.get(
        f"/project-members/{missing_project_id}/active",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Project not found or is archived"


def test_add_project_members_returns_200(client, project_factory, user_factory):
    owner = user_factory(
        email="route-project-owner-one@test.com", first_name="Route", last_name="Owner"
    )
    project = project_factory(owner=owner, name="Route Team")
    user_one = user_factory(email="route-add-member-one@test.com")
    user_two = user_factory(email="route-add-member-two@test.com")

    access_token = _login_and_get_access_token(client, email=owner.email)
    response = client.put(
        f"/project-members/{project.id}/add",
        json={"users_ids": [str(user_one.id), str(user_two.id)]},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["message"] == "Project members added successfully"

    project_members = ProjectMember.query.filter_by(project_id=project.id).all()
    assert len(project_members) == 2
    assert sorted(project_member.user_id for project_member in project_members) == sorted(
        [user_one.id, user_two.id]
    )

    notifications = Notification.query.filter_by(project_id=project.id).all()
    assert len(notifications) == 2
    assert all(
        notification.notification_type == NotificationType.ADDED for notification in notifications
    )
    assert all(
        notification.message == '"Route Owner" just added you to "Route Team"'
        for notification in notifications
    )


def test_add_project_members_reactivates_removed_membership(
    client, project_factory, user_factory, project_member_factory
):
    owner = user_factory(email="route-reactivate-member-owner@test.com")
    project = project_factory(owner=owner)
    user = user_factory(email="route-reactivate-member@test.com")
    project_member = project_member_factory(
        project=project, user=user, removed_at=__import__("datetime").datetime.now()
    )

    access_token = _login_and_get_access_token(client, email=owner.email)
    response = client.put(
        f"/project-members/{project.id}/add",
        json={"users_ids": [str(user.id)]},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    refreshed_project_member = ProjectMember.query.filter_by(id=project_member.id).first()
    assert refreshed_project_member.removed_at is None
    assert refreshed_project_member.removed_by_user_id is None


def test_add_project_members_returns_404_when_project_is_archived(
    client, project_factory, user_factory
):
    owner = user_factory(email="route-add-archived-owner@test.com")
    project = project_factory(owner=owner, is_archived=True)
    user = user_factory(email="route-add-archived-project@test.com")
    access_token = _login_and_get_access_token(client, email=owner.email)

    response = client.put(
        f"/project-members/{project.id}/add",
        json={"users_ids": [str(user.id)]},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Project not found or is archived"


def test_add_project_members_returns_404_when_user_is_inactive(
    client, project_factory, user_factory
):
    owner = user_factory(email="route-add-inactive-owner@test.com")
    project = project_factory(owner=owner)
    user = user_factory(email="route-add-inactive-user@test.com", is_active=False)
    access_token = _login_and_get_access_token(client, email=owner.email)

    response = client.put(
        f"/project-members/{project.id}/add",
        json={"users_ids": [str(user.id)]},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == f"User with id {user.id} not found or is not active"


def test_add_project_members_returns_404_when_user_is_missing(client, project_factory):
    project = project_factory()
    missing_user_id = "5540e840-e29b-41d4-a716-446655440000"
    access_token = _login_and_get_access_token(client, email=project.owner.email)

    response = client.put(
        f"/project-members/{project.id}/add",
        json={"users_ids": [missing_user_id]},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == f"User with id {missing_user_id} not found or is not active"


def test_remove_project_member_returns_200(
    client, project_factory, user_factory, project_member_factory
):
    owner = user_factory(
        email="route-project-owner-two@test.com", first_name="Route", last_name="Lead"
    )
    project = project_factory(owner=owner, name="Route Ops")
    user = user_factory(email="route-remove-member@test.com")
    project_member = project_member_factory(project=project, user=user)

    access_token = _login_and_get_access_token(client, email=owner.email)
    response = client.put(
        f"/project-members/{project.id}/{user.id}/remove",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["message"] == "Project member removed successfully"

    refreshed_project_member = ProjectMember.query.filter_by(id=project_member.id).first()
    assert refreshed_project_member.removed_at is not None
    assert refreshed_project_member.removed_by_user_id is None

    notification = Notification.query.filter_by(
        project_id=project.id, recipient_user_id=user.id
    ).first()
    assert notification is not None
    assert notification.notification_type == NotificationType.REMOVED
    assert notification.message.startswith('"Route Lead" just removed you from "Route Ops" at "')


def test_remove_project_member_returns_404_when_membership_not_found(
    client, project_factory, user_factory
):
    owner = user_factory(email="route-remove-missing-membership-owner@test.com")
    project = project_factory(owner=owner)
    user = user_factory(email="route-missing-membership@test.com")
    access_token = _login_and_get_access_token(client, email=owner.email)

    response = client.put(
        f"/project-members/{project.id}/{user.id}/remove",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Project member not found"


def test_remove_project_member_returns_404_when_project_is_archived(
    client, project_factory, user_factory, project_member_factory
):
    owner = user_factory(email="route-remove-archived-owner@test.com")
    project = project_factory(owner=owner, is_archived=True)
    user = user_factory(email="route-archived-project-member@test.com")
    project_member_factory(project=project, user=user)
    access_token = _login_and_get_access_token(client, email=owner.email)

    response = client.put(
        f"/project-members/{project.id}/{user.id}/remove",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Project not found or is archived"


def test_remove_project_member_returns_404_when_user_is_inactive(
    client, project_factory, user_factory
):
    owner = user_factory(email="route-remove-inactive-owner@test.com")
    project = project_factory(owner=owner)
    user = user_factory(email="route-inactive-remove-member@test.com", is_active=False)
    access_token = _login_and_get_access_token(client, email=owner.email)

    response = client.put(
        f"/project-members/{project.id}/{user.id}/remove",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == f"User with id {user.id} not found or is not active"


def test_remove_project_member_returns_404_when_user_is_missing(client, project_factory):
    project = project_factory()
    missing_user_id = "5540e840-e29b-41d4-a716-446655440000"
    access_token = _login_and_get_access_token(client, email=project.owner.email)

    response = client.put(
        f"/project-members/{project.id}/{missing_user_id}/remove",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == f"User with id {missing_user_id} not found or is not active"


def test_add_project_members_returns_403_when_user_is_not_owner(
    client, project_factory, user_factory
):
    owner = user_factory(email="route-non-owner-add-owner@test.com")
    actor = user_factory(email="route-non-owner-add-actor@test.com")
    project = project_factory(owner=owner)
    user = user_factory(email="route-non-owner-add-member@test.com")
    access_token = _login_and_get_access_token(client, email=actor.email)

    response = client.put(
        f"/project-members/{project.id}/add",
        json={"users_ids": [str(user.id)]},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "User is not the project owner"


def test_remove_project_member_returns_403_when_user_is_not_owner(
    client, project_factory, user_factory, project_member_factory
):
    owner = user_factory(email="route-non-owner-remove-owner@test.com")
    actor = user_factory(email="route-non-owner-remove-actor@test.com")
    project = project_factory(owner=owner)
    member = user_factory(email="route-non-owner-remove-member@test.com")
    project_member_factory(project=project, user=member)
    access_token = _login_and_get_access_token(client, email=actor.email)

    response = client.put(
        f"/project-members/{project.id}/{member.id}/remove",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 403
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "User is not the project owner"


def test_project_members_routes_return_401_without_token(client, project_factory, user_factory):
    project = project_factory()
    user = user_factory(email="route-members-unauthorized@test.com")

    get_response = client.get(f"/project-members/{project.id}/active")
    add_response = client.put(
        f"/project-members/{project.id}/add",
        json={"users_ids": [str(user.id)]},
    )
    remove_response = client.put(f"/project-members/{project.id}/{user.id}/remove")

    assert get_response.status_code == 401
    assert add_response.status_code == 401
    assert remove_response.status_code == 401
