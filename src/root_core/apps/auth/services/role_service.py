"""Role service."""

from typing import Any, Dict, List, Type

from sqlmodel import SQLModel
from root_core.bases.base_service import BaseService
from root_core.apps.auth.repositories.role_repository import RoleRepository
from root_core.apps.auth.models.role import Role
from root_core.schemas.fields import (
    DynamicFormConfig,
    FieldType,
    FieldValidation,
    ModelField,
    ModelLayoutItem,
)


class RoleService(BaseService[Role]):
    """Role service class."""

    def __init__(self, repository: RoleRepository):
        super().__init__(repository)

    async def _return_multi_data(self, data: List[Role | dict]):
        return await super()._return_multi_data(
            [
                {
                    **(role.model_dump() if isinstance(role, Role) else role),
                    "permissions": (
                        [perm.id for perm in role.permissions]
                        if isinstance(role, Role)
                        else role.get("permissions", [])
                    ),
                }
                for role in data
            ]
        )

    async def _validate_create(self, create_data: Dict[str, Any]) -> None:
        """Validate data before creation."""
        # Add your business logic validation here
        pass

    async def _validate_update(
        self, item_id: Any, update_data: Dict[str, Any], existing_item: Role
    ) -> None:
        """Validate data before update."""
        # Add your business logic validation here
        pass

    async def _validate_delete(self, item_id: Any, existing_item: Role) -> None:
        """Validate before soft delete."""
        # Add your business logic validation here
        pass

    async def _validate_force_delete(self, item_id: Any, existing_item: Role) -> None:
        """Validate before force delete."""
        # Add your business logic validation here
        pass

    def get_dynamic_form_config(self, model_class: type[SQLModel]) -> DynamicFormConfig:
        return DynamicFormConfig(
            model_name=model_class.__name__,
            fields=[
                ModelField(
                    default_value=None,
                    description="ادخل اسم الدور",
                    is_list=False,
                    is_relationship=False,
                    is_required=True,
                    name="name",
                    python_type="str",
                    relationship=None,
                    title="اسم الدور",
                    type=FieldType.STRING,
                    validation=FieldValidation(
                        max_length=50,
                        min_length=3,
                        required=True,
                    ),
                ),
                ModelField(
                    default_value=None,
                    description="ادخل وصف الدور",
                    is_list=False,
                    is_relationship=False,
                    is_required=True,
                    name="description",
                    python_type="str",
                    relationship=None,
                    title="وصف الدور",
                    type=FieldType.STRING,
                    validation=FieldValidation(
                        max_length=255,
                        min_length=3,
                    ),
                ),
            ],
            layout=[
                ModelLayoutItem(
                    name="name",
                    type=FieldType.STRING,
                    label="اسم الدور",
                    required=True,
                    placeholder="ادخل اسم الدور",
                    description="ادخل اسم الدور",
                ),
                ModelLayoutItem(
                    name="description",
                    type=FieldType.STRING,
                    label="وصف الدور",
                    required=True,
                    placeholder="ادخل وصف الدور",
                    description="ادخل وصف الدور",
                ),
            ],
            description=f"Dynamic form configuration for {model_class.__name__}",
            title=f"{model_class.__name__} Form",
            validation_rules={
                "name": {"required": True, "type": "string", "max_length": 50},
                "description": {"required": False, "type": "string", "max_length": 255},
            },
        )
