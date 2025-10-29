"""GroupRole router."""

from root_core.database import get_session
from root_core.bases.crud_api import CRUDApi
from root_core.apps.auth.services.grouprole_service import GroupRoleService
from root_core.apps.auth.repositories.grouprole_repository import GroupRoleRepository
from root_core.apps.auth.schemas.grouprole import GroupRoleCreate, GroupRoleUpdate

resource_name = "أدوار المجموعات"


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
            prefix="/grouproles",
            tags=["Grouproles"],
            resource_name=resource_name,
        )


# Router instance
router = GroupRoleRouter()
