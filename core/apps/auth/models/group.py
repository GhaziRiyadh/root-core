"""Group model."""

from typing import TYPE_CHECKING, List
from sqlmodel import Field, Relationship
from .grouprole import GroupRole
from .usergroup import UserGroup
from src.core.database import BaseModel


if TYPE_CHECKING:
    from .role import Role
    from .user import User


class Group(BaseModel, table=True):
    """Group model class."""

    __tablename__ = "auth_groups"  # type: ignore
    name: str = Field(
        max_length=50,
        unique=True,
        index=True,
        title="اسم المجموعة",
        description="مجموعة المستخدمين",
    )
    description: str = Field(
        default="",
        title="وصف المجموعة",
        description="وصف مجموعة المستخدمين",
    )

    # relations
    roles: List["Role"] = Relationship(  # type:ignore
        back_populates="groups",
        link_model=GroupRole,
    )
    users: List["User"] = Relationship(  # type:ignore
        back_populates="groups",
        link_model=UserGroup,
    )
