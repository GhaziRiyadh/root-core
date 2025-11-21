"""RolePermission schemas."""

from typing import Optional
from pydantic import BaseModel


class RolePermissionCreate(BaseModel):
    """Schema for creating a rolepermissions."""

    user_id: int
    role_id: int


class RolePermissionUpdate(BaseModel):
    """Schema for updating a rolepermissions."""

    user_id: Optional[int] = None
    role_id: Optional[int] = None
