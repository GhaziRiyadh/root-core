"""Role model."""

from typing import TYPE_CHECKING, List
from sqlmodel import Field, Relationship
from .grouprole import GroupRole
from .rolepermission import RolePermission
from .userrole import UserRole
from root_core.database import BaseModel


from .permission import Permission

if TYPE_CHECKING:
    from .user import User
    from .group import Group


class Role(BaseModel, table=True):
    """Role model class."""

    __tablename__ = "auth_roles"  # type: ignore
    name: str = Field(
        max_length=50,
        unique=True,
        index=True,
        title="اسم الدور",
        description="دور المستخدم",
    )
    description: str = Field(
        default="",
        title="وصف الدور",
        description="وصف دور المستخدم",
    )

    # relations
    permissions: list["Permission"] = Relationship(  # type:ignore
        back_populates="roles",
        link_model=RolePermission,
    )
    users: List["User"] = Relationship(  # type:ignore
        back_populates="roles",
        link_model=UserRole,
    )
    groups: List["Group"] = Relationship(  # type:ignore
        back_populates="roles",
        link_model=GroupRole,
    )
