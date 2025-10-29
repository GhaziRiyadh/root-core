"""UserRole repository."""

from root_core.bases.base_repository import BaseRepository
from root_core.apps.auth.models.userrole import UserRole


class UserRoleRepository(BaseRepository[UserRole]):
    """UserRole repository class."""

    model = UserRole
