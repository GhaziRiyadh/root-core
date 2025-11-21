"""UserPermission repository."""

from src.core.bases.base_repository import BaseRepository
from src.core.apps.auth.models.userpermission import UserPermission


class UserPermissionRepository(BaseRepository[UserPermission]):
    """UserPermission repository class."""

    model = UserPermission
