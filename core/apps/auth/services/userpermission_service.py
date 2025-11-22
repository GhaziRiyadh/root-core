"""UserPermission service."""

from typing import Any, Dict
from core.bases.base_service import BaseService
from core.apps.auth.repositories.userpermission_repository import (
    UserPermissionRepository,
)
from core.apps.auth.models.userpermission import UserPermission


class UserPermissionService(BaseService[UserPermission]):
    """UserPermission service class."""

    def __init__(self, repository: UserPermissionRepository):
        super().__init__(repository)

    async def _validate_create(self, create_data: Dict[str, Any]) -> None:
        """Validate data before creation."""
        # Add your business logic validation here
        pass

    async def _validate_update(
        self, item_id: Any, update_data: Dict[str, Any], existing_item: UserPermission
    ) -> None:
        """Validate data before update."""
        # Add your business logic validation here
        pass

    async def _validate_delete(
        self, item_id: Any, existing_item: UserPermission
    ) -> None:
        """Validate before soft delete."""
        # Add your business logic validation here
        pass

    async def _validate_force_delete(
        self, item_id: Any, existing_item: UserPermission
    ) -> None:
        """Validate before force delete."""
        # Add your business logic validation here
        pass
