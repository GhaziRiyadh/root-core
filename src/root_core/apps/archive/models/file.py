"""File model."""

from typing import Optional
from sqlmodel import Column, DateTime, Enum, Field, Relationship
from root_core.apps.archive.models.archive import Archive
from root_core.apps.archive.utils.image_sizes import ImageSize
from root_core.database import BaseModel
from datetime import datetime
from root_core.config import settings


class File(BaseModel, table=True):
    """File model class."""

    __tablename__ = "archive_files"  # type: ignore

    name: str = Field(max_length=255, nullable=False, index=True)
    src: str = Field(max_length=500, nullable=False)
    size: str = Field(
        default=str(ImageSize.COURSE_THUMBNAIL),
        nullable=False,
    )

    uploaded_at: datetime = Field(
        default_factory=settings.get_now,
        sa_column=Column(DateTime(timezone=True)),
    )
    archive_id: Optional[int] = Field(
        default=None, foreign_key="archive_archives.id", nullable=True
    )

    archive: "Archive" = Relationship(back_populates="files")
