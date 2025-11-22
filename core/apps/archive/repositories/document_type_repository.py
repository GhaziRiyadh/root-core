"""DocumentType repository."""

from core.bases.base_repository import BaseRepository
from core.apps.archive.models.document_type import DocumentType


class DocumentTypeRepository(BaseRepository[DocumentType]):
    """DocumentType repository class."""

    model = DocumentType
