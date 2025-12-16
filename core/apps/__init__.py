from typing import TYPE_CHECKING
from fastapi import APIRouter, FastAPI

from core.apps.auth import routers as auth_routers
from core.apps.archive import routers as archive_routers
from core.apps.base import routers as base_routers


if TYPE_CHECKING:
    from core.bases.base_router import BaseRouter

routers = [
    *auth_routers,
    *archive_routers,
    *base_routers,
]