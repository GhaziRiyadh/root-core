"""UserRole router."""

from src.core.bases.crud_api import CRUDApi
from src.core.database import get_session
from src.core.apps.auth.services.userrole_service import UserRoleService
from src.core.apps.auth.repositories.userrole_repository import UserRoleRepository
from src.core.apps.auth.schemas.userrole import UserRoleCreate, UserRoleUpdate

resource_name: str = "user-roles"


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
            tags=["Userroles"],
            resource_name=resource_name,
        )


# Router instance
router = UserRoleRouter()
