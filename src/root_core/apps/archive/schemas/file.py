"""File schemas."""

from typing import Optional
from pydantic import BaseModel


class FileCreate(BaseModel):
    """Schema for creating a file."""
    name: str


class FileUpdate(BaseModel):
    """Schema for updating a file."""
    name: Optional[str] = None

