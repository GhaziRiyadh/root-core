"""UserGroup router."""

from core.bases.crud_api import CRUDApi
from core.database import get_session
from core.apps.auth.services.usergroup_service import UserGroupService
from core.apps.auth.repositories.usergroup_repository import UserGroupRepository
from core.apps.auth.schemas.usergroup import UserGroupCreate, UserGroupUpdate

resource_name: str = "user-groups"


def get_usergroup_repository():
    """Get usergroup repository instance."""
    return UserGroupRepository(get_session)  # type:ignore


def get_usergroup_service():
    """Get usergroup service instance."""
    repository = get_usergroup_repository()
    return UserGroupService(repository)


class UserGroupRouter(CRUDApi):
    """UserGroup router class."""

    def __init__(self):
        super().__init__(
            service=get_usergroup_service(),
            create_schema=UserGroupCreate,
            update_schema=UserGroupUpdate,
            tags=["Usergroups"],
            resource_name=resource_name,
        )


# Router instance
router = UserGroupRouter()
