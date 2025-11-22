"""Archive router."""

from core.router import add_route
from core.bases.crud_api import CRUDApi
from core.config import PermissionAction
from core.database import get_session
from core.apps.archive.services.archive_service import ArchiveService
from core.apps.archive.repositories.archive_repository import ArchiveRepository
from core.apps.archive.schemas.archive import ArchiveCreate, ArchiveUpdate
from fastapi import Form, UploadFile, status
from src.core import exceptions
from core.response import handlers

resource_name: str = "archives"


def get_archive_repository():
    """Get archive repository instance."""
    return ArchiveRepository(get_session)  # type:ignore


def get_archive_service():
    """Get archive service instance."""
    repository = get_archive_repository()
    return ArchiveService(repository)


class ArchiveRouter(CRUDApi):
    """Archive router class."""

    service: ArchiveService

    def __init__(self):
        super().__init__(
            service=get_archive_service(),
            create_schema=ArchiveCreate,
            update_schema=ArchiveUpdate,
            tags=["Archives"],
            resource_name=resource_name,
        )

    @add_route(
        "/{id}/files/",
        "GET",
        response_model=list,
        response_model_exclude_none=True,
        name="Get files of an archive",
        action=PermissionAction.READ,
    )
    async def get_files(self, archive_id: int):
        try:
            return handlers.success_response(**await self.service.get_files(archive_id))
        except exceptions.ValidationException as e:
            return handlers.error_response(
                error_code="VALIDATION_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=[detail.model_dump() for detail in e.error_details],
            )
        except exceptions.ServiceException as e:
            return handlers.error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/upload/",
        "POST",
        response_model=list,
        response_model_exclude_none=True,
        name="Upload files",
        action=PermissionAction.CREATE,
    )
    async def upload_file(self, file: UploadFile, archive_id: int | None = Form(None)):
        try:
            return handlers.success_response(
                **await self.service.upload_file(file, archive_id)
            )
        except exceptions.ValidationException as e:
            return handlers.error_response(
                error_code="VALIDATION_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=[detail.model_dump() for detail in e.error_details],
            )
        except exceptions.ServiceException as e:
            return handlers.error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Router instance
router = ArchiveRouter()
