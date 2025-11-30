"""Auth app."""

from .routers.user_router import router as user_router
from .routers.role_router import router as role_router
from .routers.permission_router import router as permission_router
from .routers.group_router import router as group_router
from .routers.userrole_router import router as userrole_router
from .routers.rolepermissions_router import router as rolepermissions_router
from .routers.userpermission_router import router as userpermission_router
from .routers.usergroup_router import router as usergroup_router
from .routers.grouprole_router import router as grouprole_router
from .routers.auth_router import router as auth_router

routers = [
    user_router,
    role_router,
    permission_router,
    group_router,
    userrole_router,
    rolepermissions_router,
    userpermission_router,
    usergroup_router,
    grouprole_router,
    auth_router,
]


"""Auth models."""

# Import all models to ensure they're registered with SQLAlchemy
from .models.user import User
from .models.role import Role
from .models.group import Group
from .models.permission import Permission
from .models.rolepermission import RolePermission
from .models.userpermission import UserPermission
from .models.userrole import UserRole
from .models.usergroup import UserGroup
from .models.grouprole import GroupRole

__all__ = [
    "User",
    "Role",
    "Group",
    "Permission",
    "RolePermission",
    "UserPermission",
    "UserRole",
    "UserGroup",
    "GroupRole",
]
