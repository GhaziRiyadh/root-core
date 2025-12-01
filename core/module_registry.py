"""
Module Registry for Modular Monolith Architecture.

This module provides automatic discovery and registration of application modules.
Each module can register its routers, models, and services.
"""

from typing import TYPE_CHECKING, List
from fastapi import APIRouter, FastAPI

if TYPE_CHECKING:
    from core.bases.base_router import BaseRouter


def get_all_routers() -> List["BaseRouter"]:
    """
    Dynamically discover and return all routers from registered modules.
    
    Returns:
        List of BaseRouter instances from all modules
    """
    from core.apps.auth import routers as auth_routers
    from core.apps.archive import routers as archive_routers
    from core.apps.base import routers as base_routers

    return [
        *auth_routers,
        *archive_routers,
        *base_routers,
    ]


def handle_router(app: FastAPI, router: "BaseRouter") -> None:
    """
    Register a single router with the FastAPI application.
    
    Args:
        app: FastAPI application instance
        router: BaseRouter instance to register
    """
    route = router.get_router()
    if isinstance(route, APIRouter):
        app.include_router(route)
    elif isinstance(route, FastAPI):
        app.mount(router.prefix, route)


def handle_routers(app: FastAPI) -> None:
    """
    Register all discovered routers with the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    routers = get_all_routers()
    for router in routers:
        handle_router(app, router)


__all__ = ["get_all_routers", "handle_router", "handle_routers"]
