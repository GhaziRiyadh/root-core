"""Log repository."""
from sqlalchemy.orm import selectinload

from core.bases.base_repository import BaseRepository
from core.apps.base.models.log import Log


class LogRepository(BaseRepository[Log]):
    """Log repository class."""

    model = Log
    _search_fields = ["action"]
    _options = [
        selectinload(Log.user)  # type:ignore
    ]
