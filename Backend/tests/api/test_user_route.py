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

