"""UserRole router."""

from root_core.bases.crud_api import CRUDApi
from root_core.database import get_session
from root_core.apps.auth.services.userrole_service import UserRoleService
from root_core.apps.auth.repositories.userrole_repository import UserRoleRepository
from root_core.apps.auth.schemas.userrole import UserRoleCreate, UserRoleUpdate

resource_name = "ادوار المستخدمين"


def get_userrole_repository():
    """Get userrole repository instance."""
    return UserRoleRepository(get_session)  # type:ignore


def get_userrole_service():
    """Get userrole service instance."""
    repository = get_userrole_repository()
    return UserRoleService(repository)


class UserRoleRouter(CRUDApi):
    """UserRole router class."""

    def __init__(self):
        super().__init__(
            service=get_userrole_service(),
            create_schema=UserRoleCreate,
            update_schema=UserRoleUpdate,
            prefix="/userroles",
            tags=["Userroles"],
            resource_name=resource_name,
        )


# Router instance
router = UserRoleRouter()
