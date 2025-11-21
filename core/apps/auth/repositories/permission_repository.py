"""Permission repository."""

from src.core.bases.base_repository import BaseRepository
from ..models.permission import Permission


class PermissionRepository(BaseRepository[Permission]):
    """Permission repository class."""
    
    model = Permission
