"""Log repository."""

from root_core.bases.base_repository import BaseRepository
from root_core.apps.base.models.log import Log


class LogRepository(BaseRepository[Log]):
    """Log repository class."""

    model = Log
