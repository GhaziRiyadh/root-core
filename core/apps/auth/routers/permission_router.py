"""Permission router."""

from src.core.database import get_session
from src.core.bases.crud_api import CRUDApi
from src.core.apps.auth.services.permission_service import PermissionService
from src.core.apps.auth.repositories.permission_repository import PermissionRepository
from src.core.apps.auth.schemas.permission import PermissionCreate, PermissionUpdate

resource_name: str = "permissions"


def get_permission_repository():
    """Get permission repository instance."""
    return PermissionRepository(get_session)  # type:ignore


def get_permission_service():
    """Get permission service instance."""
    repository = get_permission_repository()
    return PermissionService(repository)


class PermissionRouter(CRUDApi):
    """Permission router class."""

    def __init__(self):
        super().__init__(
            service=get_permission_service(),
            create_schema=PermissionCreate,
            update_schema=PermissionUpdate,
            tags=["Permissions"],
            resource_name=resource_name,
        )


# Router instance
router = PermissionRouter()
