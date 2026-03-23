import pytest

from uuid import UUID
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

def test_crete_user_failed_invalid_email_format():

    with pytest.raises(ValidationError) as exc_info:
        UserService.create_user(
            email = "invalidemail",
            firstname = " Tiago ",
            lastname = " Martins ",
            password = "password123",            
        )
    
    assert exc_info.value.message == "Invalid email format"

