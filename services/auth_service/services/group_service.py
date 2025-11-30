"""Group service."""

from typing import Any, Dict, List

from sqlmodel import SQLModel
from ..schemas.group import GroupCreate
from core.bases.base_service import BaseService
from ..repositories.group_repository import GroupRepository
from ..models.group import Group
from core.schemas.fields import (
    DynamicFormConfig,
    FieldType,
    FieldValidation,
    ModelField,
    ModelLayoutItem,
    RelationshipInfo,
    RelationshipType,
)


class GroupService(BaseService[Group]):
    """Group service class."""

    def __init__(self, repository: GroupRepository):
        super().__init__(repository)

    async def _return_multi_data(self, data: List[Group | dict]):
        return await super()._return_multi_data(
            [
                {
                    **(group.model_dump() if isinstance(group, Group) else group),
                    "roles": (
                        [role.id for role in group.roles]
                        if isinstance(group, Group)
                        else group.get("roles", [])
                    ),
                }
                for group in data
            ]
        )

    async def create(self, obj_in: GroupCreate, **additional_data) -> Dict[str, Any]:
        from ..routers.role_router import get_role_repository

        role_repo = get_role_repository()
        async with role_repo.get_session() as session:
            role_res = await session.exec(
                role_repo._build_select_stmt().where(
                    role_repo.model.id.in_(obj_in.roles),  # type:ignore
                )
            )
            obj_in.roles = role_res.all()  # type:ignore

        return await super().create(obj_in, roles=obj_in.roles)

    async def _validate_create(self, create_data: Dict[str, Any]) -> None:
        """Validate data before creation."""
        # Add your business logic validation here
        pass

    async def _validate_update(
        self, item_id: Any, update_data: Dict[str, Any], existing_item: Group
    ) -> None:
        """Validate data before update."""
        # Add your business logic validation here
        pass

    async def _validate_delete(self, item_id: Any, existing_item: Group) -> None:
        """Validate before soft delete."""
        # Add your business logic validation here
        pass

    async def _validate_force_delete(self, item_id: Any, existing_item: Group) -> None:
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
                # add roles
                # roles
                ModelField(
                    default_value=[],
                    description="ادخل الأدوار",
                    is_list=True,
                    is_relationship=True,
                    is_required=False,
                    name="roles",
                    python_type="List[int]",
                    title="الأدوار",
                    type=FieldType.LIST,
                    validation=FieldValidation(),
                    relationship=RelationshipInfo(
                        type=RelationshipType.MANY_TO_MANY,
                        related_model="Role",
                        related_field="id",
                        description="Foreign key to User",
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
                ModelLayoutItem(
                    name="roles",
                    type=FieldType.LIST,
                    label="الأدوار",
                    required=False,
                    placeholder="ادخل الأدوار",
                    description="ادخل الأدوار",
                ),
            ],
            description=f"Dynamic form configuration for {model_class.__name__}",
            title=f"{model_class.__name__} Form",
            validation_rules={
                "name": {"required": True, "type": "string", "max_length": 50},
                "description": {"required": False, "type": "string", "max_length": 255},
            },
        )
