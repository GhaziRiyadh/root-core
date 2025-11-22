"""UserGroup service."""

from typing import Any, Dict
from core.bases.base_service import BaseService
from core.apps.auth.repositories.usergroup_repository import UserGroupRepository
from core.apps.auth.models.usergroup import UserGroup


class UserGroupService(BaseService[UserGroup]):
    """UserGroup service class."""

    def __init__(self, repository: UserGroupRepository):
        super().__init__(repository)

    async def _validate_create(self, create_data: Dict[str, Any]) -> None:
        """Validate data before creation."""
        # Add your business logic validation here
        pass

    async def _validate_update(
        self, item_id: Any, update_data: Dict[str, Any], existing_item: UserGroup
    ) -> None:
        """Validate data before update."""
        # Add your business logic validation here
        pass

    async def _validate_delete(self, item_id: Any, existing_item: UserGroup) -> None:
        """Validate before soft delete."""
        # Add your business logic validation here
        pass

    async def _validate_force_delete(
        self, item_id: Any, existing_item: UserGroup
    ) -> None:
        """Validate before force delete."""
        # Add your business logic validation here
        pass
