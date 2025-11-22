"""Permission schemas."""

from typing import Optional
from pydantic import BaseModel

from core.apps.auth.utils.enums import PermissionActions


class PermissionCreate(BaseModel):
    """Schema for creating a permission."""

    resource: str
    action: PermissionActions

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class PermissionUpdate(BaseModel):
    """Schema for updating a permission."""

    resource: Optional[str] = None
    action: Optional[PermissionActions] = None

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
