"""Archive service."""

from typing import Any, Dict, List

from fastapi import UploadFile
from root_core.apps.archive.routers.file_router import get_file_repository
from root_core.apps.archive.utils.upload_file import handle_upload_file
from root_core.apps.archive.utils.utils import archive_to_srcset, get_file_url
from root_core.bases.base_service import BaseService
from root_core.apps.archive.repositories.archive_repository import ArchiveRepository
from root_core.apps.archive.models.archive import Archive


class ArchiveService(BaseService[Archive]):
    """Archive service class."""

    repository: ArchiveRepository

    async def _return_multi_data(self, data: List):
        return [
            {
                **archive.model_dump(),
                "original_path": get_file_url(archive.original_path),
                "full_src_set": await archive_to_srcset(archive),
            }
            for archive in data
        ]

    async def _return_one_data(self, data: Archive):
        return {
            **data.model_dump(),
            "original_path": get_file_url(data.original_path),
            "full_src_set": await archive_to_srcset(data),
        }

    async def _validate_create(self, create_data: Dict[str, Any]) -> None:
        """Validate data before creation."""
        # Add your business logic validation here
        pass

    async def _validate_update(
        self, item_id: Any, update_data: Dict[str, Any], existing_item: Archive
    ) -> None:
        """Validate data before update."""
        # Add your business logic validation here
        pass

    async def _validate_delete(self, item_id: Any, existing_item: Archive) -> None:
        """Validate before soft delete."""
        # Add your business logic validation here
        pass

    async def _validate_force_delete(
        self, item_id: Any, existing_item: Archive
    ) -> None:
        """Validate before force delete."""
        # Add your business logic validation here
        pass

    async def get_files(self, archive_id: int):
        """Get files associated with an archive."""
        file_repo = get_file_repository()
        return {
            "data": await self._return_multi_data(
                await file_repo.get_many(archive_id=archive_id)
            ),
            "message": "Files retrieved successfully",
        }

    async def upload_file(self, file: UploadFile, archive_id: int | None = None):
        """Upload files and associate them with an archive."""

        return {
            "data": await self._return_one_data(
                await self.repository.create_or_update_from_path(
                    await handle_upload_file(file), archive_id
                )
            ),
            "message": "Files uploaded successfully",
        }
