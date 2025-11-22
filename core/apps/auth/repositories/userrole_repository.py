"""UserRole repository."""

from core.bases.base_repository import BaseRepository
from core.apps.auth.models.userrole import UserRole


class UserRoleRepository(BaseRepository[UserRole]):
    """UserRole repository class."""

    model = UserRole
