from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_active: bool = True


class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    is_active: bool
    vendor_id: UUID