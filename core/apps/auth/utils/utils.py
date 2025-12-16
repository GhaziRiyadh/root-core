from datetime import timedelta
from typing import Any, Optional, Dict
import importlib

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from core.config import settings
from .security import (
    BaseSecurity,
    Token,
    TokenData,
    Auth,
    oauth2_scheme,
    CURRENT_AUTH,
    password_hash,
)


# Load Security Class
def get_security_class() -> BaseSecurity:
    module_name, class_name = settings.SECURITY_CLASS.rsplit(".", 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cls()


security = get_security_class()


def auth() -> Auth:
    """Return the current request Auth object."""
    return security.auth()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return security.verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return security.get_password_hash(password)


async def get_user(username: Optional[str]) -> Optional[Any]:
    return await security.get_user(username)


async def authenticate_user(username: str, password: str) -> Optional[Any]:
    return await security.authenticate_user(username, password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return security.create_access_token(data, expires_delta)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Any:
    return await security.get_current_user(token)


async def get_current_user_or_none(request: Request) -> Any:
    return await security.get_current_user_or_none(request)


async def initia_auth(current_user: Any = Depends(get_current_user_or_none)):
    """Return the current user or None if not authenticated or deleted."""
    if getattr(current_user, "is_deleted", False):
        return None
    return current_user


def get_current_active_user():
    """Return the current active user or raise 401 if deleted."""
    current_user = auth().user
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO: add chaeck permission for user
    return current_user
