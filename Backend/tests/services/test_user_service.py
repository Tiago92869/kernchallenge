import pytest

from uuid import UUID
from tests.conftest import user_factory
from app.api.errors import NotFoundError, ValidationError
from app.services.user_service import UserService

def test_create_user_sucess(app):
    with app.app_context():
        user = UserService.create_user(
            email = "tiago@gmail.com",
            firstname = " Tiago ",
            lastname = " Martins ",
            password = "password123",
        )

        assert user.id is not None
        assert user.email == "tiago@gmail.com"
        assert user.first_name == "Tiago"
        assert user.last_name == "Martins"
        assert user.password_hash is not None
    assert user.is_active is True

def test_create_user_failed_duplicated_email(user_factory):
    user_db = user_factory()

    with pytest.raises(ValidationError) as exc_info:
        UserService.create_user(
            email = user_db.email,
            firstname = " Tiago ",
            lastname = " Martins ",
            password = "password123",            
        )
    
    assert exc_info.value.message == "Email already exists"

def test_create_user_failed_invalid_email_format():

    with pytest.raises(ValidationError) as exc_info:
        UserService.create_user(
            email = "invalidemail",
            firstname = " Tiago ",
            lastname = " Martins ",
            password = "password123",            
        )
    
    assert exc_info.value.message == "Invalid email format"

def test_update_user_sucess(user_factory):
    user_db = user_factory()

    user = UserService.update_user(
        user_id = user_db.id,
        email = "tiago@gmail.com",
        firstname = "Pedro",
        lastname = "Jonas"
    )

    assert user.id == user_db.id
    assert user.email == "tiago@gmail.com"
    assert user.first_name == "Pedro"
    assert user.last_name == "Jonas"

def test_update_user_email_already_exists(user_factory):
    user_db = user_factory()

    with pytest.raises(ValidationError) as exc_info:
        UserService.update_user(
            user_id = user_db.id,
            email = "tiagomartins123@gmail.com",
            firstname = "Pedro",
            lastname = "Jonas"
        )

    assert exc_info.value.message == "Email already exists"

def test_update_user_wrong_email_format(user_factory):
    user_db = user_factory()

    with pytest.raises(ValidationError) as exc_info:
        UserService.update_user(
            user_id = user_db.id,
            email = "invalidemail",
            firstname = "Pedro",
            lastname = "Jonas"
        )

    assert exc_info.value.message == "Invalid email format"

def test_update_user_not_found(user_factory):
    user_factory()

    with pytest.raises(NotFoundError) as exc_info:
        UserService.update_user(
            user_id = UUID("5540e840-e29b-41d4-a716-446655440000"),
            email = "tiagomartins123321@gmail.com",
            firstname = "Pedro",
            lastname = "Jonas"
        )

    assert exc_info.value.message == "User not found"

def test_get_user_by_id_sucess(client, user_factory):
    user_db = user_factory()

    user = UserService.get_user_by_id(user_db.id)

    assert user.id == user_db.id
    assert user.email == user_db.email
    assert user.first_name == user_db.first_name
    assert user.last_name == user_db.last_name

def test_get_user_by_id_not_found(client, user_factory):
    user_factory()

    with pytest.raises(NotFoundError) as exc_info:
        UserService.get_user_by_id(UUID("5540e840-e29b-41d4-a716-446655440000"))

    assert exc_info.value.message == "User not found"

def test_update_password_sucess(user_factory):
    user_db = user_factory()

    UserService.update_password(
        user_id = user_db.id,
        old_password = "password123",
        new_password = "newpassword123"
    )

    assert user_db.check_password("newpassword123") is True

def test_update_password_user_not_found(user_factory):
    user_factory()

    with pytest.raises(NotFoundError) as exc_info:
        UserService.update_password(
            user_id = UUID("5540e840-e29b-41d4-a716-446655440000"),
            old_password = "password123",
            new_password = "newpassword123"
        )

    assert exc_info.value.message == "User not found"

def test_update_password_empty_password(user_factory):
    user_db = user_factory()

    with pytest.raises(ValidationError) as exc_info:
        UserService.update_password(
            user_id = user_db.id,
            old_password = "password123",
            new_password = ""
        )

    assert exc_info.value.message == "New password cannot be empty"

def test_update_password_current_password_same_as_new_password(user_factory):
    user_db = user_factory()

    with pytest.raises(ValidationError) as exc_info:
        UserService.update_password(
            user_id = user_db.id,
            old_password = "password123",
            new_password = "password123"
        )

    assert exc_info.value.message == "New password cannot be the same as the current password"

def test_update_password_incorrect_old_password(user_factory):
    user_db = user_factory()

    with pytest.raises(ValidationError) as exc_info:
        UserService.update_password(
            user_id = user_db.id,
            old_password = "wrongpassword",
            new_password = "newpassword123"
        )

    assert exc_info.value.message == "Incorrect old password"

def test_get_all_users_with_search_success(client, multiple_users_factory):
    multiple_users_factory()

    users = UserService.get_all_users(search="Smith")

    assert len(users) == 1
    assert users[0].email == "user0@test.com"
    assert users[0].first_name == "Alice"
    assert users[0].last_name == "Smith"

def test_get_all_users_with_search_no_results(client, multiple_users_factory):
    multiple_users_factory()

    users = UserService.get_all_users(search="NonExistent")

    assert len(users) == 0

def test_get_all_users_with_search_empty_search(client, multiple_users_factory):
    multiple_users_factory()

    users = UserService.get_all_users()

    assert len(users) == 5

def test_get_all_users_without_search_with_is_active_true_filter(client, multiple_users_factory):
    multiple_users_factory()

    users = UserService.get_all_users(is_active=True)

    assert len(users) == 3
    for user in users:
        assert user.is_active is True

def test_get_all_users_without_search_with_is_active_false_filter(client, multiple_users_factory):
    multiple_users_factory()

    users = UserService.get_all_users(is_active=False)

    assert len(users) == 2
    for user in users:
        assert user.is_active is False

def test_get_all_users_without_search_with_is_active_false_filter(client, multiple_users_factory):
    multiple_users_factory()

    users = UserService.get_all_users(is_active=False)

    assert len(users) == 2
    for user in users:
        assert user.is_active is False

def test_get_all_users_with_search_with_is_active_false_filter(client, multiple_users_factory):
    multiple_users_factory()

    users = UserService.get_all_users(search="E", is_active=False)
    
    assert len(users) == 2
    for user in users:
        assert user.is_active is False

def test_get_all_users_with_search_with_is_active_invalid_filter(client, multiple_users_factory):
    multiple_users_factory()

    with pytest.raises(ValidationError) as exc_info:
        UserService.get_all_users(search="E", is_active="invalid")

    assert exc_info.value.message == "Invalid is_active filter"

def test_does_user_exist_and_active_returns_true(user_factory):
    user_db = user_factory(email="active-user@test.com", is_active=True)

    user_exists = UserService.does_user_exist_and_active(user_db.id)

    assert user_exists is True

def test_does_user_exist_and_active_returns_false_for_inactive_user(user_factory):
    user_db = user_factory(email="inactive-user@test.com", is_active=False)

    user_exists = UserService.does_user_exist_and_active(user_db.id)

    assert user_exists is False

def test_does_user_exist_and_active_returns_false_for_missing_user(app):
    with app.app_context():
        user_exists = UserService.does_user_exist_and_active(UUID("5540e840-e29b-41d4-a716-446655440000"))

    assert user_exists is False
