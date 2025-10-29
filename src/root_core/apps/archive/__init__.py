"""Archive app."""

from .routers.archive_router import router as archive_router
from .routers.file_router import router as file_router


routers = [archive_router, file_router]

from .routers.document_type_router import router as document_type_router

routers.append(document_type_router)
