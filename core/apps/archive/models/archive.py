"""Archive model."""

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from core.database import BaseModel

if TYPE_CHECKING:
    from .file import File


class Archive(BaseModel, table=True):
    """Archive model class."""

    __tablename__ = "archive_archives"  # type: ignore
    name: str = Field(max_length=255, nullable=False, index=True)
    original_path: str = Field(max_length=500, nullable=False)
    mime_type: str = Field(default="unknown", max_length=100)
    file_size: int = Field(default=0)

    file_type: Optional[str] = Field(default=None, max_length=50)
    user_id: Optional[int] = Field(None, foreign_key="auth_users.id")

    files: List["File"] = Relationship(back_populates="archive")
    # created_by: "User" = Relationship(back_populates="archives")
