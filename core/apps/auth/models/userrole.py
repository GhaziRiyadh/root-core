"""UserRole model."""

from sqlmodel import Field, SQLModel


class UserRole(SQLModel, table=True):
    """UserRole model class."""

    __tablename__ = "auth_user_roles"  # type: ignore
    user_id: int = Field(
        foreign_key="auth_users.id",
        primary_key=True,
        title=" المستخدم",
        description=" المستخدم المرتبط بالصلاحية",
    )
    role_id: int = Field(
        foreign_key="auth_roles.id",
        primary_key=True,
        title=" الدور",
        description=" الدور المرتبط بالمستخدم",
    )
