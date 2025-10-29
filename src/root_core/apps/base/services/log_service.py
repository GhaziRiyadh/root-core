"""Log service."""

from typing import Any, Dict
from root_core.bases.base_service import BaseService
from root_core.apps.base.repositories.log_repository import LogRepository
from root_core.apps.base.models.log import Log


class LogService(BaseService[Log]):
    """Log service class."""

    def __init__(self, repository: LogRepository):
        super().__init__(repository)

    async def _validate_create(self, create_data: Dict[str, Any]) -> None:
        """Validate data before creation."""
        # Add your business logic validation here
        pass

    async def _validate_update(
        self, item_id: Any, update_data: Dict[str, Any], existing_item: Log
    ) -> None:
        """Validate data before update."""
        # Add your business logic validation here
        pass

    async def _validate_delete(self, item_id: Any, existing_item: Log) -> None:
        """Validate before soft delete."""
        # Add your business logic validation here
        pass

    async def _validate_force_delete(self, item_id: Any, existing_item: Log) -> None:
        """Validate before force delete."""
        # Add your business logic validation here
        pass
