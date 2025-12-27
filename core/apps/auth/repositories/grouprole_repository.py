"""GroupRole repository."""

from core.bases.base_repository import BaseRepository
from core.apps.auth.models.grouprole import GroupRole


class GroupRoleRepository(BaseRepository[GroupRole]):
    """GroupRole repository class."""

    model = GroupRole
