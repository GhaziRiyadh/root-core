from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Tuple
import contextvars

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from sqlmodel import select

# from src.core.apps.auth.routers.permission_router import get_permission_repository
from src.core.config import settings
from src.core.database import get_session
from src.core.exceptions import NotFoundException
from sqlalchemy.orm import selectinload


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Auth(BaseModel):
    user: Optional[Dict[str, Any]] = None
    token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


_CACHE_TTL = 60 * 60  # seconds

# Improved cache: token -> (Auth, expire_time)
_AUTH_CACHE: Dict[str, Tuple[Auth, float]] = {}

# Context var to store the current request's Auth so synchronous code
# (or code not using FastAPI dependencies) can access the authenticated user
# via the `auth()` helper.
CURRENT_AUTH: contextvars.ContextVar[Optional[Auth]] = contextvars.ContextVar(
    "CURRENT_AUTH", default=None
)


def _get_cached_auth(token: str) -> Optional[Auth]:
    entry = _AUTH_CACHE.get(token)
    if entry:
        auth, expire_time = entry
        if expire_time > datetime.now().timestamp():
            return auth
        else:
            del _AUTH_CACHE[token]
    return None


def _set_cached_auth(token: str, auth: Auth):
    expire_time = datetime.now().timestamp()
    # expire_time = datetime.now().timestamp() + _CACHE_TTL
    _AUTH_CACHE[token] = (auth, expire_time)


def auth() -> Auth:
    """Return the current request Auth object.

    This is a synchronous helper that returns an Auth object with a `.user`
    attribute. It reads from a ContextVar which is set by the FastAPI
    dependency `get_current_user`. If no auth is set, an Auth with `user=None`
    and empty token is returned.
    """
    current = CURRENT_AUTH.get()
    if current is None:
        return Auth(user=None, token="")
    return current


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


async def get_user(username: Optional[str]) -> Optional[Any]:
    if not username:
        raise NotFoundException("Username is required")
    async with get_session() as session:
        user_model = __import__(settings.USER_MODEL, fromlist=["User"])
        stmt = (
            select(user_model.User)
            .where(user_model.User.username == username)
            .options(
                selectinload(user_model.User.groups),  # type:ignore
                selectinload(user_model.User.roles),  # type:ignore
                selectinload(user_model.User.permissions),  # type:ignore
            )
        )
        result = await session.exec(stmt)
        return result.first()


async def authenticate_user(username: str, password: str) -> Optional[Any]:
    user = await get_user(username)
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.

    Accepts either a dict with a 'sub' key or a 'username' key. Ensures the
    'sub' claim is a string (PyJWT requires a string subject) and includes an
    expiration ('exp').
    """
    to_encode = data.copy()
    expire = settings.get_now() + (expires_delta or timedelta(minutes=15))
    # Prefer explicit 'sub', fall back to 'username' for backwards-compatibility
    sub_value = data.get("sub") if data.get("sub") is not None else data.get("username")
    if sub_value is None:
        # No subject provided; encode without sub (decode will fail validation)
        sub_str = None
    else:
        # Ensure subject is a string (PyJWT expects a string for 'sub')
        sub_str = str(sub_value)

    # Use timestamp-aware datetime for exp (PyJWT handles datetimes)
    to_encode.update({"exp": expire})
    if sub_str is not None:
        to_encode.update({"sub": sub_str})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Any:
    cached_auth = _get_cached_auth(token)
    if cached_auth:
        # set context var so sync code can access the auth
        try:
            CURRENT_AUTH.set(cached_auth)
        except Exception:
            # If setting the context var fails for any reason, fall back to
            # returning the user; this should be rare.
            pass
        return cached_auth.user

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(username=username)
    if not user:
        raise credentials_exception

    # Cache the authenticated user
    auth_obj = Auth(user=user, token=token)
    _set_cached_auth(token, auth_obj)

    # set context var for synchronous access
    try:
        CURRENT_AUTH.set(auth_obj)
    except Exception:
        pass

    return user


async def get_current_user_or_none(request: Request) -> Any:
    try:
        token: str | None = await oauth2_scheme(request)
    except Exception as e:
        return None

    if not token:
        return None

    cached_auth = _get_cached_auth(token)
    if cached_auth:
        # set context var so sync code can access the auth
        try:
            CURRENT_AUTH.set(cached_auth)
            request.state.__setattr__("auth", cached_auth)
        except Exception:
            pass
        return cached_auth.user

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        username = payload.get("sub")
        if not username:
            return None
    except InvalidTokenError as e:
        return None
    user = await get_user(username=username)
    if not user:
        return None

    # Cache the authenticated user
    # Gather user permissions and permissions from all roles, avoiding duplicates
    permission_ids = set()
    permissions = list(user.permissions) if user.permissions else []

    # single query to fetch all permissions:
    # - permissions directly assigned to the user
    # - permissions assigned to any of the user's roles
    # - permissions assigned to roles that belong to any of the user's groups

    group_ids = (
        [g.id for g in getattr(user, "groups", [])]
        if getattr(user, "groups", [])
        else []
    )
    role_ids = (
        [r.id for r in getattr(user, "roles", [])] if getattr(user, "roles", []) else []
    )

    from ..models.permission import Permission
    from ..models.role import Role
    from ..models.user import User
    from ..models.group import Group

    query = (
        select(Permission)
        .where(
            (Permission.users.any(User.id == user.id))  # type: ignore
            | (Permission.roles.any(Role.id.in_(role_ids)))  # type: ignore
            | (Permission.roles.any(Role.groups.any(Group.id.in_(group_ids))))  # type: ignore
        )
        .distinct()
    )

    async with get_session() as session:
        result = await session.exec(query)
        permissions = result.all()

    # Remove duplicates by permission id
    unique_permissions = []
    for perm in permissions:
        if perm.id not in permission_ids:
            permission_ids.add(perm.id)
            unique_permissions.append(perm)

    auth_obj = Auth(
        user={
            **user.model_dump(exclude={"password"}),
            "roles": [
                role.model_dump(include={"name", "id"})
                for role in getattr(user, "roles", [])
            ],
            "groups": [
                group.model_dump(include={"name", "id"})
                for group in getattr(user, "groups", [])
            ],
            "permissions": [
                perm.model_dump(
                    include={
                        "action",
                        "id",
                        "resource",
                        "app_name",
                    }
                )
                for perm in unique_permissions
            ],
        },
        token=token,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )
    request.state.__setattr__("auth", auth_obj)
    _set_cached_auth(token, auth_obj)

    # set context var for synchronous access
    try:
        CURRENT_AUTH.set(auth_obj)
    except Exception:
        pass

    return user


async def initia_auth(current_user: Any = Depends(get_current_user_or_none)):
    """Return the current user or None if not authenticated or deleted."""
    if getattr(current_user, "is_deleted", False):
        return None
    return current_user


# async def get_current_active_user(
#     current_user: Any = Depends(get_current_user),
# ) -> Any:
#     if getattr(current_user, "is_deleted", False):
#         raise HTTPException(status_code=400, detail="Deleted user")
#     return current_user


def get_current_active_user():
    """Return the current active user or raise 400 if deleted."""
    current_user = auth().user
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO: add chaeck permission for user
    return current_user
