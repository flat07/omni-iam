# app/models/identity.py
from sqlalchemy import Column, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.base import BaseMixin, VendorMixin

class User(Base, BaseMixin, VendorMixin):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)

    # Scope
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)

    groups = relationship("Group", secondary="user_groups", back_populates="users")


class Group(Base, BaseMixin, VendorMixin):
    __tablename__ = "groups"

    name = Column(String, nullable=False)
    users = relationship("User", secondary="user_groups", back_populates="groups")
    permissions = relationship("Permission", secondary="group_permissions", back_populates="groups")
    parent_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=True)



class Permission(Base, BaseMixin, VendorMixin):
    __tablename__ = "permissions"

    code = Column(String, unique=True)  # e.g. "tickets:read"
    groups = relationship("Group", secondary="group_permissions", back_populates="permissions")



class UserGroup(Base):
    __tablename__ = "user_groups"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)


class GroupPermission(Base):
    __tablename__ = "group_permissions"

    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id"), primary_key=True)
    
