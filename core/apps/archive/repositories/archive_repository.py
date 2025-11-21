"""Archive repository."""

from src.core.apps.archive.utils.Image_processor import AsyncImageProcessor
from src.core.apps.archive.utils.utils import get_file_type_by_extension
from src.core.bases.base_repository import BaseRepository
from src.core.apps.archive.models.archive import Archive
from src.core.apps.archive.models.file import File
from src.core.apps.archive.models.archive import Archive
from sqlalchemy.orm import selectinload

from pathlib import Path
import mimetypes

from src.core.apps.auth.utils.utils import auth


class ArchiveRepository(BaseRepository[Archive]):
    """Archive repository class."""

    model = Archive
    _search_fields = ["name", "original_path", "mime_type", "tags"]
    _options = [
        selectinload(Archive.files)  # type:ignore
    ]

    async def create_or_update_from_path(
        self,
        path: Path,
        id: int | None,
        file_name: str | None,
    ) -> Archive:
        """
        Creates or updates a file record from a given path.
        If updating, deletes old files before saving new versions.
        """
        stat = path.stat()  # Avoid multiple stat() calls
        mime_type = mimetypes.guess_type(path)[0] or "unknown"
        user = auth().user
        user_id = None
        if user:
            user_id = user.get("id", None)

        if not file_name:
            file_name = path.name

        async with self.get_session() as session:
            file_model = None
            if id is not None:
                file_model = await session.get(Archive, id)
                if file_model:
                    # Delete old files
                    for file in file_model.files:
                        try:
                            Path(file.src).unlink(missing_ok=True)
                        except Exception:
                            pass
                    file_model.files.clear()
                    file_model.name = file_name
                    file_model.original_path = str(path)
                    file_model.mime_type = mime_type
                    file_model.user_id
                    file_model.file_size = stat.st_size
                    file_model.file_type = get_file_type_by_extension(path)
                else:
                    file_model = Archive(
                        name=file_name,
                        original_path=str(path),
                        mime_type=mime_type,
                        user_id=user_id,
                        file_size=stat.st_size,
                        file_type=get_file_type_by_extension(path),
                    )
            else:
                file_model = Archive(
                    name=file_name,
                    original_path=str(path),
                    mime_type=mime_type,
                    user_id=user_id,
                    file_size=stat.st_size,
                    file_type=get_file_type_by_extension(path),
                )

            if file_model.file_type is not None and "image" in file_model.file_type:
                file_model = await self.process_image_versions(file_model, path)

            session.add(file_model)
            await session.commit()
            await session.refresh(file_model)

        archive = await self.get(file_model.id) if file_model.id else file_model
        if archive is None:
            raise Exception("Failed to retrieve the archive after creation/update.")

        return archive

    def filter_file_type(self, stmt, value):
        if isinstance(value, list):
            return stmt.where(
                *[Archive.file_type.ilike(f"%{v}%") for v in value]  # type:ignore
            )
        return stmt.where(
            Archive.file_type.ilike(f"%{value}%")  # type:ignore
        )

    async def process_image_versions(self, file_model: Archive, path: Path) -> Archive:
        """Handles image resizing and versioning."""
        version_paths = await AsyncImageProcessor.resize_and_save_all(path)

        for version_path in version_paths:
            file_model.files.append(
                File(
                    name=version_path.path.name,
                    src=str(version_path.path),
                    size=str(version_path.size),
                )
            )

        return file_model
