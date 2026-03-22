import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    password_hash = db.Column(db.String(255), nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)

    owned_projects = db.relationship("Project",foreign_keys="Project.owner_id",back_populates="owner",lazy=True)
    archived_projects_actions = db.relationship("Project",foreign_keys="Project.archived_by_user_id",back_populates="archived_by",lazy=True)
    project_memberships = db.relationship("ProjectMember",foreign_keys="ProjectMember.user_id",back_populates="user",lazy=True)
    memberships_added = db.relationship("ProjectMember",foreign_keys="ProjectMember.added_by_user_id",back_populates="added_by",lazy=True)
    memberships_removed = db.relationship("ProjectMember",foreign_keys="ProjectMember.removed_by_user_id",back_populates="removed_by",lazy=True)
    notifications_received = db.relationship("Notification",foreign_keys="Notification.recipient_user_id",back_populates="recipient",lazy=True)
    notifications_triggered = db.relationship("Notification",foreign_keys="Notification.actor_user_id",back_populates="actor",lazy=True)
    time_entries = db.relationship("TimeEntry",foreign_keys="TimeEntry.user_id",back_populates="user",lazy=True)
    deleted_time_entries_actions = db.relationship("TimeEntry",foreign_keys="TimeEntry.deleted_by_user_id",back_populates="deleted_by",lazy=True)

    #helper methods for password
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)