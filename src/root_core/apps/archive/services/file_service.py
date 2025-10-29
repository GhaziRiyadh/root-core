"""File service."""

from typing import Any, Dict
from root_core.bases.base_service import BaseService
from root_core.apps.archive.repositories.file_repository import FileRepository
from root_core.apps.archive.models.file import File


class FileService(BaseService[File]):
    """File service class."""

    def __init__(self, repository: FileRepository):
        super().__init__(repository)

    async def _validate_create(self, create_data: Dict[str, Any]) -> None:
        """Validate data before creation."""
        # Add your business logic validation here
        pass

    async def _validate_update(
        self, item_id: Any, update_data: Dict[str, Any], existing_item: File
    ) -> None:
        """Validate data before update."""
        # Add your business logic validation here
        pass

    async def _validate_delete(self, item_id: Any, existing_item: File) -> None:
        """Validate before soft delete."""
        # Add your business logic validation here
        pass

    async def _validate_force_delete(self, item_id: Any, existing_item: File) -> None:
        """Validate before force delete."""
        # Add your business logic validation here
        pass
