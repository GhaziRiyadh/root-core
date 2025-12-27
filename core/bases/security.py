from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple, Set
import contextvars

import jwt
from fastapi import HTTPException, Request, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy.orm import selectinload

from core.config import settings
from core.database import get_session
from core.exceptions import NotFoundException


# Models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class Auth(BaseModel):
    user: Optional[Dict[str, Any]] = None
    token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


# Context & Globals
CURRENT_AUTH: contextvars.ContextVar[Optional[Auth]] = contextvars.ContextVar(
    "CURRENT_AUTH", default=None
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
password_hash = PasswordHash.recommended()
_CACHE_TTL = 60 * 60  # seconds
_AUTH_CACHE: Dict[str, Tuple[Auth, float]] = {}


class BaseSecurity(ABC):
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass

    @abstractmethod
    def get_password_hash(self, password: str) -> str:
        pass

    @abstractmethod
    async def get_user(self, username: Optional[str]) -> Optional[Any]:
        pass

    @abstractmethod
    async def authenticate_user(self, username: str, password: str) -> Optional[Any]:
        pass

    @abstractmethod
    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        pass

    @abstractmethod
    async def get_current_user(self, token: str) -> Any:
        pass

    @abstractmethod
    async def get_current_user_or_none(self, request: Request) -> Any:
        pass

    @abstractmethod
    def auth(self) -> Auth:
        pass


class DefaultSecurity(BaseSecurity):
    def _get_cached_auth(self, token: str) -> Optional[Auth]:
        entry = _AUTH_CACHE.get(token)
        if entry:
            auth, expire_time = entry
            if expire_time > datetime.now().timestamp():
                return auth
            else:
                del _AUTH_CACHE[token]
        return None

    def _set_cached_auth(self, token: str, auth: Auth):
        expire_time = datetime.now().timestamp()
        # expire_time = datetime.now().timestamp() + _CACHE_TTL
        _AUTH_CACHE[token] = (auth, expire_time)

    def auth(self) -> Auth:
        """Return the current request Auth object."""
        current = CURRENT_AUTH.get()
        if current is None:
            return Auth(user=None, token="")
        return current

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return password_hash.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return password_hash.hash(password)

    async def get_user(self, username: Optional[str]) -> Optional[Any]:
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

    async def authenticate_user(self, username: str, password: str) -> Optional[Any]:
        user = await self.get_user(username)
        if not user or not self.verify_password(password, user.password):
            return None
        return user

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        expire = settings.get_now() + (expires_delta or timedelta(minutes=15))
        sub_value = (
            data.get("sub") if data.get("sub") is not None else data.get("username")
        )
        if sub_value is None:
            sub_str = None
        else:
            sub_str = str(sub_value)

        to_encode.update({"exp": expire})
        if sub_str is not None:
            to_encode.update({"sub": sub_str})

        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def get_current_user(self, token: str) -> Any:
        cached_auth = self._get_cached_auth(token)
        if cached_auth:
            try:
                CURRENT_AUTH.set(cached_auth)
            except Exception:
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
        user = await self.get_user(username=username)
        if not user:
            raise credentials_exception

        auth_obj = Auth(user=user, token=token)
        self._set_cached_auth(token, auth_obj)

        try:
            CURRENT_AUTH.set(auth_obj)
        except Exception:
            pass

        return user

    async def get_current_user_or_none(self, request: Request) -> Any:
        try:
            # We use the global oauth2_scheme here effectively
            token: str | None = await oauth2_scheme(request)
        except Exception:
            return None

        if not token:
            return None

        cached_auth = self._get_cached_auth(token)
        if cached_auth:
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
        except InvalidTokenError:
            return None
        user = await self.get_user(username=username)
        if not user:
            return None

        # Gather permissions
        permission_ids = set()
        permissions = list(user.permissions) if user.permissions else []

        group_ids = (
            [g.id for g in getattr(user, "groups", [])]
            if getattr(user, "groups", [])
            else []
        )
        role_ids = (
            [r.id for r in getattr(user, "roles", [])]
            if getattr(user, "roles", [])
            else []
        )

        from core.apps.auth.models.permission import Permission
        from core.apps.auth.models.role import Role
        from core.apps.auth.models.user import User
        from core.apps.auth.models.group import Group

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
        self._set_cached_auth(token, auth_obj)

        try:
            CURRENT_AUTH.set(auth_obj)
        except Exception:
            pass

        return user
