"""UserPermission router."""

from core.bases.crud_api import CRUDApi
from core.database import get_session
from core.apps.auth.services.userpermission_service import UserPermissionService
from core.apps.auth.repositories.userpermission_repository import (
    UserPermissionRepository,
)
from core.apps.auth.schemas.userpermission import (
    UserPermissionCreate,
    UserPermissionUpdate,
)

resource_name: str = "user-permissions"


def get_userpermission_repository():
    """Get userpermission repository instance."""
    return UserPermissionRepository(get_session)  # type:ignore


def get_userpermission_service():
    """Get userpermission service instance."""
    repository = get_userpermission_repository()
    return UserPermissionService(repository)


class UserPermissionRouter(CRUDApi):
    """UserPermission router class."""

    def __init__(self):
        super().__init__(
            service=get_userpermission_service(),
            create_schema=UserPermissionCreate,
            update_schema=UserPermissionUpdate,
            tags=["Userpermissions"],
            resource_name=resource_name,
        )


# Router instance
router = UserPermissionRouter()
