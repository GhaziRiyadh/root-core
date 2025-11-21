"""UserGroup schemas."""

from typing import Optional
from pydantic import BaseModel


class UserGroupCreate(BaseModel):
    """Schema for creating a usergroup."""
    user_id: int
    group_id: int


class UserGroupUpdate(BaseModel):
    """Schema for updating a usergroup."""
    user_id: Optional[int] = None
    group_id: Optional[int] = None

