from core.bases.serializer import BaseSerializer, SerializerMethodField
from core.apps.auth.models.user import User


class UserSerializer(BaseSerializer):
    class Meta:
        model = User
        # Define fields explicitly or rely on model fields
        # fields = ["id", "username", "email", "full_name"]

    is_active_display = SerializerMethodField()

    async def save_roles(self, instance: User, role_ids: list, **kwargs):
        if not role_ids:
            return

        from core.apps.auth.routers.role_router import get_role_repository

        role_repo = get_role_repository()
        async with role_repo.get_session() as session:
            from sqlmodel import select
            from core.apps.auth.models.role import Role

            stmt = select(Role).where(Role.id.in_(role_ids))  # type: ignore
            roles = (await session.exec(stmt)).all()

            # Since instance might be detached or we want to ensure persistence
            # Simplest way for M2M update on existing instance:
            instance.roles = list(roles)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)

    async def save_groups(self, instance: User, group_ids: list, **kwargs):
        if not group_ids:
            return

        from core.apps.auth.routers.group_router import get_group_repository

        group_repo = get_group_repository()
        async with group_repo.get_session() as session:
            from sqlmodel import select
            from core.apps.auth.models.group import Group

            stmt = select(Group).where(Group.id.in_(group_ids))  # type: ignore
            groups = (await session.exec(stmt)).all()

            instance.groups = list(groups)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)

    # Relation fields (returning IDs as per legacy logic)
    roles = SerializerMethodField()
    groups = SerializerMethodField()
    permissions = SerializerMethodField()

    def get_full_name(self, obj: User) -> str:
        # Assuming User has first_name and last_name, or just returning username as fallback
        first = getattr(obj, "first_name", "")
        last = getattr(obj, "last_name", "")
        if first or last:
            return f"{first} {last}".strip()
        return getattr(obj, "username", "")

    def get_is_active_display(self, obj: User) -> str:
        return "Active" if getattr(obj, "is_active", False) else "Inactive"

    def get_roles(self, obj: User) -> list:
        return [role.id for role in obj.roles] if hasattr(obj, "roles") else []

    def get_groups(self, obj: User) -> list:
        return [group.id for group in obj.groups] if hasattr(obj, "groups") else []

    def get_permissions(self, obj: User) -> list:
        return (
            [perm.id for perm in obj.permissions] if hasattr(obj, "permissions") else []
        )
