from uuid import UUID
import secrets
import string

from app.api.errors import NotFoundError, ValidationError
from app.models.revoked_token import RevokedToken
from app.models.user import User
from app.repositories.revoked_token_repository import RevokedTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService

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
    
    @staticmethod
    def does_user_exist_and_active(user_id: UUID) -> bool:
        user = UserRepository.get_by_id(user_id)
        return user is not None and user.is_active is True

    @staticmethod
    def login(*, email: str, password: str) -> User:
        from datetime import datetime

        user = UserRepository.get_by_email(email.strip())

        if not user or not user.check_password(password):
            raise ValidationError(message="Invalid email or password")

        if not user.is_active:
            raise ValidationError(message="Account is inactive")

        user.last_login_at = datetime.now()
        UserRepository.save(user)

        return user

    @staticmethod
    def logout(*, jti: str) -> None:
        normalized_jti = (jti or "").strip()
        if not normalized_jti:
            raise ValidationError(message="Invalid token")

        if RevokedTokenRepository.exists_by_jti(normalized_jti):
            return

        RevokedTokenRepository.save(RevokedToken(jti=normalized_jti))

    @staticmethod
    def is_token_revoked(jti: str) -> bool:
        return RevokedTokenRepository.exists_by_jti(jti)

    @staticmethod
    def generate_temporary_password(length: int = 12) -> str:
        if length < 8:
            raise ValidationError(message="Temporary password length is too short")

        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def reset_forgotten_password(*, email: str) -> None:
        normalized_email = (email or "").strip()

        if not UserService.check_email_format(normalized_email):
            raise ValidationError(message="Invalid email format")

        user = UserRepository.get_by_email(normalized_email)
        if not user:
            raise NotFoundError(message="User not found")

        temporary_password = UserService.generate_temporary_password()
        user.set_password(temporary_password)
        UserRepository.save(user)

        EmailService.send_password_reset_email(
            to_email=user.email,
            temporary_password=temporary_password,
        )