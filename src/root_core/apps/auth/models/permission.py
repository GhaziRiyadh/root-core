"""Permission model."""

from typing import List, TYPE_CHECKING
from sqlmodel import Field, Relationship, UniqueConstraint

from .rolepermission import RolePermission
from .userpermission import UserPermission
from root_core.database import BaseModel

if TYPE_CHECKING:
    from .role import Role
from root_core.apps.auth.models.user import User


class Permission(BaseModel, table=True):
    """Permission model class."""

    __tablename__ = "auth_permissions"  # type: ignore
    # add constraint to make (resource, action) unique

    resource: str = Field(
        max_length=100,
        title="المورد",
        description="المورد الذي تنتمي له الصلاحية",
    )
    action: str = Field(
        max_length=100,
        # sa_column=Column(
        #     "action",
        #     Enum(
        #         PermissionAction,
        #         create_constraint=True,
        #         native_enum=False,
        #     ),
        # ),
        title="الإجراء",
        description="الإجراء الذي تغطيه الصلاحية",
    )
    app_name: str = Field(
        max_length=100,
        title="اسم التطبيق",
        description="اسم التطبيق الذي تنتمي له الصلاحية",
    )

    __table_args__ = (
        UniqueConstraint(
            "resource",
            "action",
            "is_deleted",
            name="uix_resource_action",
        ),
    )

    # relations
    roles: List["Role"] = Relationship(
        back_populates="permissions",
        link_model=RolePermission,
    )

    users: List["User"] = Relationship(  # type:ignore
        back_populates="permissions",
        link_model=UserPermission,
    )
