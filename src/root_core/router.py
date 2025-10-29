# Decorator to mark endpoint methods with route metadata
from typing import Callable, Optional
from typing_extensions import Literal

from root_core.config import PermissionAction


def add_route(
    path: str,
    method: Literal[
        "get",
        "post",
        "put",
        "delete",
        "patch",
        "options",
        "head",
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
    Used as decorator on BaseRouter methods to register them as routes.

    Example:
    @add_route("/path", "get", PermissionAction.READ, summary="...")
    async def my_handler(self, ...): ...
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
