"""GroupRole router."""

from core.database import get_session
from core.bases.crud_api import CRUDApi
from ..services.grouprole_service import GroupRoleService
from ..repositories.grouprole_repository import GroupRoleRepository
from ..schemas.grouprole import GroupRoleCreate, GroupRoleUpdate

resource_name: str = "role-groups"


def get_grouprole_repository():
    """Get grouprole repository instance."""
    return GroupRoleRepository(get_session)  # type:ignore


def get_grouprole_service():
    """Get grouprole service instance."""
    repository = get_grouprole_repository()
    return GroupRoleService(repository)


class GroupRoleRouter(CRUDApi):
    """GroupRole router class."""

    def __init__(self):
        super().__init__(
            service=get_grouprole_service(),
            create_schema=GroupRoleCreate,
            update_schema=GroupRoleUpdate,
            tags=["Grouproles"],
            resource_name=resource_name,
        )


# Router instance
router = GroupRoleRouter()
