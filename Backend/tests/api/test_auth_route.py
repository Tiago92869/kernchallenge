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


def test_forgot_password_200_success(client, user_factory, monkeypatch):
    user_factory(email="forgot@test.com", password="password123", is_active=True)

    monkeypatch.setattr(
        "app.services.user_service.EmailService.send_password_reset_email",
        lambda **kwargs: None,
    )

    response = client.post(
        "/auth/forgot-password",
        json={"email": "forgot@test.com"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["message"] == "A new password was sent to your email"


def test_forgot_password_400_invalid_email(client):
    response = client.post(
        "/auth/forgot-password",
        json={"email": "invalid-email"},
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid email format"


def test_forgot_password_404_user_not_found(client):
    response = client.post(
        "/auth/forgot-password",
        json={"email": "missing@test.com"},
    )

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "User not found"
