"""GroupRole repository."""

from src.core.bases.base_repository import BaseRepository
from ..models.grouprole import GroupRole


class GroupRoleRepository(BaseRepository[GroupRole]):
    """GroupRole repository class."""

    model = GroupRole
