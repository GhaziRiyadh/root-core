"""Log schemas."""

from typing import Optional
from pydantic import BaseModel


class LogCreate(BaseModel):
    """Schema for creating a log."""
    name: str


class LogUpdate(BaseModel):
    """Schema for updating a log."""
    name: Optional[str] = None

