"""DocumentType schemas."""

from typing import Optional
from pydantic import BaseModel


class DocumentTypeCreate(BaseModel):
    """Schema for creating a document_type."""

    name: str
    description: str


class DocumentTypeUpdate(BaseModel):
    """Schema for updating a document_type."""

    name: Optional[str] = None
    description: Optional[str] = None
