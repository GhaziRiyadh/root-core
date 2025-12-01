# API Reference

## Base Classes

### BaseRouter

Base class for creating FastAPI routers with authentication support.

```python
from core.bases.base_router import BaseRouter

class MyRouter(BaseRouter):
    _need_auth = True  # Require authentication (default: True)
    _middlewares = []  # Custom middlewares
    
    def __init__(self):
        super().__init__(
            resource_name="my_resource",
            tags=["My Resource"],
            prefix="/my-resource",
        )
```

**Constructor Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `resource_name` | `str` | Name used for permission checking |
| `tags` | `List[str]` | OpenAPI tags |
| `prefix` | `str` | Route prefix |
| `create_schema` | `Type[BaseModel]` | Schema for create operations |
| `update_schema` | `Type[BaseModel]` | Schema for update operations |
| `response_schema` | `Type[BaseModel]` | Schema for responses |
| `dependencies` | `List[Callable]` | FastAPI dependencies |
| `is_app` | `bool` | Create sub-application instead of router |
| `app_name` | `str` | Application name for permissions |

### CRUDApi

Generic CRUD router with automatic endpoints.

```python
from core.bases.crud_api import CRUDApi

class ItemRouter(CRUDApi):
    def __init__(self):
        super().__init__(
            service=get_service(),
            resource_name="items",
            create_schema=ItemCreate,
            update_schema=ItemUpdate,
            tags=["Items"],
        )
```

**Auto-generated Endpoints:**

| Method | Path | Action |
|--------|------|--------|
| GET | `/` | List items (paginated) |
| GET | `/all` | List all items |
| GET | `/{id}/` | Get by ID |
| POST | `/` | Create item |
| PUT | `/{id}/` | Update item |
| DELETE | `/{id}/` | Soft delete |
| PATCH | `/{id}/restore` | Restore deleted |
| DELETE | `/{id}/force` | Force delete |
| GET | `/count` | Count items |
| GET | `/{id}/exists` | Check existence |
| POST | `/bulk` | Bulk create |
| PUT | `/bulk` | Bulk update |
| POST | `/delete/bulk` | Bulk delete |
| GET | `/logs` | Audit logs |

### BaseService

Base class for business logic services.

```python
from core.bases.base_service import BaseService

class ItemService(BaseService):
    def __init__(self, repository: ItemRepository):
        super().__init__(repository)
    
    async def _validate_create(self, create_data: dict) -> None:
        """Validate before create."""
        pass
    
    async def _validate_update(self, item_id, update_data, existing_item) -> None:
        """Validate before update."""
        pass
    
    async def _validate_delete(self, item_id, existing_item) -> None:
        """Validate before soft delete."""
        pass
```

**Methods:**

| Method | Description |
|--------|-------------|
| `get_all(**filters)` | Get all items |
| `get_by_id(id)` | Get item by ID |
| `get_list(page, per_page, **filters)` | Paginated list |
| `get_many(skip, limit, **filters)` | Get multiple items |
| `create(obj_in)` | Create item |
| `update(id, obj_in)` | Update item |
| `soft_delete(id)` | Soft delete item |
| `restore(id)` | Restore deleted item |
| `force_delete(id)` | Permanently delete |
| `exists(id)` | Check existence |
| `count(**filters)` | Count items |
| `bulk_create(items)` | Create multiple |
| `bulk_update(items)` | Update multiple |
| `bulk_delete(ids)` | Delete multiple |
| `search(query)` | Search items |

### BaseRepository

Base class for data access.

```python
from core.bases.base_repository import BaseRepository

class ItemRepository(BaseRepository[Item]):
    model = Item
    _search_fields = ["name", "description"]
    _options = []  # SQLAlchemy options (e.g., selectinload)
    
    # Custom filter methods
    def filter_status(self, stmt, value):
        return stmt.where(self.model.status == value)
```

**Methods:**

