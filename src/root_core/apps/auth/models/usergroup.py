"""UserGroup model."""

from sqlmodel import Field, SQLModel


class UserGroup(SQLModel, table=True):
    """UserGroup model class."""

    __tablename__ = "auth_user_groups"  # type: ignore
    user_id: int = Field(
        foreign_key="auth_users.id",
        primary_key=True,
        title="معرف المستخدم",
        description="معرف المستخدم المرتبط بالصلاحية",
    )
    group_id: int = Field(
        foreign_key="auth_groups.id",
        primary_key=True,
        title="معرف المجموعة",
        description="معرف المجموعة المرتبط بالمستخدم",
    )
