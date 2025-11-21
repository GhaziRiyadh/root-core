# src/core/schemas/fields.py
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from enum import Enum


class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    TEXT = "text"
    JSON = "json"
    EMAIL = "email"
    URL = "url"
    UUID = "uuid"
    LIST = "list"
    IMAGE = "image"
    GALLERY = "gallery"
    FILE = "file"
    FILE_MULTI = "file_multiple"
    ENUM = "enum"
    DATE = "date"
    TIME = "time"
    TEL = "tel"


class RelationshipType(str, Enum):
    FOREIGN_KEY = "foreign_key"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


class FieldValidation(BaseModel):
    required: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[str]] = None


class RelationshipInfo(BaseModel):
    type: RelationshipType
    related_model: str
    related_field: Optional[str] = None
    description: str


class ModelField(BaseModel):
    name: str
    type: FieldType
    python_type: str
    is_required: bool = False
    is_relationship: bool = False
    is_list: bool = False
    default_value: Optional[Any] = None
    validation: Optional[FieldValidation] = None
    relationship: Optional[RelationshipInfo] = None
    description: Optional[str] = None
    title: Optional[str] = None
    options: Optional[List[Any]] = None  # For ENUM types


class ModelDefinition(BaseModel):
    model_name: str
    table_name: str
    fields: List[ModelField]
    relationships: List[RelationshipInfo]


class ModelSchemaResponse(BaseModel):
    create_schema: Dict[str, Any]
    update_schema: Dict[str, Any]
    response_schema: Dict[str, Any]


class ModelLayoutItem(BaseModel):
    name: str
    type: FieldType
    label: Optional[str] = None
    required: bool = False
    placeholder: Optional[str] = None
    description: Optional[str] = None
    default_value: Optional[Any] = None
    options: Optional[List[Any]] = None  # For ENUM types


