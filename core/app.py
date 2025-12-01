from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_babel import BabelConfigs, BabelMiddleware
from sqlmodel import select
import os
from pathlib import Path

from core.config import settings
from core.database import get_session
from core.response.handlers import global_exception_handler
from core.apps.auth.utils.utils import initia_auth
from core.module_registry import handle_routers


class CoreApp:
    def __init__(
        self,
        title: str = settings.PROJECT_NAME,
        description: str = settings.PROJECT_INFO,
        version: str = settings.PROJECT_VERSION,
        lifespan=None,
        dependencies: Optional[List[Any]] = None,
        openapi_tags: Optional[List[Dict[str, Any]]] = None,
        enable_cors: bool = True,
        enable_babel: bool = True,
        static_files_mount: Optional[str] = "/uploads",
        static_files_dir: Optional[str] = settings.UPLOAD_FOLDER,
    ):
        self.title = title
        self.description = description
        self.version = version
        self.lifespan = lifespan or self._default_lifespan
        self.dependencies = dependencies or [Depends(initia_auth)]
        self.openapi_tags = openapi_tags or [
            {
                "name": "Health",
                "description": "Health check endpoints for the API",
            },
            {
                "name": "Authentication",
                "description": "Endpoints related to user authentication and authorization",
            },
        ]
        self.enable_cors = enable_cors
        self.enable_babel = enable_babel
        self.static_files_mount = static_files_mount
        self.static_files_dir = static_files_dir

        self.app = FastAPI(
            title=self.title,
            description=self.description,
            version=self.version,
            lifespan=self.lifespan,
            dependencies=self.dependencies,
            openapi_tags=self.openapi_tags,
        )

        self._configure_middleware()
        self._configure_exception_handlers()
        self._configure_routes()
        self._configure_static_files()

    @asynccontextmanager
    async def _default_lifespan(self, app: FastAPI):
        # Startup: Create database tables
        async with get_session() as session:
            await session.exec(select(1))
        print("✅ Database connection succecfully")
        yield
        # Shutdown: Clean up resources if needed
        print("🔄 Shutting down...")

    def _configure_middleware(self):
        if self.enable_babel:
            configs = BabelConfigs(
                ROOT_DIR=os.path.dirname(__file__),
                BABEL_DEFAULT_LOCALE="ar",
                BABEL_TRANSLATION_DIRECTORY="locales",
            )
            self.app.add_middleware(BabelMiddleware, babel_configs=configs)

        if self.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],  # Adjust in production
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    def _configure_exception_handlers(self):
        self.app.add_exception_handler(Exception, global_exception_handler)

    def _configure_routes(self):
        # Health check endpoint
        @self.app.get("/", tags=["Health"])
        async def root():
            """Root endpoint with health check."""
            return {
                "message": "🚀 Server is running!",
                "status": "healthy",
                "version": self.version,
            }

        @self.app.get("/health", tags=["Health"])
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "message": "Service is running normally"}

        # Include app routers
        handle_routers(self.app)

    def _configure_static_files(self):
        if self.static_files_mount and self.static_files_dir:
            upload_dir = Path(self.static_files_dir).resolve()
            upload_dir.mkdir(parents=True, exist_ok=True)

            self.app.mount(
                self.static_files_mount,
                StaticFiles(directory=upload_dir),
                name="uploads",
            )

    def get_app(self) -> FastAPI:
        return self.app
