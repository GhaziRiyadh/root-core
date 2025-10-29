"""UserPermission repository."""

from root_core.bases.base_repository import BaseRepository
from root_core.apps.auth.models.userpermission import UserPermission


class UserPermissionRepository(BaseRepository[UserPermission]):
    """UserPermission repository class."""

    model = UserPermission
