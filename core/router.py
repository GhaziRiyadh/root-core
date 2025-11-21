# Decorator to mark endpoint methods with route metadata
from typing import Callable, Optional
from typing_extensions import Literal

from src.core.config import PermissionAction


def add_route(
    path: str,
    method: Literal[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "OPTIONS",
        "HEAD",
    ],
    action: PermissionAction,
    need_auth: Optional[bool] = None,
    **kwargs,
):
    """
    Used as a decorator on BaseRouter methods to register them as routes.
    
    Parameters:
        path (str): The URL path for the route (e.g., "/users" or "/items/{item_id}")
        method (str): The HTTP method for the route ("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD")
        action (PermissionAction): The permission action required for this route
        need_auth (Optional[bool]): Whether authentication is required for this route. If None, defaults to system settings
        **kwargs: Additional keyword arguments to pass to the route registration (e.g., summary, description, tags)

    Example:
    >>>@add_route("/path", "GET", PermissionAction.READ, summary="...")
    >>>async def my_handler(self, ...): ...
    """

    def decorator(func: Callable) -> Callable:
        setattr(
            func,
            "_route_info",
            {
                "path": path,
                "method": method.lower(),
                "action": action,
                "need_auth": need_auth,
                "kwargs": kwargs or {},
            },
        )
        return func

    return decorator
