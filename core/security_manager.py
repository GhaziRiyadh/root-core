"""
Unified security manager class for authentication and authorization.

This module provides a single SecurityManager class that can be extended
to customize all security-related behavior.
"""

from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, Set, Tuple
from functools import wraps
import asyncio
import contextvars
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy.orm import selectinload

from core.config import settings, PermissionAction
from core.database import get_session
from core.exceptions import NotFoundException


# --- Models ---

class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """JWT token payload data."""
    username: Optional[str] = None


class Auth(BaseModel):
    """Authentication context containing user info and token."""
    user: Optional[Dict[str, Any]] = None
    token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


# --- Security Manager Class ---

class SecurityManager:
    """
    Unified security manager handling all authentication and authorization.
    
    This class can be extended to customize security behavior for different
    services or environments. All security-related functionality is contained
    in this single class.
    
    Example:
        # Use default implementation
        security = SecurityManager()
        
        # Or extend for custom behavior
        class CustomSecurity(SecurityManager):
            def check_permissions(self, ...):
                # Custom permission logic
                pass
    """
    
    def __init__(self):
        """Initialize the security manager."""
        # Password hashing
        self.password_hash = PasswordHash.recommended()
        
        # OAuth2 scheme
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        
        # Cache configuration
        self._cache_ttl = 60 * 60  # seconds
        self._auth_cache: Dict[str, Tuple[Auth, float]] = {}
        
        # Context variable for current auth
        self._current_auth: contextvars.ContextVar[Optional[Auth]] = contextvars.ContextVar(
            "CURRENT_AUTH", default=None
        )
    
    # --- Properties ---
    
    @property
    def user(self) -> Optional[Dict[str, Any]]:
        """Get the current authenticated user."""
        current = self._current_auth.get()
        if current is None:
            return None
        return current.user
    
    @property
    def token(self) -> str:
        """Get the current auth token."""
        current = self._current_auth.get()
        if current is None:
            return ""
        return current.token
    
    @property
    def auth_object(self) -> Auth:
        """Get the full Auth object."""
        current = self._current_auth.get()
        if current is None:
            return Auth(user=None, token="")
        return current
    
    # --- Auth Context Management ---
    
    def set_auth(self, auth_obj: Auth) -> None:
        """Set the current auth context."""
        self._current_auth.set(auth_obj)
    
    def clear_auth(self) -> None:
        """Clear the current auth context."""
        self._current_auth.set(None)
    
    # --- Cache Management ---
    
    def get_cached_auth(self, token: str) -> Optional[Auth]:
        """Get cached authentication for a token."""
        entry = self._auth_cache.get(token)
        if entry:
            auth, expire_time = entry
            if expire_time > datetime.now().timestamp():
                return auth
            else:
                del self._auth_cache[token]
        return None
    
    def set_cached_auth(self, token: str, auth: Auth) -> None:
        """Cache authentication for a token."""
        expire_time = datetime.now().timestamp() + self._cache_ttl
        self._auth_cache[token] = (auth, expire_time)
    
    # --- Password Management ---
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return self.password_hash.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return self.password_hash.hash(password)
    
    # --- Token Management ---
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = settings.get_now() + (expires_delta or timedelta(minutes=15))
        sub_value = data.get("sub") if data.get("sub") is not None else data.get("username")
        sub_str = str(sub_value) if sub_value is not None else None
        
        to_encode.update({"exp": expire})
        if sub_str is not None:
            to_encode.update({"sub": sub_str})
        
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # --- User Management ---
    
    async def get_user(self, username: Optional[str]) -> Optional[Any]:
        """Get a user by username.
        
        Override this method to customize user retrieval logic.
        """
        if settings.GET_USER_FUNCTION:
            return await settings.GET_USER_FUNCTION(username)
        if not username:
            raise NotFoundException("Username is required")
        async with get_session() as session:
            user_model = __import__(settings.USER_MODEL, fromlist=["User"])
            stmt = (
                select(user_model.User)
                .where(user_model.User.username == username)
                .options(
                    selectinload(user_model.User.groups),
                    selectinload(user_model.User.roles),
                    selectinload(user_model.User.permissions),
                )
            )
            result = await session.exec(stmt)
            return result.first()
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Any]:
        """Authenticate a user with username and password.
        
        Override this method to customize authentication logic.
        """
        user = await self.get_user(username)
        if not user or not self.verify_password(password, user.password):
            return None
        return user
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> Any:
        """Get the current authenticated user from a JWT token."""
        cached_auth = self.get_cached_auth(token)
        if cached_auth:
            try:
                self._current_auth.set(cached_auth)
                self.set_auth(cached_auth)
            except Exception:
                pass
            return cached_auth.user

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username = payload.get("sub")
            if not username:
                raise credentials_exception
        except InvalidTokenError:
            raise credentials_exception
        user = await self.get_user(username=username)
        if not user:
            raise credentials_exception

        auth_obj = Auth(user=user, token=token)
        self.set_cached_auth(token, auth_obj)
        try:
            self._current_auth.set(auth_obj)
            self.set_auth(auth_obj)
        except Exception:
            pass
        return user
    
    async def get_current_user_or_none(self, request: Request) -> Any:
        """Get the current user or None if not authenticated."""
        try:
            token: str | None = await self.oauth2_scheme(request)
        except Exception:
            return None

        if not token:
            return None

        cached_auth = self.get_cached_auth(token)
        if cached_auth:
            try:
                self._current_auth.set(cached_auth)
                self.set_auth(cached_auth)
                request.state.__setattr__("auth", cached_auth)
            except Exception:
                pass
            return cached_auth.user

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username = payload.get("sub")
            if not username:
                return None
        except InvalidTokenError:
            return None
        user = await self.get_user(username=username)
        if not user:
            return None

        auth_obj = Auth(
            user=user,
            token=token,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
        )
        request.state.__setattr__("auth", auth_obj)
        self.set_cached_auth(token, auth_obj)
        try:
            self._current_auth.set(auth_obj)
            self.set_auth(auth_obj)
        except Exception:
            pass
        return user
    
    def get_current_active_user(self):
        """Return the current active user or raise 401 if not authenticated."""
        current_user = self.user
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return current_user
    
    # --- Permission Management ---
    
    def check_permissions(
        self,
        required_actions: Set[str],
        resource: str,
        app_name: Optional[str] = None
    ) -> bool:
        """Check if the current user has the required permissions.
        
        Override this method to customize permission checking logic.
        """
        user = self.user
        if not user:
            return False
        
        # Check if user is superuser
        is_superuser = user.get("is_superuser", False) if isinstance(user, dict) else getattr(user, "is_superuser", False)
        if is_superuser:
            return True
        
        # Get user permissions
        user_permissions = self._get_user_permissions(user, resource, app_name)
        return required_actions.issubset(user_permissions)
    
    def _get_user_permissions(self, user: Any, resource: str, app_name: Optional[str]) -> Set[str]:
        """Extract user permissions for a given resource.
        
        Override this method to customize permission extraction.
        """
        perms = user.get("permissions", []) if isinstance(user, dict) else getattr(user, "permissions", [])
        result = set()
        for perm in perms:
            p_resource = perm.get("resource") if isinstance(perm, dict) else getattr(perm, "resource", None)
            p_app_name = perm.get("app_name") if isinstance(perm, dict) else getattr(perm, "app_name", None)
            
            if p_resource == resource and (app_name is None or p_app_name == app_name):
                action = perm.get("action") if isinstance(perm, dict) else getattr(perm, "action", None)
                result.add(action if isinstance(action, str) else getattr(action, "value", str(action)))
        return result
    
    def require_permissions(
        self,
        *actions: PermissionAction,
        resource: str,
        need_auth: bool = True,
        app_name: Optional[str] = None,
    ) -> Callable:
        """Decorator to require specific permissions for an endpoint.
        
        This method returns a decorator that can be used on endpoints.
        """
        required_actions: Set[str] = set(
            action.value if hasattr(action, "value") else str(action) 
            for action in actions
        )

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            is_coro = asyncio.iscoroutinefunction(func)

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
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

            def _raise_forbidden() -> None:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

            if is_coro:
                @wraps(func)
                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    if self.user is None:
                        _raise_unauthorized()
                        return

                    if not self.check_permissions(required_actions, resource, app_name):
                        _raise_forbidden()

                    return await func(*args, **kwargs)
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                    if self.user is None:
                        _raise_unauthorized()
                        return

                    if not self.check_permissions(required_actions, resource, app_name):
                        _raise_forbidden()

                    return func(*args, **kwargs)
                return sync_wrapper
        return decorator


