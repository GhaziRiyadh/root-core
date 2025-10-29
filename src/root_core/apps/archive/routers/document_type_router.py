"""DocumentType router."""

from root_core.bases.crud_api import CRUDApi
from root_core.database import get_session
from root_core.apps.archive.services.document_type_service import DocumentTypeService
from root_core.apps.archive.repositories.document_type_repository import (
    DocumentTypeRepository,
)
from root_core.apps.archive.schemas.document_type import (
    DocumentTypeCreate,
    DocumentTypeUpdate,
)

resource_name: str = "أنواع المستندات"  # "Document Types" in Arabic


def get_document_type_repository():
    """Get document_type repository instance."""
    return DocumentTypeRepository(get_session)  # type:ignore


def get_document_type_service():
    """Get document_type service instance."""
    repository = get_document_type_repository()
    return DocumentTypeService(repository)


class DocumentTypeRouter(CRUDApi):
    """DocumentType router class."""

    def __init__(self):
        super().__init__(
            service=get_document_type_service(),
            create_schema=DocumentTypeCreate,
            update_schema=DocumentTypeUpdate,
            prefix="/document-types",
            tags=["Documenttypes"],
            resource_name=resource_name,
        )


# Router instance
router = DocumentTypeRouter()
