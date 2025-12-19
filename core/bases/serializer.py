from typing import Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel, ValidationError
from sqlmodel import SQLModel


class SerializerMethodField:
    """
    A read-only field that gets its representation from calling a method on the
    parent serializer class. The method name defaults to 'get_<field_name>'.
    """

    def __init__(self, method_name: Optional[str] = None):
        self.method_name = method_name

    def bind(self, field_name: str, serializer: "BaseSerializer"):
        self.method_name = self.method_name or f"get_{field_name}"
        self.serializer = serializer


class BaseSerializer:
    """
    A DRF-style serializer that wraps Pydantic models/schemas but adds
    dynamic method fields and context handling.
    """

    def __init__(
        self,
        instance: Union[SQLModel, List[SQLModel], Any] = None,
        data: Union[Dict, List[Dict], Any] = None,
        many: bool = False,
        context: Dict = None,
        partial: bool = False,
    ):
        self.instance = instance
        self.initial_data = data
        self.many = many
        self.context = context or {}
        self.partial = partial
        self._data = None
        self._validated_data = None

    def __init__(
        self,
        instance: Union[SQLModel, List[SQLModel], Any] = None,
        data: Union[Dict, List[Dict], Any] = None,
        many: bool = False,
        context: Dict = None,
        partial: bool = False,
    ):
        self.instance = instance
        self.initial_data = data
        self.many = many
        self.context = context or {}
        self.partial = partial
        self._data = None
        self._validated_data = None
        self._errors = []

    @property
    def data(self):
        if self._data is None:
            if self._validated_data is not None and not self.instance:
                # If we validated but didn't save/ have no instance, return validated data
                return self._validated_data

            # If we have an instance (or list of instances), serialize it
            self._data = self.to_representation(self.instance)
        return self._data

    @property
    def validated_data(self):
        if self._validated_data is None:
            raise Exception(
                "You must call .is_valid() before accessing .validated_data"
            )
        return self._validated_data

    async def is_valid(self, raise_exception: bool = False) -> bool:
        """
        Validates the initial_data against the Pydantic model defined in Meta.model.
        """
        if not hasattr(self, "Meta") or not hasattr(self.Meta, "model"):
            raise Exception("Serializer must have Meta.model defined for validation")

        model_class = self.Meta.model
        try:
            if self.many:
                if not isinstance(self.initial_data, list):
                    self._errors = [
                        {
                            "detail": "Expected a list of items but got type "
                            + type(self.initial_data).__name__
                        }
                    ]
                    if raise_exception:
                        raise Exception(self._errors)
                    return False

                self._validated_data = []
                # TODO: Implement bulk validation loop
                for item in self.initial_data:
                    # Simplistic validation for now
                    if hasattr(model_class, "model_validate"):
                        self._validated_data.append(
                            model_class.model_validate(item).model_dump()
                        )
                    else:
                        self._validated_data.append(model_class(**item).dict())
            else:
                # Single item validation
                if self.partial and self.instance:
                    # For partial update, we might need to merge with existing instance data if we were doing strict checking
                    # But Pydantic usually validates the *subset* if configured, or we assume partial=True means "only validate keys present"
                    # SQLModel/Pydantic V2 'model_validate' doesn't support 'partial' directly in the same way DRF does (ignoring missing required fields).
                    # A common pattern is creating a separate PatchSchema or using 'exclude_unset'.
                    pass

                if hasattr(model_class, "model_validate"):
                    # Use Pydantic V2 if available
                    validated_obj = model_class.model_validate(self.initial_data)
                    self._validated_data = validated_obj.model_dump(exclude_unset=True)
                else:
                    # Pydantic V1 fallback
                    validated_obj = model_class(**self.initial_data)
                    self._validated_data = validated_obj.dict(exclude_unset=True)

            return True
        except ValidationError as e:
            self._errors = []
            for error in e.errors():
                self._errors.append(
                    {
                        "field": ".".join(str(x) for x in error["loc"]),
                        "msg": error["msg"],
                        "type": error["type"],
                    }
                )
            if raise_exception:
                raise Exception(self._errors)
            return False
        except Exception as e:
            self._errors = [{"detail": str(e)}]
            if raise_exception:
                raise e
            return False

    async def save(self, **kwargs):
        """
        Persists the validated data.
        If instance exists, calls update(); otherwise calls create().
        Passes 'kwargs' (like 'service') down.
        """
        if self._validated_data is None:
            raise Exception("You must call .is_valid() before .save()")

        # Allow passing service/repo via save kwargs or context
        service = kwargs.get("service")

        if self.instance is not None:
            self.instance = await self.update(
                self.instance, self.validated_data, **kwargs
            )
        else:
            self.instance = await self.create(self.validated_data, **kwargs)

        return self.instance

    async def create(self, validated_data: Dict, **kwargs):
        """
        Override this method to support custom creation logic.
        """
        service = kwargs.get("service")
        if service:
            # 1. Identify and pop fields that have custom save hooks
            hooks = {}
            for key in list(validated_data.keys()):
                hook_method = getattr(self, f"save_{key}", None)
                if hook_method and callable(hook_method):
                    hooks[key] = {
                        "method": hook_method,
                        "value": validated_data.pop(key),
                    }

            # 2. Persist the main instance
            result = await service.repository.create(validated_data)

            # 3. Execute hooks
            for key, hook_info in hooks.items():
                await hook_info["method"](result, hook_info["value"], **kwargs)

            return result

        raise NotImplementedError(
            "Serializer.create() must be implemented or 'service' passed to save()"
        )

    async def update(self, instance: Any, validated_data: Dict, **kwargs):
        """
        Override this method to support custom update logic.
        """
        service = kwargs.get("service")
        if service:
            # 1. Identify and pop fields that have custom save hooks
            hooks = {}
            # We look at keys in validated_data to see if we need to update them via hook
            for key in list(validated_data.keys()):
                hook_method = getattr(self, f"save_{key}", None)
                if hook_method and callable(hook_method):
                    hooks[key] = {
                        "method": hook_method,
                        "value": validated_data.pop(key),
                    }

            # 2. Update the main instance
            result = await service.repository.update(instance.id, validated_data)

            # 3. Execute hooks
            for key, hook_info in hooks.items():
                await hook_info["method"](result, hook_info["value"], **kwargs)

            return result

        raise NotImplementedError(
            "Serializer.update() must be implemented or 'service' passed to save()"
        )

    def get_fields(self) -> Dict[str, Any]:
        """
        Returns a dictionary of fields to be serialized.
        Combines Pydantic fields (from Meta.model) and explicitly defined fields.
        """
        fields = {}

        # 1. Get fields from Meta model if it exists
        if hasattr(self, "Meta") and hasattr(self.Meta, "model"):
            model_class = self.Meta.model
            # simplistic approach: use all model fields
            # specific inclusions/exclusions can be added here
            for name, field_info in model_class.model_fields.items():
                fields[name] = field_info

        # 2. Add/Override with class-defined attributes (like SerializerMethodField)
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, SerializerMethodField):
                attr.bind(attr_name, self)
                fields[attr_name] = attr

        return fields

    def to_representation(self, instance: Any) -> Any:
        """
        Converts the instance into a dictionary/list.
        """
        if self.many:
            if isinstance(instance, list):
                return [self._serialize_single(item) for item in instance]
            return []
        return self._serialize_single(instance)

    def _serialize_single(self, instance: Any) -> Dict[str, Any]:
        ret = {}

        # If the instance is a SQLModel/Pydantic model, start with its dump
        if isinstance(instance, BaseModel):
            ret = instance.model_dump()
        else:
            # Fallback for dicts or objects
            # This part depends on what 'instance' usually is in your system
            if hasattr(instance, "__dict__"):
                ret = instance.__dict__.copy()
            elif isinstance(instance, dict):
                ret = instance.copy()

        # Process methods and overrides
        for attr_name in dir(self):
            attr = getattr(self, attr_name)

            # Handle SerializerMethodField
            if isinstance(attr, SerializerMethodField):
                method = getattr(self, attr.method_name, None)
                if method:
                    ret[attr_name] = method(instance)

        # Optional: Filter based on Meta.fields if specific subset requested
        # if hasattr(self, "Meta") and hasattr(self.Meta, "fields"):
        #    allowed = set(self.Meta.fields)
        #    ret = {k: v for k, v in ret.items() if k in allowed}

        return ret
