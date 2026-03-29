# app/models/session.py
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base


class UserSession(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    refresh_jti = Column(String, nullable=False, unique=True, index=True)

    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

    is_revoked = Column(Boolean, default=False)

    created_at = Column(DateTime, default=func.now())
    last_used_at = Column(DateTime, nullable=True)