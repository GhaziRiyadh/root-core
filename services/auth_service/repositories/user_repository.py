"""User repository."""

from typing import List
from core.bases.base_repository import BaseRepository
from ..models.user import User
from ..models.role import Role
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession


class UserRepository(BaseRepository[User]):
    """User repository class."""

    model = User
    _search_fields = ["name", "username"]
    _options = [
        selectinload(User.groups),  # type:ignore
        selectinload(User.roles).selectinload(Role.permissions),  # type:ignore
        selectinload(User.permissions),  # type:ignore
    ]
    

    async def update_roles(
        self,
        session: AsyncSession,
        obj_in: User,
        roles,
    ):
        from ..routers.role_router import get_role_repository

        role_repo = get_role_repository()
        role_res = await session.exec(role_repo._build_select_stmt(id=roles))
        obj_in.roles = role_res.all()  # type:ignore

    async def update_groups(
        self,
        session: AsyncSession,
        obj_in: User,
        groups,
    ):
        from ..routers.group_router import get_group_repository

        groups_repo = get_group_repository()
        groups_res = await session.exec(groups_repo._build_select_stmt(id=groups))
        obj_in.groups = groups_res.all()  # type:ignore

    async def update_permissions(
        self,
        session: AsyncSession,
        obj_in: User,
        permissions: List[int],
    ):
        from ..routers.permission_router import get_permission_repository

        permission_repo = get_permission_repository()
        permission_res = await session.exec(
            permission_repo._build_select_stmt(id=permissions)
        )
        obj_in.permissions = permission_res.all()  # type:ignore
