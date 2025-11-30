"""UserRole schemas."""

from typing import Optional
from pydantic import BaseModel


class UserRoleCreate(BaseModel):
    """Schema for creating a userrole."""
    user_id: int
    role_id: int


class UserRoleUpdate(BaseModel):
    """Schema for updating a userrole."""
    user_id: Optional[int] = None
    role_id: Optional[int] = None

