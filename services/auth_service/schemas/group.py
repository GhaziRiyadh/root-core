"""Group schemas."""

from typing import List, Optional
from pydantic import BaseModel


class GroupCreate(BaseModel):
    """Schema for creating a group."""

    name: str
    description: str
    roles: List[int]


class GroupUpdate(BaseModel):
    """Schema for updating a group."""

    name: Optional[str] = None
    description: Optional[str] = None
    roles: Optional[List[int]] = None