| Method | Description |
|--------|-------------|
| `get(id)` | Get by ID |
| `get_all(**filters)` | Get all |
| `get_one(**filters)` | Get first matching |
| `get_many(skip, limit)` | Get with offset/limit |
| `list(page, per_page)` | Paginated list |
| `create(obj_in)` | Create |
| `update(id, obj_in)` | Update |
| `soft_delete(id)` | Soft delete |
| `restore(id)` | Restore |
| `force_delete(id)` | Hard delete |
| `exists(id)` | Check existence |
| `count(**filters)` | Count |
| `search(query, fields)` | Search |
| `bulk_create(items)` | Bulk create |
| `bulk_update(items)` | Bulk update |
| `bulk_delete(ids)` | Bulk delete |

## Decorators

### @add_route

Register a custom route on a router.

```python
from core.router import add_route
from core.config import PermissionAction

class MyRouter(BaseRouter):
    @add_route(
        path="/custom/{id}",
        method="GET",
        action=PermissionAction.READ,
        need_auth=True,  # Optional, defaults to class setting
        summary="Custom endpoint",
        description="Detailed description",
    )
    async def custom_endpoint(self, id: int):
        return {"id": id}
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` | URL path |
| `method` | `str` | HTTP method |
| `action` | `PermissionAction` | Required permission |
| `need_auth` | `bool` | Override authentication requirement |
| `**kwargs` | | Additional FastAPI route kwargs |

## Permission Actions

```python
from core.config import PermissionAction

PermissionAction.CREATE      # Create permission
PermissionAction.READ        # Read permission
PermissionAction.UPDATE      # Update permission
PermissionAction.DELETE      # Delete permission
PermissionAction.FORCE_DELETE # Permanent delete permission
PermissionAction.RESTORE     # Restore permission
PermissionAction.LOGS        # View logs permission
PermissionAction.MANAGE      # Management permission
PermissionAction.COPY        # Copy permission
PermissionAction.EXPORT      # Export permission
```

## Security Manager

```python
from core.security_manager import security

# Get current user
user = security().user

# Check permissions
has_perm = security().check_permissions({"read"}, "users")

# Create token
token = security().create_access_token({"sub": "username"})

# Hash password
hashed = security().get_password_hash("password")

# Verify password
valid = security().verify_password("password", hashed)
```

## Response Handlers

```python
from core.response.handlers import (
    success_response,
    error_response,
    paginated_response,
)

# Success response
return success_response(data=item, message="Created")

# Error response
return error_response(
    error_code="NOT_FOUND",
    message="Item not found",
    status_code=404,
)

# Paginated response
return paginated_response(
    items=items,
    total=100,
    page=1,
    per_page=10,
    pages=10,
)
```

## Exceptions

```python
from core import exceptions

# Not found
raise exceptions.NotFoundException(detail="Item not found")

# Validation error
raise exceptions.ValidationException(
    detail="Invalid data",
    error_details=[{"field": "name", "message": "Required"}],
)

# Conflict
raise exceptions.ConflictException(detail="Already exists")

# Service error
raise exceptions.ServiceException(detail="Operation failed")

# Operation error
raise exceptions.OperationException(detail="Cannot perform action")
```

## Database

```python
from core.database import get_session, BaseModel
from sqlmodel import Field

# Using session
async with get_session() as session:
    result = await session.exec(select(Item))
    items = result.all()

# Model with soft delete
class Item(BaseModel, table=True):
    __tablename__ = "items"
    
    name: str = Field(index=True)
    # id and is_deleted inherited from BaseModel
```

## Configuration

Access settings via:

```python
from core.config import settings

# Available settings
settings.DATABASE_URI
settings.ASYNC_DATABASE_URI
settings.SECRET_KEY
settings.ALGORITHM
settings.ACCESS_TOKEN_EXPIRE_MINUTES
settings.PROJECT_NAME
settings.PROJECT_INFO
settings.PROJECT_VERSION
settings.TIME_ZONE
settings.UPLOAD_FOLDER
settings.USER_MODEL
settings.LOG_MODEL
settings.APPS_DIR
settings.AUTH_CLASS
```
