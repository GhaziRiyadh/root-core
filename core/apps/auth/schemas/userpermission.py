"""UserPermission schemas."""

from typing import Optional
from pydantic import BaseModel


class UserPermissionCreate(BaseModel):
    """Schema for creating a userpermission."""
    user_id: int
    permission_id: int


class UserPermissionUpdate(BaseModel):
    """Schema for updating a userpermission."""
    user_id: Optional[int] = None
    permission_id: Optional[int] = None

