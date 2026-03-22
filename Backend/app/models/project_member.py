import uuid
import enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.extensions import db

class ProjectMember(db.Model):
    __tablename__ = "project_members"

    # Make sure there are no entiries with the same project id and user id combination
    __table_args__ = (
        db.UniqueConstraint("project_id", "user_id", name="uq_project_members_project_user"),
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey("projects.id"), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)

    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    added_by_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)
    
    removed_at = db.Column(db.DateTime, nullable=True)
    removed_by_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)

    project = db.relationship("Project",foreign_keys=[project_id],back_populates="project_members")
    user = db.relationship("User", foreign_keys=[user_id], back_populates="project_memberships")
    added_by = db.relationship("User", foreign_keys=[added_by_user_id], back_populates="memberships_added")
    removed_by = db.relationship("User", foreign_keys=[removed_by_user_id], back_populates="memberships_removed")
