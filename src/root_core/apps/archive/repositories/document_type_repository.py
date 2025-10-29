"""DocumentType repository."""

from root_core.bases.base_repository import BaseRepository
from root_core.apps.archive.models.document_type import DocumentType


class DocumentTypeRepository(BaseRepository[DocumentType]):
    """DocumentType repository class."""

    model = DocumentType
