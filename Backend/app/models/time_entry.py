import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.extensions import db

class TimeEntry(db.Model):
    __tablename__ = "time_entries"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(UUID(as_uuid=True), db.ForeignKey("projects.id"), nullable=False)

    description = db.Column(db.Text, nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    deleted_at = db.Column(db.DateTime, nullable=True) 
    deleted_by_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=True)

    user = db.relationship("User",foreign_keys=[user_id],back_populates="time_entries")
    project = db.relationship("Project",foreign_keys=[project_id],back_populates="time_entries")
    deleted_by = db.relationship("User",foreign_keys=[deleted_by_user_id],back_populates="deleted_time_entries_actions")