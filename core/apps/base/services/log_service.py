"""Log service."""

from typing import Any, Dict
from src.core.bases.base_service import BaseService
from src.core.apps.base.repositories.log_repository import LogRepository
from src.core.apps.base.models.log import Log


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
