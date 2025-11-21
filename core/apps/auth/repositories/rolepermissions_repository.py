"""RolePermission repository."""

from src.core.bases.base_repository import BaseRepository
from ..models.rolepermission import RolePermission


class RolePermissionRepository(BaseRepository[RolePermission]):
    """RolePermission repository class."""

    model = RolePermission
