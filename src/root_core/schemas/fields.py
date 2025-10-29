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


class DynamicFormConfig(BaseModel):
    model_name: str
    fields: List[ModelField]
    layout: List[ModelLayoutItem | Dict[str, Any]]  # For frontend form layout
    validation_rules: Dict[str, Any]
    title: Optional[str] = None
    description: Optional[str] = None
