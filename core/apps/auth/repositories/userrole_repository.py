"""UserRole repository."""

from src.core.bases.base_repository import BaseRepository
from src.core.apps.auth.models.userrole import UserRole


class UserRoleRepository(BaseRepository[UserRole]):
    """UserRole repository class."""

    model = UserRole
