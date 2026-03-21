import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(100), nullable=False, unique=True)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    password_hash = db.Column(db.String(255), nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True)

    #helper methods for password
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)