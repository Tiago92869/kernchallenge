from datetime import date, datetime
from uuid import UUID

from app.api.errors import NotFoundError
from app.models.notification import Notification, NotificationType
from app.repositories.notification_repository import NotificationRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository


class NotificationService:
    @staticmethod
    def _ensure_user_exists(user_id: UUID) -> None:
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise NotFoundError(message="User not found")

    @staticmethod
    def _ensure_project_exists(project_id: UUID) -> None:
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            raise NotFoundError(message="Project not found")

    @staticmethod
    def create_notification(
        *,
        recipient_user_id: UUID,
        actor_user_id: UUID,
        project_id: UUID,
        notification_type: NotificationType,
        message: str,
    ) -> Notification:
        NotificationService._ensure_user_exists(recipient_user_id)
        NotificationService._ensure_user_exists(actor_user_id)
        NotificationService._ensure_project_exists(project_id)

        notification = Notification(
            recipient_user_id=recipient_user_id,
            actor_user_id=actor_user_id,
            project_id=project_id,
            notification_type=notification_type,
            message=message,
        )

        return NotificationRepository.save(notification)

    @staticmethod
    def get_notifications_by_recipient(
        *,
        recipient_user_id: UUID,
        search: str | None = None,
        created_date: date | None = None,
        project_id: UUID | None = None,
    ) -> list[Notification]:
        NotificationService._ensure_user_exists(recipient_user_id)

        if project_id:
            NotificationService._ensure_project_exists(project_id)

        return NotificationRepository.get_all_by_recipient(
            recipient_user_id=recipient_user_id,
            search=(search or "").strip(),
            created_date=created_date,
            project_id=project_id,
        )

    @staticmethod
    def mark_notification_as_read(notification_id: UUID) -> Notification:
        notification = NotificationRepository.get_by_id(notification_id)

        if not notification:
            raise NotFoundError(message="Notification not found")

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now()
            notification = NotificationRepository.save(notification)

        return notification

    @staticmethod
    def mark_all_notifications_as_read(recipient_user_id: UUID) -> None:
        NotificationService._ensure_user_exists(recipient_user_id)
        NotificationRepository.mark_all_as_read(
            recipient_user_id=recipient_user_id,
            read_at=datetime.now(),
        )
