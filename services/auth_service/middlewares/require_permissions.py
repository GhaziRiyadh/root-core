from functools import wraps
from typing import Any, Callable, Dict, Optional, Set
import asyncio

from fastapi import HTTPException, status


from core.config import PermissionAction


def _to_action_str(action: Any) -> str:
    # Accept PermissionAction enum or plain string
    return action.value if hasattr(action, "value") else str(action)


def require_permissions(
    *actions: PermissionAction,
    resource: str,
    need_auth: bool = True,
    app_name: Optional[str] = None,
) -> Callable:
    """
    Decorator to protect FastAPI endpoint functions.

    Usage:
        @app.get("/protected")
        @require_permissions(PermissionAction.READ, resource="stuff",app_name="")
        async def endpoint(request: Request):
            ...

    Note: the decorated endpoint must accept a `request: Request` parameter.
    """

    required_actions: Set[str] = set(_to_action_str(a) for a in actions)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_coro = asyncio.iscoroutinefunction(func)

        # If authentication/authorization is not required, return a thin wrapper
        # that preserves function metadata and coroutine/sync behavior.
        if not need_auth:
            if is_coro:

                @wraps(func)
                async def _async_passthrough(*args: Any, **kwargs: Any) -> Any:
                    return await func(*args, **kwargs)

                return _async_passthrough
            else:

                @wraps(func)
                def _passthrough(*args: Any, **kwargs: Any) -> Any:
                    return func(*args, **kwargs)

                return _passthrough

        def _raise_unauthorized() -> None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )

        def _raise_forbidden() -> None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )

        def _user_permissions_set(
            user: Dict[str, Any],
            resource_name: str,
            app_name: Optional[str],
        ) -> Set[str]:
            perms = user.get("permissions", []) or []
            result = set()
            for perm in perms:
                resource = perm.get("resource", None)
                param_app_name = perm.get("app_name", None)
                if (
                    resource
                    and resource == resource_name
                    and (app_name is None or param_app_name == app_name)
                ):
                    try:
                        action = perm.get("action", None)
                    except Exception:
                        continue
                    result.add(
                        action
                        if isinstance(action, str)
                        else getattr(action, "value", str(action))
                    )
            return result

        from ...auth.utils.utils import auth

        if is_coro:

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                user = auth().user if auth() else None
                if user is None:
                    _raise_unauthorized()
                    return

                if user.get("is_superuser", False):
                    print(func, "func: ")
                    return await func(*args, **kwargs)

                user_permissions = _user_permissions_set(user, resource, app_name)
                print(
                    "User permissions:",
                    user_permissions,
                    "Required:",
                    required_actions,
                    actions,
                    resource,
                    app_name,
                )
                if not required_actions.issubset(user_permissions):
                    _raise_forbidden()

                return await func(*args, **kwargs)

            return async_wrapper

        else:

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:

                user = auth().user if auth() else None
                if user is None:
                    _raise_unauthorized()
                    return

                if user.get("is_superuser", False):
                    return func(*args, **kwargs)

                user_permissions = _user_permissions_set(user, resource, app_name)

                if not required_actions.issubset(user_permissions):
                    _raise_forbidden()

                return func(*args, **kwargs)

            return sync_wrapper

    return decorator
