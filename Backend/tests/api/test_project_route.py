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