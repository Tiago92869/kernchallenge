from uuid import UUID

from app.api.errors import NotFoundError, ValidationError
from app.models.user import User
from app.repositories.user_repository import UserRepository

class UserService:
    @staticmethod
    def _normalize_is_active_filter(is_active: bool | str | None) -> bool | None:
        if is_active is None or is_active == "":
            return None

        if isinstance(is_active, bool):
            return is_active

        if isinstance(is_active, str):
            normalized = is_active.strip().lower()
            if normalized == "true":
                return True
            if normalized == "false":
                return False

        raise ValidationError(message="Invalid is_active filter")

    @staticmethod
    def create_user(
        *,
        email: str,
        firstname: str,
        lastname: str,
        password: str,
    ) -> User:

        normalized_email = email.strip()
        normalized_firstname = firstname.strip()
        normalized_lastname = lastname.strip()
        
        if not UserService.check_email_format(normalized_email):
            raise ValidationError(message="Invalid email format")

        if UserService.check_email_exists(normalized_email):
            raise ValidationError(message="Email already exists")

        # encrypt the password
        user = User(
            email = normalized_email,
            first_name = normalized_firstname,
            last_name = normalized_lastname,
        )
        user.set_password(password)
        
        return UserRepository.save(user)

    @staticmethod
    def check_email_exists(email: str) -> bool:
        existing_user = UserRepository.get_by_email(email)
        return existing_user is not None
    
    @staticmethod
    def check_email_format(email: str) -> bool:
        # Basic email format validation
        if "@" not in email or "." not in email:
            return False
        return True
        
    @staticmethod
    def update_user(
        *,
        user_id: UUID,
        email: str,
        firstname: str,
        lastname: str, 
    ) -> User:
        
        normalized_email = email.strip()
        normalized_firstname = firstname.strip()
        normalized_lastname = lastname.strip()

        user = UserRepository.get_by_id(user_id)

        if not user:
            raise NotFoundError(message = "User not found")

        if not UserService.check_email_format(normalized_email):
            raise ValidationError(message = "Invalid email format")

        if UserService.check_email_exists(normalized_email):
            raise ValidationError(message="Email already exists")
        
        user.email = normalized_email
        user.first_name = normalized_firstname
        user.last_name = normalized_lastname

        return UserRepository.save(user)

    @staticmethod
    def get_user_by_id(
        user_id: UUID
    ) -> User:
    
        user = UserRepository.get_by_id(user_id)

        if not user:
            raise NotFoundError(message = "User not found")
        else:
            return user

    @staticmethod
    def update_password(
        *,
        user_id: UUID,
        old_password: str,
        new_password: str
    ) -> None:
        user = UserRepository.get_by_id(user_id)

        if not user:
            raise NotFoundError(message = "User not found")
        
        if not user.check_password(old_password):
            raise ValidationError(message = "Incorrect old password")

        if not new_password:
            raise ValidationError(message = "New password cannot be empty")

        if old_password == new_password:
            raise ValidationError(message = "New password cannot be the same as the current password")

        user.set_password(new_password)
        UserRepository.save(user)

    @staticmethod
    def get_all_users(*, search: str | None = None, is_active: bool | str | None = None) -> list[User]:
        normalized_search = (search or "").strip()
        normalized_is_active = UserService._normalize_is_active_filter(is_active)

        return UserRepository.get_all(
            normalized_search,
            normalized_is_active,
        )