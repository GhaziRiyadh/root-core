from typing import Any, Callable, Dict, List, Optional, Type
from fastapi import Query, Request, status
from pydantic import BaseModel, ValidationError

from src.core.bases.base_router import BaseRouter

from ..router import add_route
from .base_service import BaseService
from ..config import PermissionAction
from ..response.handlers import (
    success_response,
    paginated_response,
    error_response,
)
from .. import exceptions
from ..schemas.fields import DynamicFormConfig, ModelDefinition


# Schema type definitions for dynamic model creation
class CreateSchema(BaseModel):
    pass


class UpdateSchema(BaseModel):
    pass


class QueryParams(BaseModel):
    page: int = Query(1, ge=1, description="Page number")
    per_page: int = Query(10, ge=1, le=100, description="Items per page")
    include_deleted: bool = Query(False, description="Include soft deleted items")


class CRUDApi(BaseRouter):
    """Generic CRUD API router class.

    Provides a standard REST router for a resource backed by a `BaseService` implementation.
    Routes are registered via the `@add_route` decorator applied to handler methods.

    Constructor parameters:
        service: BaseService
            Service instance responsible for business logic and data access.
        resource_name: str
            Resource identifier used to build the route prefix when `prefix` is not provided.
        tags: Optional[List[str]]
            OpenAPI tags applied to the router's endpoints.
        prefix: Optional[str]
            Custom route prefix. Defaults to `"/{resource_name}"`.
        create_schema: Optional[Type[BaseModel]]
            Pydantic model used to validate create requests.
        update_schema: Optional[Type[BaseModel]]
            Pydantic model used to validate update requests.
        response_schema: Optional[Type[BaseModel]]
            Pydantic model used to serialize responses when applicable.
        dependencies: Optional[List[Callable]]
            FastAPI dependencies applied to the router.
        is_app: bool
            When True, indicates this router is registered under an application context.
        app_name: Optional[str]
            Optional application name used for app-scoped operations (e.g., enum lookups).

    Key behavior:
        - Registers common CRUD endpoints (list, retrieve, create, update, delete, restore, force delete),
          bulk operations, counting, existence checks, logs, and model/form metadata endpoints.
        - Validates input using provided Pydantic schemas (supports both Pydantic v1/constructor and v2 `model_validate`).
        - Normalizes responses using `success_response`, `paginated_response` and `error_response`.
        - Maps service-layer exceptions (`NotFoundException`, `ValidationException`, `ConflictException`,
          `ServiceException`) to consistent HTTP error responses.
        - Some metadata endpoints are exposed with `need_auth=False` to remain publicly accessible.

    Example usage:
        router = CRUDApi(service=my_service, resource_name="users", create_schema=UserCreate, update_schema=UserUpdate)

    """

    def __init__(
            self,
            service: BaseService,
            resource_name: str,
            tags: Optional[List[str]] = None,
            prefix: Optional[str] = None,
            create_schema: Optional[Type[BaseModel]] = None,
            update_schema: Optional[Type[BaseModel]] = None,
            response_schema: Optional[Type[BaseModel]] = None,
            dependencies: Optional[List[Callable]] = None,
            is_app: bool = False,
            app_name: Optional[str] = None,
    ):
        self.service = service
        super().__init__(
            resource_name,
            tags,
            prefix if prefix else f"/{resource_name}",
            create_schema,
            update_schema,
            response_schema,
            dependencies,
            is_app,
            app_name,
        )

    # -----------------------
    # Base handler methods (moved out of register functions)
    # Each route is decorated with @add_route so registration happens automatically.
    # Note: dynamic schema validation is done inside handlers using the instance schemas
    # because Pydantic models are provided at construction time.
    # -----------------------

    @add_route(
        "/{item_id}/",
        "GET",
        PermissionAction.READ,
        response_model=None,
        summary="Get item by ID",
        responses={
            200: {"description": "Item retrieved successfully"},
            404: {"description": "Item not found"},
            500: {"description": "Internal server error"},
        },
    )
    async def get_by_id(
            self,
            item_id: int,
            include_deleted: bool = Query(False, description="Include soft deleted items"),
    ):
        try:
            result = await self.service.get_by_id(
                item_id=item_id, include_deleted=include_deleted
            )
            return success_response(data=result["data"], message=result["message"])
        except exceptions.NotFoundException as e:
            return error_response(
                error_code="NOT_FOUND",
                message=str(e.detail),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except exceptions.ServiceException as e:
            return error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/all",
        "GET",
        PermissionAction.READ,
        summary="List all items without pagination",
        responses={
            200: {"description": "Items retrieved successfully"},
            500: {"description": "Internal server error"},
        },
    )
    async def list_all(self, request: Request):
        try:
            filters: Dict[str, Any] = {}
            for k, item in request.query_params.items():
                filters[k] = item
            result = await self.service.get_all(**filters)
            return success_response(data=result["data"], message=result["message"])
        except exceptions.ServiceException as e:
            return error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/",
        "GET",
        PermissionAction.READ,
        summary="List items",
        responses={
            200: {"description": "Items retrieved successfully"},
            500: {"description": "Internal server error"},
        },
    )
    async def list_items(
            self,
            request: Request,
            page: int = Query(1, ge=1),
            per_page: int = Query(10, ge=1, le=100),
            include_deleted: bool = Query(False),
            query: Optional[str] = Query(None),
    ):
        try:
            filters: Dict[str, Any] = {}
            for k, item in request.query_params.items():
                filters[k] = item

            result = await self.service.get_list(
                page=int(filters.pop("page", page)),
                per_page=int(filters.pop("per_page", per_page)),
                include_deleted=bool(filters.pop("include_deleted", include_deleted)),
                query=query,
                **filters,
            )
            return paginated_response(
                items=result["items"],
                total=result["total"],
                page=result["page"],
                per_page=result["per_page"],
                pages=result["pages"],
                message=result["message"],
            )
        except exceptions.ServiceException as e:
            return error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/",
        "POST",
        PermissionAction.CREATE,
        status_code=status.HTTP_201_CREATED,
        summary="Create new item",
        responses={
            201: {"description": "Item created successfully"},
            400: {"description": "Bad request"},
            422: {"description": "Validation error"},
            500: {"description": "Internal server error"},
        },
    )
    async def create_item(self, item_data: dict):
        if not self.create_schema:
            return error_response(
                error_code="SCHEMA_ERROR",
                message="Create schema not provided",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        try:
            # Validate input using the provided schema
            try:
                validated = (
                    self.create_schema.model_validate(item_data)
                    if hasattr(self.create_schema, "model_validate")
                    else self.create_schema(**item_data)
                )
            except ValidationError as ve:
                raise exceptions.ValidationException(
                    detail=str(ve),
                    error_details=[
                        {k: v for k, v in d.items() if k != "ctx"} for d in ve.errors()
                    ],
                )
            except Exception as ve:
                raise exceptions.ValidationException(detail=str(ve), error_details=[])

            result = await self.service.create(validated)
            return success_response(
                data=result["data"],
                message=result["message"],
                status_code=status.HTTP_201_CREATED,
            )
        except exceptions.ValidationException as e:
            return error_response(
                error_code="VALIDATION_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=[
                    (detail.model_dump() if isinstance(detail, BaseModel) else detail)
                    for detail in e.error_details
                ],
            )
        except exceptions.ConflictException as e:
            return error_response(
                error_code="CONFLICT",
                message=str(e.detail),
                status_code=status.HTTP_409_CONFLICT,
                details=[
                    (detail.model_dump() if isinstance(detail, BaseModel) else detail)
                    for detail in e.error_details
                ],
            )
        except exceptions.ServiceException as e:
            return error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/{item_id}/",
        "PUT",
        PermissionAction.UPDATE,
        summary="Update item",
        responses={
            200: {"description": "Item updated successfully"},
            404: {"description": "Item not found"},
            422: {"description": "Validation error"},
            500: {"description": "Internal server error"},
        },
    )
    async def update_item(self, item_id: int, item_data: dict):
        if not self.update_schema:
            return error_response(
                error_code="SCHEMA_ERROR",
                message="Update schema not provided",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        try:
            try:
                validated = (
                    self.update_schema.model_validate(item_data)
                    if hasattr(self.update_schema, "model_validate")
                    else self.update_schema(**item_data)
                )
            except ValidationError as ve:
                raise exceptions.ValidationException(
                    detail=str(ve),
                    error_details=[
                        {k: v for k, v in d.items() if k != "ctx"} for d in ve.errors()
                    ],
                )
            except Exception as ve:
                raise exceptions.ValidationException(detail=str(ve))

            result = await self.service.update(item_id, validated)

            return success_response(
                data=result["data"],
                message=result["message"],
                status_code=status.HTTP_200_OK,
            )
        except exceptions.NotFoundException as e:
            return error_response(
                error_code="NOT_FOUND",
                message=str(e.detail),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except exceptions.ValidationException as e:
            return error_response(
                error_code="VALIDATION_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=e.error_details,
            )
        except exceptions.ServiceException as e:
            return error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/{item_id}/",
        "DELETE",
        PermissionAction.DELETE,
        summary="Soft delete item",
        responses={
            200: {"description": "Item soft deleted successfully"},
            404: {"description": "Item not found"},
            500: {"description": "Internal server error"},
        },
    )
    async def soft_delete_item(self, item_id: int):
        try:
            result = await self.service.soft_delete(item_id)
            return success_response(data=result["data"], message=result["message"])
        except exceptions.NotFoundException as e:
            return error_response(
                error_code="NOT_FOUND",
                message=str(e.detail),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except exceptions.ServiceException as e:
            return error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/{item_id}/restore",
        "PATCH",
        PermissionAction.RESTORE,
        summary="Restore soft deleted item",
        responses={
            200: {"description": "Item restored successfully"},
            404: {"description": "Item not found"},
            500: {"description": "Internal server error"},
        },
    )
    async def restore_item(self, item_id: int):
        try:
            result = await self.service.restore(item_id)
            return success_response(data=result["data"], message=result["message"])
        except exceptions.NotFoundException as e:
            return error_response(
                error_code="NOT_FOUND",
                message=str(e.detail),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except exceptions.ServiceException as e:
            return error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/{item_id}/force",
        "DELETE",
        PermissionAction.FORCE_DELETE,
        summary="Permanently delete item",
        responses={
            200: {"description": "Item permanently deleted successfully"},
            404: {"description": "Item not found"},
            500: {"description": "Internal server error"},
        },
    )
    async def force_delete_item(self, item_id: int):
        try:
            result = await self.service.force_delete(item_id)
            return success_response(data=result["data"], message=result["message"])
        except exceptions.NotFoundException as e:
            return error_response(
                error_code="NOT_FOUND",
                message=str(e.detail),
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except exceptions.ServiceException as e:
            return error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/count",
        "GET",
        PermissionAction.READ,
        summary="Count items",
        responses={
            200: {"description": "Count retrieved successfully"},
            500: {"description": "Internal server error"},
        },
    )
    async def count_items(self, include_deleted: bool = Query(False)):
        try:
            result = await self.service.count(include_deleted=include_deleted)
            return success_response(data=result["data"], message=result["message"])
        except exceptions.ServiceException as e:
            return error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/{item_id}/exists",
        "GET",
        PermissionAction.READ,
        summary="Check if item exists",
        responses={
            200: {"description": "Existence check completed"},
            500: {"description": "Internal server error"},
        },
    )
    async def check_exists(self, item_id: int, include_deleted: bool = Query(False)):
        try:
            result = await self.service.exists(
                item_id=item_id, include_deleted=include_deleted
            )
            return success_response(data=result["data"], message=result["message"])
        except exceptions.ServiceException as e:
            return error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/bulk",
        "POST",
        PermissionAction.CREATE,
        status_code=status.HTTP_201_CREATED,
        summary="Bulk create items",
        responses={
            201: {"description": "Items created successfully"},
            400: {"description": "Bad request"},
            422: {"description": "Validation error"},
            500: {"description": "Internal server error"},
        },
    )
    async def bulk_create_items(self, items_data: list):
        if not self.create_schema:
            return error_response(
                error_code="SCHEMA_ERROR",
                message="Create schema not provided",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        try:
            # Validate each item
            validated_items = []
            for d in items_data:
                try:
                    validated = (
                        self.create_schema.model_validate(d)
                        if hasattr(self.create_schema, "model_validate")
                        else self.create_schema(**d)
                    )
                    validated_items.append(validated)
                except ValidationError as ve:
                    raise exceptions.ValidationException(
                        detail=str(ve),
                        error_details=[
                            {k: v for k, v in d.items() if k != "ctx"}
                            for d in ve.errors()
                        ],
                    )
                except Exception as ve:
                    raise exceptions.ValidationException(
                        detail=str(ve), error_details=[]
                    )

            result = await self.service.bulk_create(validated_items)
            return success_response(
                data=result["data"],
                message=result["message"],
                status_code=status.HTTP_201_CREATED,
            )
        except exceptions.ValidationException as e:
            return error_response(
                error_code="VALIDATION_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=[detail.model_dump() for detail in e.error_details],
            )
        except exceptions.ConflictException as e:
            return error_response(
                error_code="CONFLICT",
                message=str(e.detail),
                status_code=status.HTTP_409_CONFLICT,
                details=[detail.model_dump() for detail in e.error_details],
            )
        except exceptions.ServiceException as e:
            return error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/bulk",
        "PUT",
        PermissionAction.UPDATE,
        summary="Bulk update items",
        responses={
            200: {"description": "Items updated successfully"},
            400: {"description": "Bad request"},
            422: {"description": "Validation error"},
            500: {"description": "Internal server error"},
        },
    )
    async def bulk_update_items(self, items_data: list):
        if not self.update_schema:
            return error_response(
                error_code="SCHEMA_ERROR",
                message="Update schema not provided",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        try:
            update_list = []
            for item in items_data:
                # Expecting dicts with id and data
                item_id = item.get("id")
                data = item.get("data")
                try:
                    validated = (
                        self.update_schema.model_validate(data)
                        if hasattr(self.update_schema, "model_validate")
                        else self.update_schema(**data)
                    )

                except ValidationError as ve:
                    raise exceptions.ValidationException(
                        detail=str(ve),
                        error_details=[
                            {k: v for k, v in d.items() if k != "ctx"}
                            for d in ve.errors()
                        ],
                    )
                except Exception as ve:
                    raise exceptions.ValidationException(
                        detail=str(ve), error_details=[]
                    )
                update_list.append({"id": item_id, "data": validated})

            result = await self.service.bulk_update(update_list)
            return success_response(data=result["data"], message=result["message"])
        except exceptions.ValidationException as e:
            return error_response(
                error_code="VALIDATION_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=[detail.model_dump() for detail in e.error_details],
            )
        except exceptions.ServiceException as e:
            return error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/delete/bulk",
        "POST",
        PermissionAction.DELETE,
        summary="Bulk delete items",
        responses={
            200: {"description": "Items deleted successfully"},
            400: {"description": "Bad request"},
            422: {"description": "Validation error"},
            500: {"description": "Internal server error"},
        },
    )
    async def bulk_delete(self, ids: List[int]):
        try:
            result = await self.service.bulk_delete(ids)
            return success_response(data=result["data"], message=result["message"])
        except exceptions.ValidationException as e:
            return error_response(
                error_code="VALIDATION_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=[detail.model_dump() for detail in e.error_details],
            )
        except exceptions.ServiceException as e:
            return error_response(
                error_code="SERVICE_ERROR",
                message=str(e.detail),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/logs",
        "GET",
        PermissionAction.LOGS,
        summary="Get logs",
        responses={
            200: {"description": "Logs retrieved successfully"},
            500: {"description": "Internal server error"},
        },
    )
    async def get_logs(
            self,
            request: Request,
            page: int = 1,
            per_page: int = 10,
            include_deleted: bool = False,
            query: Optional[str] = None,
    ):
        try:
            # Build filters from raw query params so arbitrary filtering keys are captured
            filters: Dict[str, Any] = {}
            for k, v in request.query_params.items():
                # Skip parameters explicitly handled by function signature
                if k in {"page", "per_page", "include_deleted", "query"}:
                    continue
                filters[k] = v

            result = await self.service.get_logs(
                page=page,
                per_page=per_page,
                include_deleted=include_deleted,
                query=query,
                **filters,
            )
            return paginated_response(
                items=result["items"],
                total=result["total"],
                page=result["page"],
                per_page=result["per_page"],
                pages=result["pages"],
                message=result["message"],
            )
        except Exception as e:
            return error_response(
                error_code="LOGS_ERROR",
                message=f"Error retrieving logs: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # Field and form endpoints previously registered directly without permission decorators.
    # Keep the same behavior by setting need_auth=False on the decorator.

    @add_route(
        "/model/fields",
        "GET",
        PermissionAction.READ,
        need_auth=False,
        summary="Get model field definitions",
        response_model=ModelDefinition,
    )
    async def get_model_fields(self):
        try:
            model_class = self.service.repository.model
            return success_response(
                data=self.service.get_model_field_definitions(model_class).model_dump(),
                message=f"Field definitions for {model_class.__name__} retrieved successfully",
            )
        except Exception as e:
            return error_response(
                error_code="FIELD_DEFINITION_ERROR",
                message=f"Error retrieving field definitions: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/model/form-config",
        "GET",
        PermissionAction.READ,
        need_auth=False,
        summary="Get dynamic form configuration",
        response_model=DynamicFormConfig,
    )
    async def get_form_config(self):
        try:
            model_class = self.service.repository.model
            return success_response(
                data=self.service.get_dynamic_form_config(model_class).model_dump(),
                message=f"Form configuration for {model_class.__name__} retrieved successfully",
            )
        except Exception as e:
            return error_response(
                error_code="FORM_CONFIG_ERROR",
                message=f"Error retrieving form configuration: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @add_route(
        "/enum/{enum_name}/",
        "GET",
        PermissionAction.READ,
        need_auth=False,
        summary="Get enum definitions",
        responses={
            200: {"description": "Enum definitions retrieved successfully"},
            500: {"description": "Internal server error"},
        },
    )
    async def get_enum_definitions(self, enum_name: str):
        try:
            enum_data = self.service.get_enum_definitions(
                enum_name, self._app_name if self._app_name else "common"
            )
            return success_response(
                data=enum_data.get("data", []),
                message=enum_data.get("message", ""),
            )
        except Exception as e:
            return error_response(
                error_code="ENUM_DEFINITION_ERROR",
                message=f"Error retrieving enum definitions: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
