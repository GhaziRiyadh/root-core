import re
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class FieldType(Enum):
    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"
    DATETIME = "datetime"
    TEXT = "text"
    JSON = "json"


class FieldParser:
    """Parse model field definitions and detect relationships."""

    TYPE_MAPPINGS = {
        'str': FieldType.STRING,
        'string': FieldType.STRING,
        'int': FieldType.INTEGER,
        'integer': FieldType.INTEGER,
        'float': FieldType.FLOAT,
        'bool': FieldType.BOOLEAN,
        'boolean': FieldType.BOOLEAN,
        'datetime': FieldType.DATETIME,
        'text': FieldType.TEXT,
        'json': FieldType.JSON,
        'dict': FieldType.JSON,
    }

    @classmethod
    def parse_field(cls, field_definition: str) -> Dict[str, Any]:
        """
        Parse a field definition string and return structured information.

        Accepts "name:type", "name:type=default", and supports wrappers List[...] and Optional[...].
        """
        field_definition = field_definition.strip()
        if ':' not in field_definition:
            return cls._create_field_info(field_definition, 'str')

        name_part, type_part = field_definition.split(':', 1)
        field_name = name_part.strip()

        if '=' in type_part:
            type_def, default_val = type_part.split('=', 1)
            field_type = type_def.strip()
            default_value = default_val.strip()
        else:
            field_type = type_part.strip()
            default_value = None

        return cls._create_field_info(field_name, field_type, default_value)

    @classmethod
    def _create_field_info(cls, field_name: str, field_type: str, default_value: Optional[str] = None) -> Dict[str, Any]:
        """Create structured field information dictionary."""
        original_type = field_type.strip()

        # Unwrap wrappers and preserve inner's original casing
        inner_type, wrappers = cls._unwrap_type(original_type)

        base_type = cls._get_base_type(inner_type)
        is_optional = 'Optional' in wrappers or default_value is not None and default_value.lower() == 'none'
        is_list = 'List' in wrappers

        python_type = cls._get_python_type(inner_type, wrappers)
        sql_type = cls._get_sql_type(inner_type, wrappers)

        relationship_info = cls._detect_relationship(field_name, inner_type, wrappers)

        return {
            'name': field_name,
            'original_type': original_type,
            'base_type': base_type.value if base_type else inner_type,
            'python_type': python_type,
            'sql_type': sql_type,
            'is_optional': is_optional,
            'is_list': is_list,
            'is_relationship': relationship_info is not None,
            'relationship': relationship_info,
            'default_value': default_value,
            'field_definition': cls._generate_field_definition(field_name, python_type, default_value),
            'schema_definition': cls._generate_schema_definition(field_name, python_type, default_value),
        }

    @classmethod
    def _unwrap_type(cls, field_type: str) -> Tuple[str, List[str]]:
        """
        Remove outer wrappers like List[...] and Optional[...] iteratively.

        Returns the inner type (preserving original casing) and a list of wrappers in outer-to-inner order.
        """
        t = field_type.strip()
        wrappers: List[str] = []
        pattern = re.compile(r'^\s*(?P<w>List|Optional)\s*\[\s*(?P<inner>.+)\s*\]\s*$', re.IGNORECASE)
        while True:
            m = pattern.match(t)
            if not m:
                break
            w = m.group('w').capitalize()
            wrappers.append(w)
            t = m.group('inner').strip()
        return t, wrappers

    @classmethod
    def _get_base_type(cls, inner_type: str) -> Optional[FieldType]:
        """Get the base field type enum for a given inner type (case-insensitive)."""
        return cls.TYPE_MAPPINGS.get(inner_type.strip().lower())

    @classmethod
    def _detect_relationship(cls, field_name: str, inner_type: str, wrappers: List[str]) -> Optional[Dict[str, Any]]:
        """Detect relationship based on field name and inner type + wrappers."""

        # foreign key by naming convention: foo_id
        if field_name.lower().endswith('_id'):
            # only treat as FK if the inner type maps to integer
            base = cls._get_base_type(inner_type)
            if base == FieldType.INTEGER:
                related_raw = field_name[:-3]  # remove _id
                related_model = ''.join(part.capitalize() for part in related_raw.split('_') if part)
                return {
                    'type': 'ForeignKey',
                    'related_model': related_model,
                    'relationship_type': 'ManyToOne',
                    'description': f'Foreign key to {related_model}'
                }

        # If inner_type looks like a model name (starts with uppercase letter), treat as relation
        if inner_type and inner_type[0].isupper():
            # Determine relationship cardinality from wrappers
            if 'List' in wrappers:
                rel_type = 'OneToMany'
            else:
                rel_type = 'ManyToOne'
            related_model = inner_type
            return {
                'type': 'ModelReference' if 'List' not in wrappers else 'OneToMany',
                'related_model': related_model,
                'relationship_type': rel_type,
                'description': f'{rel_type} relationship with {related_model}'
            }

        return None

    @classmethod
    def _get_python_type(cls, inner_type: str, wrappers: List[str]) -> str:
        """Return a Python type hint string (as text) for the provided inner type and wrappers."""
        base = cls._get_base_type(inner_type)
        if base == FieldType.STRING or base == FieldType.TEXT:
            core = 'str'
        elif base == FieldType.INTEGER:
            core = 'int'
        elif base == FieldType.FLOAT:
            core = 'float'
        elif base == FieldType.BOOLEAN:
            core = 'bool'
        elif base == FieldType.DATETIME:
            core = 'datetime'
        elif base == FieldType.JSON:
            core = 'Dict[str, Any]'
        else:
            # assume a model reference; preserve original inner_type casing
            core = inner_type

        # Apply wrappers from inner outwards (reverse the collected list)
        for w in reversed(wrappers):
            if w == 'List':
                core = f'List[{core}]'
            elif w == 'Optional':
                core = f'Optional[{core}]'
        return core

    @classmethod
    def _get_sql_type(cls, inner_type: str, wrappers: List[str]) -> str:
        """Return a SQL/SQLModel type string (as text) for the provided inner type and wrappers."""
        base = cls._get_base_type(inner_type)
        if base == FieldType.STRING or base == FieldType.TEXT:
            core = 'str'
        elif base == FieldType.INTEGER:
            core = 'int'
        elif base == FieldType.FLOAT:
            core = 'float'
        elif base == FieldType.BOOLEAN:
            core = 'bool'
        elif base == FieldType.DATETIME:
            core = 'datetime'
        elif base == FieldType.JSON:
            core = 'JSON'
        else:
            core = inner_type  # model reference

        # Represent lists as List[...] for schema but leave Optional transparent
        for w in reversed(wrappers):
            if w == 'List':
                core = f'List[{core}]'
        return core

    @classmethod
    def _generate_field_definition(cls, field_name: str, python_type: str, default_value: Optional[str]) -> str:
        """Generate SQLModel/typing-style field definition string."""
        default_str = f" = {default_value}" if default_value is not None else ""
        return f"{field_name}: {python_type}{default_str}"

    @classmethod
    def _generate_schema_definition(cls, field_name: str, python_type: str, default_value: Optional[str]) -> str:
        """Generate Pydantic schema field definition string (same format used)."""
        return cls._generate_field_definition(field_name, python_type, default_value)
