class NotificationSchema:
    @staticmethod
    def serialize_notification(notification):
        return {
            "id": str(notification.id),
            "recipient_user_id": str(notification.recipient_user_id),
            "actor_user_id": str(notification.actor_user_id),
            "project_id": str(notification.project_id),
            "notification_type": notification.notification_type.value,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
        }
