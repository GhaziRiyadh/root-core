"""Log service."""

from typing import Any, Dict
from core.bases.base_service import BaseService
from core.apps.base.repositories.log_repository import LogRepository
from core.apps.base.models.log import Log


class LogService(BaseService[Log]):
    """Log service class."""
    repository: LogRepository

    def __init__(self, repository: LogRepository):
        super().__init__(repository)

    async def _return_one_data(self, data: Log) -> dict:
        return {
            **data.model_dump(),
            "user": data.user.model_dump() if data.user else None,
        }
