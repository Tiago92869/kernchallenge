def test_create_project_returns_201(client, user_factory):
    owner = user_factory()

    response = client.post(
        "/projects",
        json={
            "owner_id": str(owner.id),
            "name": "TimeSync",
            "description": "Main project",
            "visibility": "PRIVATE",
        }
    )

    assert response.status_code == 201

    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["name"] == 'TimeSync'
    assert body["data"]["description"] == 'Main project'
    assert body["data"]["visibility"] == 'PRIVATE'
    assert body["data"]["owner_id"] == str(owner.id)
    assert body["data"]["is_archived"] is False

def test_create_project_returns_400_when_name_is_blank(client, user_factory):
    owner = user_factory()

    response = client.post(
        "/projects",
        json={
            "owner_id": str(owner.id),
            "name": "   ",
            "description": "Main project",
            "visibility": "PRIVATE",
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Project name is required"

def test_create_project_returns_400_when_visibility_is_invalid(client, user_factory):
    owner = user_factory()

    response = client.post(
            "/projects",
            json={
                "owner_id": str(owner.id),
                "name": "Project",
                "description": "Main project",
                "visibility": "INVALID",
            },
        )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid project visibility"

def test_update_project_success(client, project_factory):
    project = project_factory()

    response = client.put(
        f"/projects/{project.id}",
        json={
            "name": "Updated Project",
            "description": "Updated description",
            "visibility": "PUBLIC",
        },
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["name"] == 'Updated Project'
    assert body["data"]["description"] == 'Updated description'
    assert body["data"]["visibility"] == 'PUBLIC'
    assert body["data"]["is_archived"] is False

def test_update_project_returns_404_when_project_not_found(client, user_factory):
    owner = user_factory()

    response = client.put(
        "/projects/00000000-0000-0000-0000-000000000000",
        json={
            "name": "Updated Project",
            "description": "Updated description",
            "visibility": "PUBLIC",
        },
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Project not found"

def test_update_project_returns_400_when_visibility_is_invalid(client, project_factory):
    project = project_factory()

    response = client.put(
        f"/projects/{project.id}",
        json={
            "name": "Updated Project",
            "description": "Updated description",
            "visibility": "INVALID",
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid project visibility"


def test_change_project_archive_status_archives_returns_200(client, project_factory):
    project = project_factory(is_archived=False)

    response = client.patch(
        f"/projects/{project.id}/archive",
        json={
            "user_id": str(project.owner_id),
            "action": "archive",
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["is_archived"] is True


def test_change_project_archive_status_unarchives_returns_200(client, project_factory):
    project = project_factory(is_archived=True)

    response = client.patch(
        f"/projects/{project.id}/archive",
        json={
            "user_id": str(project.owner_id),
            "action": "unarchive",
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["is_archived"] is False


def test_change_project_archive_status_returns_404_when_project_not_found(client, user_factory):
    user = user_factory(email="archive-route-owner@test.com")

    response = client.patch(
        "/projects/00000000-0000-0000-0000-000000000000/archive",
        json={
            "user_id": str(user.id),
            "action": "archive",
        },
    )

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Project not found"


def test_change_project_archive_status_returns_403_when_user_not_owner(client, project_factory, user_factory):
    project = project_factory(is_archived=False)
    user = user_factory(email="archive-route-not-owner@test.com")

    response = client.patch(
        f"/projects/{project.id}/archive",
        json={
            "user_id": str(user.id),
            "action": "archive",
        },
    )

    assert response.status_code == 403
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "User is not the project owner"


def test_change_project_archive_status_returns_400_for_invalid_action(client, project_factory):
    project = project_factory(is_archived=False)

    response = client.patch(
        f"/projects/{project.id}/archive",
        json={
            "user_id": str(project.owner_id),
            "action": "invalid",
        },
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid action. Use 'archive' or 'unarchive'"


def test_change_project_archive_status_returns_400_for_same_state(client, project_factory):
    project = project_factory(is_archived=True)

    response = client.patch(
        f"/projects/{project.id}/archive",
        json={
            "user_id": str(project.owner_id),
            "action": "archive",
        },
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Project already in requested state"