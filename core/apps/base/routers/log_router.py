"""Log router."""

from core.bases.crud_api import CRUDApi
from core.database import get_session
from core.apps.base.services.log_service import LogService
from core.apps.base.repositories.log_repository import LogRepository
from core.apps.base.schemas.log import LogCreate, LogUpdate

resource_name: str = "logs"


def get_log_repository():
    """Get log repository instance."""
    return LogRepository(get_session)  # type:ignore


def get_log_service():
    """Get log service instance."""
    repository = get_log_repository()
    return LogService(repository)


class LogRouter(CRUDApi):
    """Log router class."""

    def __init__(self):
        super().__init__(
            service=get_log_service(),
            create_schema=LogCreate,
            update_schema=LogUpdate,
            tags=["Logs"],
            resource_name=resource_name,
        )


# Router instance
router = LogRouter()
