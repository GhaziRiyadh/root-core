"""Archive schemas."""

from typing import Optional
from pydantic import BaseModel


class ArchiveCreate(BaseModel):
    """Schema for creating a archive."""
    name: str


class ArchiveUpdate(BaseModel):
    """Schema for updating a archive."""
    name: Optional[str] = None

