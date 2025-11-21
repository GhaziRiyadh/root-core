"""User schemas."""

from typing import Any, List, Optional, Annotated
from pydantic import BaseModel, Field, AfterValidator


def validate_password_strength(v: str) -> str:
    if len(v) < 8:
        raise ValueError("يجب أن تكون كلمة المرور 8 أحرف على الأقل")
    if not any(char.isdigit() for char in v):
        raise ValueError("يجب أن تحتوي كلمة المرور على رقم واحد على الأقل")
    if not any(char.isupper() for char in v):
        raise ValueError("يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل")
    return v


class UserCreate(BaseModel):
    """Schema for creating a user."""

    username: str = Field(max_length=100)
    # password: Annotated[str, AfterValidator(validate_password_strength)]
    name: str
    is_superuser: Optional[bool] = Field(default=False)

    # relations
    roles: List[Any] = Field(default_factory=list, description="List of role IDs")
    groups: List[Any] = Field(default_factory=list, description="List of group IDs")
    permissions: List[Any] = Field(
        default_factory=list, description="List of permission IDs"
    )
    phone: Optional[str] = None
    email: Optional[str] = None

    password: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    username: Optional[str] = None
    # password: Annotated[Optional[str], AfterValidator(validate_password_strength)]
    name: Optional[str] = None
    is_superuser: Optional[bool] = None

    roles: List[int] = Field(default_factory=list, description="List of role IDs")
    groups: List[int] = Field(default_factory=list, description="List of group IDs")
    permissions: List[int] = Field(
        default_factory=list, description="List of permission IDs"
    )
    phone: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
