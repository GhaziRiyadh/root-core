"""Role schemas."""

from typing import List, Optional
from pydantic import BaseModel


class RoleCreate(BaseModel):
    """Schema for creating a role."""

    name: str
    description: str


class RoleUpdate(BaseModel):
    """Schema for updating a role."""

    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[int]] = None
