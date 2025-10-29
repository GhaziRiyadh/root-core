"""Permission service."""

from typing import Any, Dict
from root_core.bases.base_service import BaseService
from root_core.apps.auth.repositories.permission_repository import PermissionRepository
from root_core.apps.auth.models.permission import Permission


class PermissionService(BaseService[Permission]):
    """Permission service class."""

    def __init__(self, repository: PermissionRepository):
        super().__init__(repository)

    async def _validate_create(self, create_data: Dict[str, Any]) -> None:
        """Validate data before creation."""
        # Add your business logic validation here
        pass

    async def _validate_update(
        self, item_id: Any, update_data: Dict[str, Any], existing_item: Permission
    ) -> None:
        """Validate data before update."""
        # Add your business logic validation here
        pass

    async def _validate_delete(self, item_id: Any, existing_item: Permission) -> None:
        """Validate before soft delete."""
        # Add your business logic validation here
        pass

    async def _validate_force_delete(
        self, item_id: Any, existing_item: Permission
    ) -> None:
        """Validate before force delete."""
        # Add your business logic validation here
        pass