# --- Global Instance ---

_security_instance: Optional[SecurityManager] = None


def get_security_class() -> type[SecurityManager]:
    """Get the configured security class from settings."""
    from importlib import import_module
    
    class_path = settings.AUTH_CLASS
    module_path, class_name = class_path.rsplit('.', 1)
    module = import_module(module_path)
    security_class = getattr(module, class_name)
    
    if not issubclass(security_class, SecurityManager):
        raise ValueError(f"AUTH_CLASS must be a subclass of SecurityManager, got {security_class}")
    
    return security_class


def security() -> SecurityManager:
    """Get the global security manager instance.
    
    The security class can be configured via settings.AUTH_CLASS.
    
    Example:
        user = security().user
        token = security().token
        security().check_permissions(...)
    """
    global _security_instance
    
    if _security_instance is None:
        security_class = get_security_class()
        _security_instance = security_class()
    
    return _security_instance


# --- Backward Compatibility Exports ---

def auth() -> SecurityManager:
    """Alias for security() for backward compatibility."""
    return security()


# Export commonly used functions for convenience
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password."""
    return security().verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return security().get_password_hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create an access token."""
    return security().create_access_token(data, expires_delta)


async def get_user(username: Optional[str]) -> Optional[Any]:
    """Get a user by username."""
    return await security().get_user(username)


async def authenticate_user(username: str, password: str) -> Optional[Any]:
    """Authenticate a user."""
    return await security().authenticate_user(username, password)


async def get_current_user(token: str = Depends(lambda: security().oauth2_scheme)) -> Any:
    """Get the current user."""
    return await security().get_current_user(token)


async def get_current_user_or_none(request: Request) -> Any:
    """Get the current user or None."""
    return await security().get_current_user_or_none(request)


def get_current_active_user():
    """Get the current active user."""
    return security().get_current_active_user()


def require_permissions(
    *actions: PermissionAction,
    resource: str,
    need_auth: bool = True,
    app_name: Optional[str] = None,
) -> Callable:
    """Require permissions decorator."""
    return security().require_permissions(*actions, resource=resource, need_auth=need_auth, app_name=app_name)


# Export for backward compatibility
BaseAuth = SecurityManager
DefaultAuth = SecurityManager
