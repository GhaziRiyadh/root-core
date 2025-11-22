"""Group repository."""

from typing import List
from ..routers.permission_router import get_permission_repository
from ..routers.role_router import get_role_repository
from core.bases.base_repository import BaseRepository
from ..models.group import Group
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession


class GroupRepository(BaseRepository[Group]):
    """Group repository class."""

    model = Group
    _search_fields = ["name"]

    _options = [
        selectinload(Group.roles)  # type:ignore
    ]

    async def update_roles(
        self,
        session: AsyncSession,
        obj_in: Group,
        roles,
    ):
        role_repo = get_role_repository()
        role_res = await session.exec(role_repo._build_select_stmt(id=roles))
        obj_in.roles = role_res.all()  # type:ignore
