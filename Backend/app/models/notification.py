import uuid
import enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.extensions import db

class NotificationType(enum.Enum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    recipient_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    actor_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey("projects.id"), nullable=False)

    notification_type = db.Column(db.Enum(NotificationType, name="notification_type"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    read_at = db.Column(db.DateTime, nullable=True)

    recipient = db.relationship("User", foreign_keys=[recipient_user_id], back_populates="notifications_received")
    actor = db.relationship("User",foreign_keys=[actor_user_id],back_populates="notifications_triggered")
    project = db.relationship("Project",foreign_keys=[project_id],back_populates="notifications")
    