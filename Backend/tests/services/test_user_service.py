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
    user = user_factory()

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
    user_db = user_factory()

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
    user_db = user_factory()

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