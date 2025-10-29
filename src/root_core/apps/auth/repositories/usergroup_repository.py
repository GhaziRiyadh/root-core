"""UserGroup repository."""

from root_core.bases.base_repository import BaseRepository
from ..models.usergroup import UserGroup


class UserGroupRepository(BaseRepository[UserGroup]):
    """UserGroup repository class."""
    
    model = UserGroup
