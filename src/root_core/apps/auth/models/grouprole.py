"""GroupRole model."""

from sqlmodel import Field, SQLModel


class GroupRole(SQLModel, table=True):
    """GroupRole model class."""

    __tablename__ = "auth_group_roles"  # type: ignore
    role_id: int = Field(
        foreign_key="auth_roles.id",
        primary_key=True,
        title="معرف الدور",
        description="معرف الدور المرتبط بالمجموعة",
    )
    group_id: int = Field(
        foreign_key="auth_groups.id",
        primary_key=True,
        title="معرف المجموعة",
        description="معرف المجموعة المرتبط بالدور",
    )
