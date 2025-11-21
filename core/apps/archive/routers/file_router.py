"""File router."""

from src.core.bases.crud_api import CRUDApi
from src.core.database import get_session
from src.core.apps.archive.services.file_service import FileService
from src.core.apps.archive.repositories.file_repository import FileRepository
from src.core.apps.archive.schemas.file import FileCreate, FileUpdate

resource_name: str = "archive-files"


def get_file_repository():
    """Get file repository instance."""
    return FileRepository(get_session)  # type:ignore


def get_file_service():
    """Get file service instance."""
    repository = get_file_repository()
    return FileService(repository)


class FileRouter(CRUDApi):
    """File router class."""

    def __init__(self):
        super().__init__(
            service=get_file_service(),
            create_schema=FileCreate,
            update_schema=FileUpdate,
            tags=["Files"],
            resource_name=resource_name,
        )


# Router instance
router = FileRouter()
