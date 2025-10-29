"""DocumentType model."""

from sqlmodel import Field
from root_core.database import BaseModel


class DocumentType(BaseModel, table=True):
    """DocumentType model class."""

    __tablename__ = "archive_document_types"  # type: ignore
    # Add your fields here
    name: str = Field(
        ...,
        max_length=100,
        title="اسم نوع المستند",
        description="اسم نوع المستند",
    )
    description: str = Field(
        ...,
        max_length=255,
        title="وصف نوع المستند",
        description="وصف نوع المستند",
    )
