"""UserPermission repository."""

from core.bases.base_repository import BaseRepository
from core.apps.auth.models.userpermission import UserPermission


class UserPermissionRepository(BaseRepository[UserPermission]):
    """UserPermission repository class."""

    model = UserPermission
