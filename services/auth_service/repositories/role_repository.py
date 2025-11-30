"""Role repository."""

from typing import TYPE_CHECKING, List
from core.bases.base_repository import BaseRepository
from ..models.role import Role
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

if TYPE_CHECKING:
    from ..models.permission import Permission


class RoleRepository(BaseRepository[Role]):
    """Role repository class."""

    model = Role
    _search_fields = ["name"]
    _options = [
        selectinload(Role.permissions)  # type:ignore
    ]

    async def update_permissions(
        self,
        session: AsyncSession,
        obj_in: Role,
        permissions: List[int],
    ):
        from ..routers.permission_router import get_permission_repository

        permission_repo = get_permission_repository()
        permission_res = await session.exec(
            permission_repo._build_select_stmt(id=permissions)
        )
        obj_in.permissions = permission_res.all()  # type:ignore

    async def get_permissions(self, role_id: int) -> List["Permission"]:
        role = await self.get(role_id)
        if role and role.permissions:
            return role.permissions
        return []

    async def get_by_name(self, name: str) -> Role | None:
        """Get role by name."""
        async with self.get_session() as session:
            result = await session.exec(self._build_select_stmt(name=name))
            return result.first()
