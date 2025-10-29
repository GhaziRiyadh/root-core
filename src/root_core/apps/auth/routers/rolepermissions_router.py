"""RolePermission router."""

from root_core.bases.crud_api import CRUDApi
from root_core.database import get_session
from root_core.apps.auth.services.rolepermissions_service import RolePermissionService
from root_core.apps.auth.repositories.rolepermissions_repository import (
    RolePermissionRepository,
)
from root_core.apps.auth.schemas.rolepermissions import (
    RolePermissionCreate,
    RolePermissionUpdate,
)

resource_name = "صلاحيات الأدوار"


def get_rolepermissions_repository():
    """Get rolepermissions repository instance."""
    return RolePermissionRepository(get_session)  # type:ignore


def get_rolepermissions_service():
    """Get rolepermissions service instance."""
    repository = get_rolepermissions_repository()
    return RolePermissionService(repository)


class RolePermissionRouter(CRUDApi):
    """RolePermission router class."""

    def __init__(self):
        super().__init__(
            service=get_rolepermissions_service(),
            create_schema=RolePermissionCreate,
            update_schema=RolePermissionUpdate,
            prefix="/rolepermissionss",
            tags=["Rolepermissionss"],
            resource_name=resource_name,
        )


# Router instance
router = RolePermissionRouter()
