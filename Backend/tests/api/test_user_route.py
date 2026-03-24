def test_create_user_returns_201(client):

    response = client.post(
        "/users",
        json = {
            "email": "tiago@gmail.com",
            "firstname": "  Tiago ",
            "lastname": "  Martins  ",
            "password": "password123",   
        }
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
        json = {
            "email": user_db.email,
            "firstname": "  Tiago ",
            "lastname": "  Martins  ",
            "password": "password123",
        }
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Email already exists"

def test_create_user_return_400_invalid_email_format(client):

    response = client.post(
        "/users",
        json = {
            "email": "invalidemail",
            "firstname": "  Tiago ",
            "lastname": "  Martins  ",
            "password": "password123",
        }
    )

    assert response.status_code == 400  

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Invalid email format"

def test_update_user_200(client, user_factory):
    user_db = user_factory()

    response = client.put(
        f"/users/{user_db.id}",
        json = {
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
        json = {
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
        json = {
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
    user_db = user_factory()

    response = client.put(
        "/users/00000000-0000-0000-0000-000000000000",
        json = {
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
        json = {
            "old_password": "password123",
            "new_password": "newpassword123"
        }
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True

def test_update_password_user_not_found(client, user_factory):
    user_db = user_factory()

    response = client.put(
        "/users/password/00000000-0000-0000-0000-000000000000",
        json = {
            "old_password": "password123",
            "new_password": "newpassword123"
        }
    )

    assert response.status_code == 404

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "User not found"

def test_update_password_empty_password(client, user_factory):
    user_db = user_factory()

    response = client.put(
        f"/users/password/{user_db.id}",
        json = {
            "old_password": "password123",
            "new_password": ""
        }
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "New password cannot be empty"

def test_update_password_current_password_same_as_new_password(client, user_factory):
    user_db = user_factory()

    response = client.put(
        f"/users/password/{user_db.id}",
        json = {
            "old_password": "password123",
            "new_password": "password123"
        }
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "New password cannot be the same as the current password"

def test_update_password_incorrect_old_password(client, user_factory):
    user_db = user_factory()

    response = client.put(
        f"/users/password/{user_db.id}",
        json = {
            "old_password": "incorrectpassword",
            "new_password": "newpassword123"
        }
    )

    assert response.status_code == 400

    body = response.get_json()
    assert body["success"] is False
    assert body["error"]["message"] == "Incorrect old password"