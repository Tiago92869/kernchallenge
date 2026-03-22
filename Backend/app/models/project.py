import uuid
import enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.extensions import db

class ProjectVisibility(enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"

class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    visibility = db.Column(db.Enum(ProjectVisibility, name="project_visibility"), nullable=False, default=ProjectVisibility.PRIVATE)
    is_archived = db.Column(db.Boolean, nullable=False, default=False)

    owner_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    archived_at = db.Column(db.DateTime, nullable=True)
    archived_by_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)
    archived_reason = db.Column(db.String(255), nullable=True)
    
    last_entry_added_at = db.Column(db.DateTime, nullable=True)
    
    owner = db.relationship("User",foreign_keys=[owner_id],back_populates="owned_projects")
    archived_by = db.relationship("User",foreign_keys=[archived_by_user_id],back_populates="archived_projects_actions")
    project_members = db.relationship("ProjectMember",foreign_keys="ProjectMember.project_id",back_populates="project",lazy=True)
    notifications = db.relationship("Notification",foreign_keys="Notification.project_id",back_populates="project",lazy=True)
    time_entries = db.relationship("TimeEntry",foreign_keys="TimeEntry.project_id",back_populates="project",lazy=True)
