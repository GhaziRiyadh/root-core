"""File repository."""

from root_core.bases.base_repository import BaseRepository
from root_core.apps.archive.models.file import File


class FileRepository(BaseRepository[File]):
    """File repository class."""

    model = File

    _search_fields = ["name", "type", "tags"]
