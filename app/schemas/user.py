from pydantic import BaseModel, ConfigDict
from uuid import UUID


class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    is_active: bool
    vendor_id: UUID