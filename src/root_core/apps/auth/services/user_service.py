"""User service."""

from typing import Any, Dict, List

from sqlmodel import SQLModel
from root_core.apps.auth.schemas.user import UserCreate
from root_core.bases.base_service import BaseService
from root_core.apps.auth.repositories.user_repository import UserRepository
from root_core.apps.auth.models.user import User
from root_core.schemas.fields import (
    DynamicFormConfig,
    FieldType,
    FieldValidation,
    ModelField,
    ModelLayoutItem,
    RelationshipInfo,
    RelationshipType,
)


class UserService(BaseService[User]):
    """User service class."""

    def __init__(self, repository: UserRepository):
        super().__init__(repository)

    async def _return_multi_data(self, data: List[User]):  # type:ignore
        dict_data = [
            {
                **user.model_dump(exclude={"password"}),
                "roles": [role.id for role in user.roles],
                "groups": [group.id for group in user.groups],
                "permissions": [perm.id for perm in user.permissions],
            }
            for user in data
        ]
        return await super()._return_multi_data(dict_data)  # type:ignore

    async def create(self, obj_in: UserCreate, **additional_data) -> Dict[str, Any]:
        from ..routers.role_router import get_role_repository

        role_repo = get_role_repository()
        async with role_repo.get_session() as session:
            role_res = await session.exec(
                role_repo._build_select_stmt().where(
                    role_repo.model.id.in_(obj_in.roles),  # type:ignore
                )
            )
            obj_in.roles = role_res.all()  # type:ignore

        from ..routers.group_router import get_group_repository

        group_repo = get_group_repository()
        async with group_repo.get_session() as session:
            res = await session.exec(
                group_repo._build_select_stmt().where(
                    group_repo.model.id.in_(obj_in.groups),  # type:ignore
                )
            )
            obj_in.groups = res.all()  # type:ignore

        return await super().create(obj_in, groups=obj_in.groups, roles=obj_in.roles)

    async def _validate_create(self, create_data: Dict[str, Any]) -> None:
        """Validate data before creation."""
        pass

    async def _validate_update(
        self, item_id: Any, update_data: Dict[str, Any], existing_item: User
    ) -> None:
        """Validate data before update."""
        # Add your business logic validation here
        pass

    async def _validate_delete(self, item_id: Any, existing_item: User) -> None:
        """Validate before soft delete."""
        # Add your business logic validation here
        pass

    async def _validate_force_delete(self, item_id: Any, existing_item: User) -> None:
        """Validate before force delete."""
        # Add your business logic validation here
        pass

    def get_dynamic_form_config(self, model_class: type[SQLModel]) -> DynamicFormConfig:
        return DynamicFormConfig(
            model_name=model_class.__name__,
            fields=[
                ModelField(
                    default_value=None,
                    description="ادخل اسم المستخدم",
                    is_list=False,
                    is_relationship=False,
                    is_required=True,
                    name="name",
                    python_type="str",
                    relationship=None,
                    title="الاسم",
                    type=FieldType.STRING,
                    validation=FieldValidation(
                        max_length=50,
                        min_length=3,
                        required=True,
                    ),
                ),
                ModelField(
                    default_value=None,
                    description="ادخل اسم المستخدم",
                    is_list=False,
                    is_relationship=False,
                    is_required=True,
                    name="username",
                    python_type="str",
                    relationship=None,
                    title="اسم المستخدم",
                    type=FieldType.STRING,
                    validation=FieldValidation(
                        max_length=255,
                        min_length=3,
                        required=True,
                    ),
                ),
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
                # groups
                ModelField(
                    default_value=[],
                    description="ادخل المجموعات",
                    is_list=True,
                    is_relationship=True,
                    is_required=False,
                    name="groups",
                    python_type="List[int]",
                    title="المجموعات",
                    type=FieldType.LIST,
                    validation=FieldValidation(),
                    relationship=RelationshipInfo(
                        type=RelationshipType.MANY_TO_MANY,
                        related_model="Group",
                        related_field="id",
                        description="Foreign key to User",
                    ),
                ),
                # is_superuser
                ModelField(
                    default_value=False,
                    description="هل المستخدم مميز؟",
                    is_list=False,
                    is_relationship=False,
                    is_required=False,
                    name="is_superuser",
                    python_type="bool",
                    relationship=None,
                    title="المستخدم المميز",
                    type=FieldType.BOOLEAN,
                    validation=FieldValidation(),
                ),
                ModelField(
                    default_value=False,
                    description="البريد الالكتروني",
                    is_list=False,
                    is_relationship=False,
                    is_required=False,
                    name="email",
                    python_type="str",
                    relationship=None,
                    title="البريد الالكتروني",
                    type=FieldType.EMAIL,
                    validation=FieldValidation(),
                ),
                ModelField(
                    default_value=False,
                    description="رقم الهاتف",
                    is_list=False,
                    is_relationship=False,
                    is_required=False,
                    name="phone",
                    python_type="str",
                    relationship=None,
                    title="رقم التلفون",
                    type=FieldType.STRING,
                    validation=FieldValidation(),
                ),
            ],
            layout=[
                # ModelLayoutItem(
                #     name="image",
                #     type=FieldType.IMAGE,
                #     label="الصوره",
                #     required=True,
                #     placeholder="ادخل الصوره",
                #     description="ادخل الصوره",
                # ),
                ModelLayoutItem(
                    name="name",
                    type=FieldType.STRING,
                    label="الاسم",
                    required=True,
                    placeholder="ادخل الاسم",
                    description="ادخل الاسم",
                ),
                ModelLayoutItem(
                    name="username",
                    type=FieldType.STRING,
                    label="اسم المستخدم",
                    required=True,
                    placeholder="ادخل اسم المستخدم",
                    description="ادخل اسم المستخدم",
                ),
                ModelLayoutItem(
                    name="roles",
                    type=FieldType.LIST,
                    label="الأدوار",
                    required=False,
                    placeholder="ادخل الأدوار",
                    description="ادخل الأدوار",
                ),
                ModelLayoutItem(
                    name="groups",
                    type=FieldType.LIST,
                    label="المجموعات",
                    required=False,
                    placeholder="ادخل المجموعات",
                    description="ادخل المجموعات",
                ),
                ModelLayoutItem(
                    name="is_superuser",
                    type=FieldType.BOOLEAN,
                    label="المستخدم المميز",
                    required=False,
                    placeholder="هل المستخدم مميز؟",
                    description="هل المستخدم مميز؟",
                ),
                ModelLayoutItem(
                    name="phone",
                    type=FieldType.STRING,
                    label="رقم الهاتف",
                    required=False,
                    placeholder="رقم الهاتف",
                    description="رقم الهاتف",
                ),
                ModelLayoutItem(
                    name="email",
                    type=FieldType.EMAIL,
                    label="الايميل",
                    required=False,
                    placeholder="البريد الالكتروني",
                    description="البريد الالكتروني",
                ),
            ],
            description=f"Dynamic form configuration for {model_class.__name__}",
            title=f"{model_class.__name__} Form",
            validation_rules={
                "name": {"required": True, "type": "string", "max_length": 50},
                "description": {"required": False, "type": "string", "max_length": 255},
            },
        )
