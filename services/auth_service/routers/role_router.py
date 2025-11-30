"""Role router."""

from core.bases.crud_api import CRUDApi
from core.database import get_session
from ..services.role_service import RoleService
from ..repositories.role_repository import RoleRepository
from ..schemas.role import RoleCreate, RoleUpdate

resource_name: str = "roles"


def get_role_repository():
    """Get role repository instance."""
    return RoleRepository(get_session)  # type:ignore


def get_role_service():
    """Get role service instance."""
    repository = get_role_repository()
    return RoleService(repository)


class RoleRouter(CRUDApi):
    """Role router class."""

    def __init__(self):
        super().__init__(
            service=get_role_service(),
            create_schema=RoleCreate,
            update_schema=RoleUpdate,
            tags=["Roles"],
            resource_name=resource_name,
        )


# Router instance
router = RoleRouter()
