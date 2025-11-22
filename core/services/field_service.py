# src/core/services/field_service.py
from typing import Any, Dict, List, Optional, Type, get_type_hints
from sqlmodel import SQLModel
from sqlmodel.main import FieldInfo

from core.schemas.fields import (
    ModelField,
    FieldType,
    FieldValidation,
    RelationshipType,
    RelationshipInfo,
    ModelDefinition,
    DynamicFormConfig,
)
import re
import sys


def convert_to_camel_case(word):
    return "".join(x.capitalize() or "_" for x in word.split("_"))


class FieldService:
    """Service to extract field information from SQLModel and Pydantic models."""

    # Type mappings
    TYPE_MAPPINGS = {
        str: FieldType.STRING,
        int: FieldType.INTEGER,
        float: FieldType.FLOAT,
        bool: FieldType.BOOLEAN,
        dict: FieldType.JSON,
        list: FieldType.JSON,
    }

    @classmethod
    def get_model_definition(cls, model_class: Type[SQLModel]) -> ModelDefinition:
        """Get complete model definition for dynamic frontend."""

        fields = []
        relationships = []
        try:
            # Resolve forward references by providing the module globals where the model is defined.
            module = sys.modules.get(model_class.__module__)
            module_globals = module.__dict__ if module is not None else {}
            # use the class namespace as localns to help resolution of inner names
            type_hints = get_type_hints(
                model_class, globalns=module_globals, localns=dict(vars(model_class))
            )
        except Exception:
            # Fallback: use raw annotations if resolution fails (e.g., TYPE_CHECKING imports missing)
            type_hints = getattr(model_class, "__annotations__", {}) or {}

        for field_name, field_info in model_class.__fields__.items():
            # Skip internal fields
            if field_name.startswith("_") or field_name in ["metadata", "registry"]:
                continue

            field_type = type_hints.get(field_name, str)
            field_def = cls._parse_field(field_name, field_type, field_info)  # type: ignore
            fields.append(field_def)

            if field_def.is_relationship and field_def.relationship:
                relationships.append(field_def.relationship)

        return ModelDefinition(
            model_name=model_class.__name__,
            table_name=getattr(
                model_class, "__tablename__", f"{model_class.__name__.lower()}s"
            ),
            fields=fields,
            relationships=relationships,
        )

    @classmethod
    def _parse_field(
        cls, field_name: str, field_type: Any, field_info: FieldInfo
    ) -> ModelField:
        """Parse a single field definition."""
        # Get base type
        base_type = cls._get_base_type(field_type)
        python_type = cls._get_python_type_name(field_type)

        # Check if it's a relationship
        relationship_info = cls._detect_relationship(field_name, field_type)

        # Check if it's a list
        is_list = cls._is_list_type(field_type)

        # check if is required
        is_required = not field_info.nullable

        # Get default value
        default_value = field_info.default if field_info.default is not None else None

        # Create validation rules
        validation = cls._create_validation_rules(field_info, field_type)

        field = ModelField(
            name=field_name,
            type=base_type,
            python_type=python_type,
            is_required=is_required,
            is_relationship=relationship_info is not None,
            is_list=is_list,
            default_value=default_value,
            validation=validation,
            relationship=relationship_info,
            # show others attributes of FieldInfo if needed
            title=(
                field_info.__getattribute__("title")
                if hasattr(field_info, "title")
                else None
            ),
            description=(
                field_info.__getattribute__("description")
                if hasattr(field_info, "description")
                else None
            ),
        )

        if base_type == FieldType.ENUM:
            field.is_relationship = False
            field.relationship = None
            field.options = [
                {"label": status.value, "value": status.name} for status in field_type
            ]

        return field

    @classmethod
    def _get_base_type(cls, field_type: Any) -> FieldType:
        """Get the base field type."""
        origin = getattr(field_type, "__origin__", field_type)
        args = getattr(field_type, "__args__", [])

        # Handle Optional[Type]
        if origin is Optional or (
            hasattr(origin, "__name__") and origin.__name__ == "Optional"
        ):
            if args:
                actual_type = args[0]
                return cls._get_base_type(actual_type)

        # Handle List[Type]
        if origin is list or (
            hasattr(origin, "__name__") and origin.__name__ == "List"
        ):
            if args:
                return cls._get_base_type(args[0])
            return FieldType.JSON

        # Handle basic types
        if origin in cls.TYPE_MAPPINGS:
            return cls.TYPE_MAPPINGS[origin]

        if args and args[0] in cls.TYPE_MAPPINGS:
            return cls.TYPE_MAPPINGS[args[0]]

        if "EnumType" == type(field_type).__name__:
            return FieldType.ENUM

        # Handle string-based types
        if hasattr(field_type, "__name__"):
            type_name = field_type.__name__.lower()

            if "uuid" in type_name:
                return FieldType.UUID
            elif "datetime" in type_name:
                return FieldType.DATETIME
            elif "email" in type_name:
                return FieldType.EMAIL
            elif "url" in type_name:
                return FieldType.URL
            elif "date" in type_name:
                return FieldType.DATE
            elif "time" in type_name:
                return FieldType.TIME
            elif "phone" in type_name:
                return FieldType.TEL
            elif "text" in type_name:
                return FieldType.TEXT
            elif "json" in type_name:
                return FieldType.JSON
            elif "decimal" in type_name:
                return FieldType.FLOAT

        # Default to string
        return FieldType.STRING

    @classmethod
    def _get_python_type_name(cls, field_type: Any) -> str:
        """Get Python type as string."""
        args = getattr(field_type, "__args__", None)
        if args:
            return cls._get_python_type_name(args[0])
        return getattr(field_type, "__name__", str(field_type))

    @classmethod
    def _is_optional_type(cls, field_type: Any) -> bool:
        """Check if field is optional."""
        origin = getattr(field_type, "__origin__", None)
        return origin is Optional

    @classmethod
    def _is_list_type(cls, field_type: Any) -> bool:
        """Check if field is a list."""
        origin = getattr(field_type, "__origin__", None)
        return origin is list

    @classmethod
    def _detect_relationship(
        cls, field_name: str, field_type: Any
    ) -> Optional[RelationshipInfo]:
        """Detect relationships."""
        type_name = str(field_type)

        # Foreign key detection (ends with _id)
        if field_name.endswith("_id"):
            related_model = convert_to_camel_case(field_name[:-3])
            return RelationshipInfo(
                type=RelationshipType.FOREIGN_KEY,
                related_model=related_model,
                related_field="id",
                description=f"Foreign key to {related_model}",
            )

        # Model reference detection (capitalized type names)
        if hasattr(field_type, "__name__") and field_type.__name__[0].isupper():
            if field_type.__name__.lower() not in [
                "str",
                "int",
                "float",
                "bool",
                "dict",
                "list",
                "optional",
                "list",
                "decimal",
                "enum",
            ]:
                return RelationshipInfo(
                    type=RelationshipType.MANY_TO_ONE,
                    related_model=field_type.__name__,
                    description=f"Relationship to {field_type.__name__}",
                )

        # List of models (OneToMany)
        origin = getattr(field_type, "__origin__", None)
        args = getattr(field_type, "__args__", [])
        if origin is list and args:
            arg_type = args[0]
            if hasattr(arg_type, "__name__") and arg_type.__name__[0].isupper():
                return RelationshipInfo(
                    type=RelationshipType.ONE_TO_MANY,
                    related_model=arg_type.__name__,
                    description=f"One-to-many relationship with {arg_type.__name__}",
                )

        return None

    @classmethod
    def _create_validation_rules(
        cls, field_info: FieldInfo, field_type: Any
    ) -> FieldValidation:
        """Create validation rules for frontend."""
        validation = FieldValidation()

        # Get field constraints from SQLModel Field
        field_extra = getattr(field_info, "field_info", None)
        if field_extra:
            # Required field
            validation.required = getattr(field_extra, "default", None) is None

            # String length constraints
            if hasattr(field_extra, "max_length"):
                validation.max_length = field_extra.max_length

            # Numeric constraints
            if hasattr(field_extra, "ge"):
                validation.min_value = field_extra.ge
            if hasattr(field_extra, "le"):
                validation.max_value = field_extra.le

        return validation

    @classmethod
    def _get_field_description(cls, field_name: str, field_type: Any) -> str:
        """Generate field description."""
        type_name = cls._get_python_type_name(field_type)

        descriptions = {
            "id": "Unique identifier",
            "created_at": "Creation timestamp",
            "updated_at": "Last update timestamp",
            "is_deleted": "Soft delete flag",
            "name": "Item name",
            "title": "Item title",
            "description": "Item description",
            "email": "Email address",
            "password": "User password",
        }

        return descriptions.get(field_name, f"{field_name.replace('_', ' ').title()}")

    @classmethod
    def get_dynamic_form_config(cls, model_class: Type[SQLModel]) -> DynamicFormConfig:
        """Get form configuration for dynamic frontend forms."""
        model_def = cls.get_model_definition(model_class)

        # Generate form layout (you can customize this)
        layout = cls._generate_form_layout(model_def.fields)

        # Generate validation rules for frontend
        validation_rules = cls._generate_validation_rules(model_def.fields)

        return DynamicFormConfig(
            model_name=model_def.model_name,
            fields=model_def.fields,
            layout=layout,  # type:ignore
            validation_rules=validation_rules,
        )

    @classmethod
    def _generate_form_layout(cls, fields: List[ModelField]) -> List[Dict[str, Any]]:
        """Generate form layout for frontend."""
        layout = []

        for field in fields:
            # Skip internal fields in forms
            if field.name in ["id", "created_at", "updated_at", "is_deleted"]:
                continue

            field_config = {
                "name": field.name,
                "type": field.type.value,
                "label": field.title or field.name.replace("_", " ").title(),
                "required": field.is_required,
                "placeholder": field.description
                or f"Enter {field.name.replace('_', ' ')}",
                "options": field.options,
            }

            # Add validation rules
            if field.validation:
                if field.validation.min_length:
                    field_config["minLength"] = field.validation.min_length
                if field.validation.max_length:
                    field_config["maxLength"] = field.validation.max_length
                if field.validation.min_value is not None:
                    field_config["min"] = field.validation.min_value
                if field.validation.max_value is not None:
                    field_config["max"] = field.validation.max_value

            # Handle relationships
            if field.is_relationship and field.relationship:
                if field.relationship.type == RelationshipType.FOREIGN_KEY:
                    field_config["type"] = "select"
                    # field_config["options"] = (
                    #     f"/{field.relationship.related_model.lower()}s"
                    # )
                elif field.relationship.type == RelationshipType.ONE_TO_MANY:
                    field_config["type"] = "multiselect"
                    # field_config["options"] = (
                    #     f"/{field.relationship.related_model.lower()}s"
                    # )

            layout.append(field_config)

        return layout

    @classmethod
    def _generate_validation_rules(cls, fields: List[ModelField]) -> Dict[str, Any]:
        """Generate validation rules for frontend."""
        rules = {}

        for field in fields:
            if field.name in ["id", "created_at", "updated_at", "is_deleted"]:
                continue

            field_rules = {}

            if field.is_required:
                field_rules["required"] = True

            if field.validation:
                if field.validation.min_length:
                    field_rules["minLength"] = field.validation.min_length
                if field.validation.max_length:
                    field_rules["maxLength"] = field.validation.max_length
                if field.validation.min_value is not None:
                    field_rules["min"] = field.validation.min_value
                if field.validation.max_value is not None:
                    field_rules["max"] = field.validation.max_value
                if field.validation.pattern:
                    field_rules["pattern"] = field.validation.pattern

            if field_rules:
                rules[field.name] = field_rules

        return rules
