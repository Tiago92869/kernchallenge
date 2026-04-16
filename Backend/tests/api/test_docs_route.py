def test_swagger_ui_is_available(client):
    response = client.get("/docs/")

    assert response.status_code == 200
