"""RolePermission service."""

from typing import Any, Dict
from core.bases.base_service import BaseService
from core.apps.auth.repositories.rolepermissions_repository import (
    RolePermissionRepository,
)
from core.apps.auth.models.rolepermission import RolePermission


class RolePermissionService(BaseService[RolePermission]):
    """RolePermission service class."""

    def __init__(self, repository: RolePermissionRepository):
        super().__init__(repository)

    async def _validate_create(self, create_data: Dict[str, Any]) -> None:
        """Validate data before creation."""
        # Add your business logic validation here
        pass

    async def _validate_update(
        self, item_id: Any, update_data: Dict[str, Any], existing_item: RolePermission
    ) -> None:
        """Validate data before update."""
        # Add your business logic validation here
        pass

    async def _validate_delete(
        self, item_id: Any, existing_item: RolePermission
    ) -> None:
        """Validate before soft delete."""
        # Add your business logic validation here
        pass

    async def _validate_force_delete(
        self, item_id: Any, existing_item: RolePermission
    ) -> None:
        """Validate before force delete."""
        # Add your business logic validation here
        pass
