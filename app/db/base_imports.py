# app/db/base_imports.py
from app.db.base import Base  # noqa: F401

# 👇 import ALL models here
from app.models.organization import Vendor, Location, Department  # noqa: F401
from app.models.identity import User, Group, Permission, UserGroup, GroupPermission  # noqa: F401