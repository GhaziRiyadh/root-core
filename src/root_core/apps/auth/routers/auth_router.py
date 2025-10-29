from datetime import timedelta
from typing import TYPE_CHECKING, Annotated

from fastapi.security import OAuth2PasswordRequestForm
from root_core.apps.auth.routers.user_router import get_user_repository
from root_core.apps.auth.schemas import user
from root_core.apps.auth.schemas.user import UserCreate
from root_core.apps.auth.utils.utils import Token, authenticate_user, create_access_token
from root_core.bases.base_router import BaseRouter
from root_core.config import PermissionAction
from root_core.response import handlers
from fastapi import Depends, HTTPException, status
from root_core.config import settings
from root_core.apps.auth.utils.utils import get_password_hash
from root_core.router import add_route

# if TYPE_CHECKING:
from ..schemas.user import UserCreate


def get_auth_service():
    pass


class AuthRouter(BaseRouter):
    """Authentication router class."""

    _need_auth = False

    def __init__(self):
        super().__init__(
            tags=["Auth"],
            resource_name="المصادقة",
        )

    @add_route(
        path="/token",
        method="post",
        action=PermissionAction.READ,
        description="Login and get access token",
    )
    async def login_for_access_token(
        self,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> Token:
        user = await authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"username": user.username}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    @add_route(
        path="/login",
        method="GET",
        action=PermissionAction.READ,
        description="Login with username and password",
    )
    async def login(self, username: str, password: str):
        print(username, password)
        user = await authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"username": user.username}, expires_delta=access_token_expires
        )
        return handlers.success_response(
            Token(access_token=access_token, token_type="bearer"),
            message="تم تسجيل الدخول بنجاح",
        )

    @add_route(
        path="/register",
        method="POST",
        action=PermissionAction.CREATE,
        description="Register a new user",
    )
    async def register(self, user: UserCreate):
        try:
            user_repo = get_user_repository()
            if user.password is None:
                user.password = "123"

            tmp_password = user.password
            hashed_password = get_password_hash(tmp_password)
            new_user = await user_repo.create(
                {
                    **user.model_dump(),
                    "password": hashed_password,
                }
            )
            if not new_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            access_token = create_access_token(
                data={"username": new_user.username}, expires_delta=access_token_expires
            )
            return handlers.success_response(
                Token(access_token=access_token, token_type="bearer"),
                message="تم تسجيل الدخول بنجاح",
            )
        except Exception as e:
            print(e)
            return handlers.error_response(error_code="ERROR", message=str(e))


router = AuthRouter()
