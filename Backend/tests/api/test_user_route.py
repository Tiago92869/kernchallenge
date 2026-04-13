def test_create_user_returns_201(client):

    response = client.post(
        "/users",
        json={
            "email": "tiago@gmail.com",
            "firstname": "  Tiago ",
            "lastname": "  Martins  ",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["email"] == "tiago@gmail.com"
    assert body["data"]["firstname"] == "Tiago"
    assert body["data"]["lastname"] == "Martins"
    assert body["data"]["is_active"] is True


def test_create_user_return_400_email_already_exists(client, user_factory):
    user_db = user_factory()

    response = client.post(
        "/users",
        json={
            "email": user_db.email,
            "firstname": "  Tiago ",
            "lastname": "  Martins  ",
            "password": "password123",
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Email already exists"


def test_create_user_return_400_invalid_email_format(client):

    response = client.post(
        "/users",
        json={
            "email": "invalidemail",
            "firstname": "  Tiago ",
            "lastname": "  Martins  ",
            "password": "password123",
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid email format"


def test_update_user_200(client, user_factory):
    user_db = user_factory()

    response = client.put(
        f"/users/{user_db.id}",
        json={
            "email": "tiago@gmail.com",
            "firstname": "Pedro",
            "lastname": "Jonas",
        },
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["email"] == "tiago@gmail.com"
    assert body["data"]["firstname"] == "Pedro"
    assert body["data"]["lastname"] == "Jonas"


def test_update_user_400_invalid_Email(client, user_factory):
    user_db = user_factory()

    response = client.put(
        f"/users/{user_db.id}",
        json={
            "email": "invalidformat",
            "firstname": "Pedro",
            "lastname": "Jonas",
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid email format"


def test_update_user_400_duplicated_email(client, user_factory):
    user_db = user_factory()

    response = client.put(
        f"/users/{user_db.id}",
        json={
            "email": "tiagomartins123@gmail.com",
            "firstname": "Pedro",
            "lastname": "Jonas",
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Email already exists"


def test_update_user_404_user_not_found(client, user_factory):
    user_factory()

    response = client.put(
        "/users/00000000-0000-0000-0000-000000000000",
        json={
            "email": "tiagomartins123@gmail.com",
            "firstname": "Pedro",
            "lastname": "Jonas",
        },
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "User not found"


def test_get_user_by_id_200(client, user_factory):
    user_db = user_factory()

    response = client.get(f"/users/{user_db.id}")

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["email"] == user_db.email
    assert body["data"]["firstname"] == user_db.first_name
    assert body["data"]["lastname"] == user_db.last_name


def test_get_user_by_id_404_user_not_found(client):

    response = client.get("/users/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "User not found"


def test_update_password_200(client, user_factory):
    user_db = user_factory()

    response = client.put(
        f"/users/password/{user_db.id}",
        json={"old_password": "password123", "new_password": "newpassword123"},
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True


def test_update_password_user_not_found(client, user_factory):
    user_factory()

    response = client.put(
        "/users/password/00000000-0000-0000-0000-000000000000",
        json={"old_password": "password123", "new_password": "newpassword123"},
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "User not found"


def test_update_password_empty_password(client, user_factory):
    user_db = user_factory()

    response = client.put(
        f"/users/password/{user_db.id}", json={"old_password": "password123", "new_password": ""}
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "New password cannot be empty"


def test_update_password_current_password_same_as_new_password(client, user_factory):
    user_db = user_factory()

    response = client.put(
        f"/users/password/{user_db.id}",
        json={"old_password": "password123", "new_password": "password123"},
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "New password cannot be the same as the current password"


def test_update_password_incorrect_old_password(client, user_factory):
    user_db = user_factory()

    response = client.put(
        f"/users/password/{user_db.id}",
        json={"old_password": "incorrectpassword", "new_password": "newpassword123"},
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Incorrect old password"


def test_get_all_users_with_search_success(client, multiple_users_factory):
    multiple_users_factory()

    response = client.get("/users?search=Smith")

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["email"] == "user0@test.com"
    assert body["data"][0]["firstname"] == "Alice"
    assert body["data"][0]["lastname"] == "Smith"


def test_get_all_users_with_search_no_results(client, multiple_users_factory):
    multiple_users_factory()

    response = client.get("/users?search=nonexistent")

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 0


def test_get_all_users_with_search_empty_search(client, multiple_users_factory):
    multiple_users_factory()

    response = client.get("/users?search=")

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 5


def test_get_all_users_without_search_with_is_active_true_filter(client, multiple_users_factory):
    multiple_users_factory()

    response = client.get("/users?search=&is_active=true")

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 3


def test_get_all_users_without_search_with_is_active_false_filter(client, multiple_users_factory):
    multiple_users_factory()

    response = client.get("/users?search=&is_active=false")

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 2


def test_get_all_users_with_search_with_is_active_false_filter(client, multiple_users_factory):
    multiple_users_factory()

    response = client.get("/users?search=Charlie&is_active=false")

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 1


def test_login_200_success(client, user_factory):
    user_db = user_factory(email="login@test.com", password="password123", is_active=True)

    response = client.get(
        "/users/login",
        json={
            "email": user_db.email,
            "password": "password123",
        },
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["id"] == str(user_db.id)
    assert body["data"]["email"] == user_db.email


def test_login_400_email_not_found(client, user_factory):
    user_factory(email="known@test.com", password="password123", is_active=True)

    response = client.get(
        "/users/login",
        json={
            "email": "unknown@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid email or password"


def test_login_400_wrong_password(client, user_factory):
    user_factory(email="login@test.com", password="password123", is_active=True)

    response = client.get(
        "/users/login",
        json={
            "email": "login@test.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid email or password"


def test_login_400_inactive_user(client, user_factory):
    user_factory(email="inactive@test.com", password="password123", is_active=False)

    response = client.get(
        "/users/login",
        json={
            "email": "inactive@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Account is inactive"


def test_login_400_empty_payload(client):
    response = client.get("/users/login", json={})

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid email or password"


def test_get_all_users_without_search_with_is_active_empty_filter(client, multiple_users_factory):
    multiple_users_factory()

    response = client.get("/users?search=&is_active=")

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert len(body["data"]) == 5


def test_get_all_users_with_search_with_is_active_invalid_filter(client, multiple_users_factory):
    multiple_users_factory()

    response = client.get("/users?search=&is_active=asd")

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid is_active filter"
