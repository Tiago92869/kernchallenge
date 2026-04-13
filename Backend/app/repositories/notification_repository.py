from datetime import date

from app.extensions import db
from app.models.notification import Notification


class NotificationRepository:
    @staticmethod
    def save(notification: Notification) -> Notification:
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def get_by_id(notification_id):
        return db.session.get(Notification, notification_id)

    @staticmethod
    def get_all_by_recipient(
        recipient_user_id, search=None, created_date: date | None = None, project_id=None
    ):
        query = Notification.query.filter(Notification.recipient_user_id == recipient_user_id)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(Notification.message.ilike(search_pattern))

        if created_date:
            query = query.filter(db.func.date(Notification.created_at) == created_date)

        if project_id:
            query = query.filter(Notification.project_id == project_id)

        return query.order_by(Notification.created_at.desc()).all()
