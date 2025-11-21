"""UserPermission model."""

from sqlmodel import Field, SQLModel


class UserPermission(SQLModel, table=True):
    """UserPermission model class."""

    __tablename__ = "auth_user_permissions"  # type: ignore
    user_id: int = Field(
        foreign_key="auth_users.id",
        primary_key=True,
        title=" المستخدم",
        description=" المستخدم المرتبط بالصلاحية",
    )
    permission_id: int = Field(
        foreign_key="auth_permissions.id",
        primary_key=True,
        title=" الصلاحية",
        description=" الصلاحية المرتبط بالمستخدم",
    )
