# app/schema/invite.py
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from typing import List, Optional

class InviteCreate(BaseModel):
    email: EmailStr
    group: str

class InviteResponse(BaseModel):
    email: EmailStr
    token: str
    invite_url: str

class InviteAcceptRequest(BaseModel):
    token: str
    password: str

class GroupOut(BaseModel):
    id: UUID
    name: str
    model_config = ConfigDict(from_attributes=True)

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    location_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    groups: List[GroupOut] = []

    # This allows Pydantic to read data from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)