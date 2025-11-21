"""GroupRole schemas."""

from typing import Optional
from pydantic import BaseModel


class GroupRoleCreate(BaseModel):
    """Schema for creating a grouprole."""
    role_id: int
    group_id: int


class GroupRoleUpdate(BaseModel):
    """Schema for updating a grouprole."""
    role_id: Optional[int] = None
    group_id: Optional[int] = None

