"""DocumentType repository."""

from src.core.bases.base_repository import BaseRepository
from src.core.apps.archive.models.document_type import DocumentType


class DocumentTypeRepository(BaseRepository[DocumentType]):
    """DocumentType repository class."""

    model = DocumentType
