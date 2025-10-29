from typing import Callable, List, Optional, Type
from fastapi import APIRouter, FastAPI, Request, Depends
from pydantic import BaseModel

from root_core.apps.auth.middlewares.require_permissions import require_permissions
from root_core.bases.base_middleware import BaseMiddleware

from root_core.apps.auth.utils.utils import get_current_active_user
from root_core.utils.utils import get_current_app
import inspect
import os


class BaseRouter:
    """Base router class with automatic CRUD endpoints."""

    _need_auth: bool = True
    _middlewares: List[BaseMiddleware] = []
    _resource_name: str
    _app_name: Optional[str] = None

    def __init__(
        self,
        resource_name: str,
        tags: Optional[List[str]] = None,
        prefix: str = "",
        create_schema: Optional[Type[BaseModel]] = None,
        update_schema: Optional[Type[BaseModel]] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        dependencies: Optional[List[Callable]] = None,
        is_app: bool = False,
        app_name: Optional[str] = None,
    ):
        self._resource_name = resource_name
        self.tags = tags or [self.__class__.__name__.replace("Router", "")]
        self.prefix = prefix
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.response_schema = response_schema

        # determine app name from provided app_name or from the caller (not this base file)
        if app_name:
            self._app_name = app_name
            caller_file = None
        else:
            caller_file = None
            # walk the call stack to find the first file that's not this base router file
            for frame_info in inspect.stack()[1:]:
                fname = os.path.normpath(frame_info.filename)
                if fname != os.path.normpath(__file__):
                    caller_file = fname
                    break
            self._app_name = get_current_app(caller_file or __file__)

        if self._need_auth:
            # get_current_active_user
            if dependencies is None:
                dependencies = [Depends(get_current_active_user)]
            else:
                dependencies.append(Depends(get_current_active_user))

        if dependencies is None:
            dependencies = [Depends(self._router_middlewares)]
        else:
            dependencies.append(Depends(self._router_middlewares))

        # Create router
        if is_app:
            self.router = FastAPI(
                prefix=self.prefix,
                tags=self.tags,  # type:ignore
                dependencies=dependencies or [],  # type:ignore
                responses={404: {"description": "Not found"}},
            )
        else:
            self.router = APIRouter(
                prefix=self.prefix,
                tags=self.tags,  # type:ignore
                dependencies=dependencies or [],  # type:ignore
                responses={404: {"description": "Not found"}},
            )

        # Register all routes decorated with @add_route on the class
        self._register_routes()

    async def _router_middlewares(self, request: Request):
        """Return list of middlewares to apply to this router."""
        for middleware in self._middlewares:
            await middleware.dispatch(request, lambda req: req)

    def _register_routes(self) -> None:
        """Register all methods decorated with @add_route."""
        # Iterate class attributes to find decorated functions
        for name in dir(self.__class__):
            cls_attr = getattr(self.__class__, name)
            route_info = getattr(cls_attr, "_route_info", None)
            if not route_info:
                continue

            # get the bound method on this instance
            endpoint = getattr(self, name)

            # Wrap with permission middleware/decorator
            need_auth = (
                route_info["need_auth"]
                if route_info["need_auth"] is not None
                else self._need_auth
            )

            endpoint_to_register = require_permissions(
                route_info["action"],
                resource=self._resource_name,
                need_auth=need_auth,
                app_name=self._app_name,
            )(endpoint)

            router_method = getattr(
                self.router,
                str(route_info["method"]).lower(),
                None,
            )
            if not router_method:
                raise ValueError(f"Unsupported HTTP method: {route_info['method']}")

            router_method(route_info["path"], **route_info["kwargs"])(
                endpoint_to_register
            )

    def include_router(self, router: APIRouter, **kwargs) -> None:
        """Include another router in this router."""
        self.router.include_router(router, **kwargs)

    def get_router(self):
        """Get the FastAPI router instance."""
        return self.router

    def _register_custom_routes(self):
        """Hook for registering custom routes in subclasses."""
        pass
