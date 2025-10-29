"""User router."""

from typing import TYPE_CHECKING, Annotated, Any
from fastapi import Depends
from root_core.bases.crud_api import CRUDApi
from root_core.database import get_session
from root_core.router import add_route
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserCreate, UserUpdate
from root_core.response import handlers
from ..utils.utils import (
    get_current_active_user,
)
from root_core.config import PermissionAction

if TYPE_CHECKING:
    from ..models.user import User

resource_name = "المستخدمين"


def get_user_repository():
    """Get user repository instance."""
    return UserRepository(get_session)  # type:ignore


def get_user_service():
    """Get user service instance."""
    repository = get_user_repository()
    return UserService(repository)


class UserRouter(CRUDApi):
    """User router class."""

    _need_auth = True

    def __init__(self):
        super().__init__(
            service=get_user_service(),
            create_schema=UserCreate,
            update_schema=UserUpdate,
            prefix="/users",
            tags=["Users"],
            resource_name=resource_name,
        )

    @add_route(
        path="/me",
        method="get",
        action=PermissionAction.READ,
        description="Get current user details",
        need_auth=False,
    )
    async def read_users_me(
        self,
        user: Annotated[Any, Depends(get_current_active_user)],
    ):
        """Get current user details."""
        return handlers.success_response(user)


# Router instance
router = UserRouter()