class DynamicFormConfig(BaseModel):
    model_name: str
    fields: List[ModelField]
    layout: List[ModelLayoutItem | Dict[str, Any]]  # For frontend form layout
    validation_rules: Dict[str, Any]
    title: Optional[str] = None
    description: Optional[str] = None
    ignored_fields: Optional[List[str]] = None

    def addField(
        self,
        name: str,
        type: FieldType,
        python_type: str,
        is_required: bool = False,
        is_relationship: bool = False,
        is_list: bool = False,
        default_value: Any | None = None,
        validation: FieldValidation | None = None,
        relationship: RelationshipInfo | None = None,
        description: str | None = None,
        title: str | None = None,
        options: List[Any] | None = None,
        placeholder: str | None = None,
    ):
        field = ModelField(
            name=name,
            type=type,
            python_type=python_type,
            is_required=is_required,
            is_relationship=is_relationship,
            is_list=is_list,
            default_value=default_value,
            validation=validation,
            relationship=relationship,
            description=description,
            title=title if title else name,
            options=options,
        )

        layout = ModelLayoutItem(
            name=name,
            type=type,
            label=title,
            required=is_required,
            placeholder=description if not placeholder else placeholder,
            description=description,
            default_value=default_value,
            options=options,
        )

        self.fields.append(field)
        self.layout.append(layout)

    def updateField(
        self,
        name: str,
        type: FieldType | None = None,
        python_type: str | None = None,
        is_required: bool | None = None,
        is_relationship: bool | None = None,
        is_list: bool | None = None,
        default_value: Any | None = None,
        validation: FieldValidation | None = None,
        relationship: RelationshipInfo | None = None,
        description: str | None = None,
        title: str | None = None,
        options: List[Any] | None = None,
        placeholder: str | None = None,
    ):
        # helpers
        new_or_old = lambda new, old: new if new is not None else old

        def merge_pydantic(new_obj, old_obj, model_cls):
            # Merge two pydantic models by preferring non-None values from new_obj
            if new_obj is None:
                return old_obj
            old_data = old_obj.dict() if old_obj is not None else {}
            new_data = new_obj.dict()
            merged = {
                **old_data,
                **{k: v for k, v in new_data.items() if v is not None},
            }
            return model_cls(**merged)

        # find existing field
        idx = next((i for i, f in enumerate(self.fields) if f.name == name), None)
        if idx is None:
            raise ValueError(f"Field '{name}' does not exist and cannot be updated.")

        old_field = self.fields[idx]

        # merge nested objects
        merged_validation = merge_pydantic(
            validation, old_field.validation, FieldValidation
        )
        merged_relationship = merge_pydantic(
            relationship, old_field.relationship, RelationshipInfo
        )

        # build updated ModelField
        updated_field = ModelField(
            name=name,
            type=new_or_old(type, old_field.type),
            python_type=new_or_old(python_type, old_field.python_type),
            is_required=new_or_old(is_required, old_field.is_required),
            is_relationship=new_or_old(is_relationship, old_field.is_relationship),
            is_list=new_or_old(is_list, old_field.is_list),
            default_value=new_or_old(default_value, old_field.default_value),
            validation=merged_validation,
            relationship=merged_relationship,
            description=new_or_old(description, old_field.description),
            title=new_or_old(title, old_field.title),
            options=new_or_old(options, old_field.options),
        )

        # replace field in list
        self.fields[idx] = updated_field

        # update or create corresponding layout item (layout entries can be ModelLayoutItem or dict)
        def _matches_layout_item(item, field_name):
            if isinstance(item, ModelLayoutItem):
                return item.name == field_name
            if isinstance(item, dict):
                return item.get("name") == field_name
            return False

        layout_idx = next(
            (i for i, it in enumerate(self.layout) if _matches_layout_item(it, name)),
            None,
        )

        layout_payload = {
            "name": name,
            "type": new_or_old(type, old_field.type),
            "label": new_or_old(title, old_field.title) or name,
            "required": new_or_old(is_required, old_field.is_required),
            "placeholder": (
                placeholder
                if placeholder is not None
                else new_or_old(description, old_field.description)
            ),
            "description": new_or_old(description, old_field.description),
            "default_value": new_or_old(default_value, old_field.default_value),
            "options": new_or_old(options, old_field.options),
        }

        if layout_idx is None:
            # append new layout item
            self.layout.append(ModelLayoutItem(**layout_payload))
        else:
            existing = self.layout[layout_idx]
            if isinstance(existing, ModelLayoutItem):
                # update fields preserving any extra attributes
                for k, v in layout_payload.items():
                    setattr(existing, k, v)
                self.layout[layout_idx] = existing
            else:
                # it's a dict, merge keys
                merged_dict = {
                    **existing,
                    **{k: v for k, v in layout_payload.items() if v is not None},
                }
                self.layout[layout_idx] = merged_dict

        return updated_field

    def ignore_field(self, name: str, remove_from_layout: bool = True) -> None:
        """
        Mark a field as ignored. Optionally remove its layout entry.
        The removed field and layout item are stored so they can be restored later.
        """
        if not hasattr(self, "ignored_fields") or self.ignored_fields is None:
            self.ignored_fields = []

        if not hasattr(self, "_removed_fields"):
            self._removed_fields: Dict[str, ModelField] = {}
        if not hasattr(self, "_removed_layout_items"):
            self._removed_layout_items: Dict[str, Any] = {}

        if name in self.ignored_fields:
            return

        # remove and store field
        field_idx = next((i for i, f in enumerate(self.fields) if f.name == name), None)
        if field_idx is not None:
            self._removed_fields[name] = self.fields.pop(field_idx)

        # remove and store layout item if requested
        if remove_from_layout:

            def _matches_layout_item(item, field_name):
                if isinstance(item, ModelLayoutItem):
                    return item.name == field_name
                if isinstance(item, dict):
                    return item.get("name") == field_name
                return False

            layout_idx = next(
                (
                    i
                    for i, it in enumerate(self.layout)
                    if _matches_layout_item(it, name)
                ),
                None,
            )
            if layout_idx is not None:
                self._removed_layout_items[name] = self.layout.pop(layout_idx)

        self.ignored_fields.append(name)

    def ignore_fields(self, names: List[str], remove_from_layout: bool = True) -> None:
        for n in names:
            self.ignore_field(n, remove_from_layout=remove_from_layout)

    def unignore_field(self, name: str, restore_layout: bool = True) -> None:
        """
        Un-ignore a previously ignored field. Restores the field and optionally its layout item
        if they were stored when ignored.
        """
        if not hasattr(self, "ignored_fields") or name not in getattr(
            self, "ignored_fields", []
        ):
            return

        # restore field if we have it stored
        if hasattr(self, "_removed_fields") and name in self._removed_fields:
            restored_field = self._removed_fields.pop(name)
            # avoid duplicating if a field with same name exists
            if not any(f.name == name for f in self.fields):
                self.fields.append(restored_field)

        # restore layout if requested and stored
        if (
            restore_layout
            and hasattr(self, "_removed_layout_items")
            and name in self._removed_layout_items
        ):
            restored_layout = self._removed_layout_items.pop(name)
            if not any(
                (isinstance(it, ModelLayoutItem) and it.name == name)
                or (isinstance(it, dict) and it.get("name") == name)
                for it in self.layout
            ):
                self.layout.append(restored_layout)

        # remove from ignored list
        self.ignored_fields = [n for n in self.ignored_fields if n != name]

    def unignore_fields(self, names: List[str], restore_layout: bool = True) -> None:
        for n in names:
            self.unignore_field(n, restore_layout=restore_layout)

    def is_ignored(self, name: str) -> bool:
        return name in getattr(self, "ignored_fields", [])

    def get_active_fields(self) -> List[ModelField]:
        """
        Return fields that are not ignored.
        """
        ignored = set(getattr(self, "ignored_fields", []))
        return [f for f in self.fields if f.name not in ignored]
