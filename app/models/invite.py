# app/models/invite.py
from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, String, Boolean, DateTime
from app.db.base import Base
from app.models.base import BaseMixin, VendorMixin


class Invite(Base, BaseMixin, VendorMixin):
    __tablename__ = "invites"

    email = Column(String)
    token = Column(String, unique=True)

    group = Column(String)

    accepted = Column(Boolean, default=False)
    expires_at = Column(DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(days=2))