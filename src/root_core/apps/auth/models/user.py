"""User model."""

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy import Index, text

# from root_core.apps.auth.models.usergroup import UserGroup
from .usergroup import UserGroup
from .userpermission import UserPermission
from .userrole import UserRole
from root_core.database import BaseModel


# from src.apps.passenger.models.passenger import Passenger
from .group import Group

if TYPE_CHECKING:
    from .permission import Permission
    from .role import Role


class User(BaseModel, table=True):
    """User model class."""

    __tablename__ = "auth_users"  # type: ignore
    __table_args__ = (
        # Create a conditional unique index that only applies when email IS NOT NULL.
        # This allows multiple NULL email rows while enforcing uniqueness for non-null emails.
        Index(
            "uix_auth_users_email_not_null",
            "email",
            unique=True,
            postgresql_where=text("email IS NOT NULL"),
            sqlite_where=text("email IS NOT NULL"),
        ),
        Index(
            "uix_auth_users_phone_not_null",
            "phone",
            unique=True,
            postgresql_where=text("phone IS NOT NULL"),
            sqlite_where=text("phone IS NOT NULL"),
        ),
    )
    name: str = Field(title="الاسم الكامل", max_length=100)
    email: Optional[str] = Field(
        title="البريد الإلكتروني",
        max_length=100,
        unique=False,
        index=True,
        default=None,
    )
    phone: Optional[str] = Field(
        title="رقم الهاتف",
        max_length=20,
        unique=True,
        index=True,
    )
    username: str = Field(
        max_length=50,
        unique=True,
        index=True,
        title="اسم المستخدم",
        description="اسم المستخدم الفريد",
    )
    password: Optional[str] = Field(
        default=None,
        title="كلمة المرور",
        description="كلمة مرور المستخدم",
    )
    is_superuser: Optional[bool] = Field(
        default=False,
        title="المستخدم المميز",
        description="هل المستخدم مميز؟",
    )
    # relations
    permissions: List["Permission"] = Relationship(
        back_populates="users",
        link_model=UserPermission,
    )
    roles: List["Role"] = Relationship(  # type:ignore
        back_populates="users",
        link_model=UserRole,
    )
    groups: List["Group"] = Relationship(
        back_populates="users",
        link_model=UserGroup,
    )

    # passenger: Optional["Passenger"] = Relationship(  # type:ignore
    #     back_populates="user"
    # )
