"""RolePermission model."""

from sqlmodel import Field, SQLModel


class RolePermission(SQLModel, table=True):
    """RolePermission model class."""

    __tablename__ = "auth_role_permissions"  # type: ignore
    permission_id: int = Field(
        foreign_key="auth_permissions.id",
        primary_key=True,
        title="معرف الصلاحية",
        description="معرف الصلاحية المرتبط بالدور",
    )
    role_id: int = Field(
        foreign_key="auth_roles.id",
        primary_key=True,
        title="معرف الدور",
        description="معرف الدور المرتبط بالمستخدم",
    )
