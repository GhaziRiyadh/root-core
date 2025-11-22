from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.apps.auth.routers.user_router import get_user_repository
from core.apps.auth.utils.utils import Token, authenticate_user, create_access_token
from core.apps.auth.utils.utils import get_password_hash
from core.bases.base_router import BaseRouter
from core.config import PermissionAction
from core.config import settings
from core.response import handlers
from core.router import add_route
from ..schemas.user import UserCreate

resource_name = "auth"


class AuthRouter(BaseRouter):
    """Authentication router class."""

    _need_auth = False

    def __init__(self):
        super().__init__(
            tags=["Auth"],
            resource_name=resource_name,
        )

    @add_route(
        path="/token",
        method="POST",
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
