"""Group router."""

from root_core.bases.crud_api import CRUDApi
from root_core.database import get_session
from root_core.apps.auth.services.group_service import GroupService
from root_core.apps.auth.repositories.group_repository import GroupRepository
from root_core.apps.auth.schemas.group import GroupCreate, GroupUpdate

resource_name = "المجموعات"


def get_group_repository():
    """Get group repository instance."""
    return GroupRepository(get_session)  # type:ignore


def get_group_service():
    """Get group service instance."""
    repository = get_group_repository()
    return GroupService(repository)


class GroupRouter(CRUDApi):
    """Group router class."""

    def __init__(self):
        super().__init__(
            service=get_group_service(),
            create_schema=GroupCreate,
            update_schema=GroupUpdate,
            prefix="/groups",
            tags=["Groups"],
            resource_name=resource_name,
        )


# Router instance
router = GroupRouter()
