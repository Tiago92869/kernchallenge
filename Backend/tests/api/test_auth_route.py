def test_logout_200_success(client, user_factory):
    user_factory(email="logout@test.com", password="password123", is_active=True)

    login_response = client.post(
        "/auth/login",
        json={
            "email": "logout@test.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200
    access_token = login_response.get_json()["data"]["auth_token"]

    response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["message"] == "Logged out successfully"


def test_signout_200_success_alias(client, user_factory):
    user_factory(email="signout@test.com", password="password123", is_active=True)

    login_response = client.post(
        "/auth/login",
        json={
            "email": "signout@test.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200
    access_token = login_response.get_json()["data"]["auth_token"]

    response = client.post(
        "/auth/signout",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["message"] == "Logged out successfully"


def test_logout_401_without_token(client):
    response = client.post("/auth/logout")

    assert response.status_code == 401


def test_logout_401_with_revoked_token(client, user_factory):
    user_factory(email="revoked@test.com", password="password123", is_active=True)

    login_response = client.post(
        "/auth/login",
        json={
            "email": "revoked@test.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200
    access_token = login_response.get_json()["data"]["auth_token"]

    first_logout = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert first_logout.status_code == 200

    second_logout = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert second_logout.status_code == 401
