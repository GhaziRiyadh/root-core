# API Reference - Root Core Python Library

## Core Modules

### core.database

#### BaseModel

Base model class for all entities with soft-delete support.

```python
from core.database import BaseModel
from sqlmodel import Field

class MyModel(BaseModel, table=True):
    __tablename__ = "my_models"
    
    # Inherited fields (don't redefine):
    # - id: Optional[int] - Primary key
    # - is_deleted: bool - Soft delete flag
    
    # Your custom fields:
    name: str = Field(max_length=200)
```

**Inherited Fields**:
- `id: Optional[int]` - Auto-incrementing primary key
- `is_deleted: bool` - Soft delete flag (default: False)
- `created_at: datetime` - Timestamp fields (commented out by default, uncomment in database.py if needed)
- `updated_at: datetime` - Update timestamp (commented out by default)

#### get_session()

Async context manager for database sessions.

```python
from core.database import get_session

async with get_session() as session:
    result = await session.exec(select(MyModel))
    items = result.all()
```

**Returns**: `AsyncSession` - SQLModel async session

#### get_local_session()

Sync context manager for database sessions (use for migrations or non-async contexts).

```python
from core.database import get_local_session

with get_local_session() as session:
    result = session.exec(select(MyModel))
    items = result.all()
```

**Returns**: `Session` - SQLModel sync session

---

### core.bases.base_repository

#### BaseRepository

Base repository class for data access operations.

```python
from core.bases.base_repository import BaseRepository

class MyRepository(BaseRepository):
    def __init__(self):
        super().__init__(MyModel)
```

**Constructor Parameters**:
- `model: Type[BaseModel]` - The SQLModel class to manage

**Methods**:

##### get()
Get a single item by ID.

```python
async def get(
    item_id: Any,
    include_deleted: bool = False,
    **filters
) -> Any
```

**Parameters**:
- `item_id` - Primary key value
- `include_deleted` - Include soft-deleted items (default: False)
- `**filters` - Additional filter conditions

**Returns**: Model instance or None

**Example**:
```python
product = await repository.get(item_id=1)
```

##### get_one()
Get a single item by filter conditions.

```python
async def get_one(**filters) -> Any
```

**Parameters**:
- `**filters` - Filter conditions (e.g., name="Product")

**Returns**: Model instance or None

**Example**:
```python
product = await repository.get_one(name="Laptop")
```

##### get_all()
Get all items matching filters.

```python
async def get_all(
    include_deleted: bool = False,
    **filters
) -> List[Any]
```

**Parameters**:
- `include_deleted` - Include soft-deleted items
- `**filters` - Filter conditions

**Returns**: List of model instances

**Example**:
```python
products = await repository.get_all(category="Electronics")
```

##### list()
Get paginated list of items.

```python
async def list(
    page: int = 1,
    per_page: int = 10,
    include_deleted: bool = False,
    **filters
) -> PaginatedResponse
```

**Parameters**:
- `page` - Page number (starts at 1)
- `per_page` - Items per page (max 100)
- `include_deleted` - Include soft-deleted items
- `**filters` - Filter conditions

**Returns**: `PaginatedResponse` with items, total, page info

**Example**:
```python
result = await repository.list(page=1, per_page=20, category="Electronics")
```

##### get_many()
Get multiple items without pagination metadata.

```python
async def get_many(
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    **filters
) -> List[Any]
```

**Parameters**:
- `skip` - Number of items to skip
- `limit` - Maximum number of items
- `include_deleted` - Include soft-deleted items
- `**filters` - Filter conditions

**Returns**: List of model instances

**Example**:
```python
products = await repository.get_many(skip=0, limit=50)
```

##### create()
Create a new item.

```python
async def create(data: Dict[str, Any]) -> Any
```

**Parameters**:
- `data` - Dictionary with field values

**Returns**: Created model instance

**Example**:
```python
product = await repository.create({
    "name": "Laptop",
    "price": 999.99
})
```

##### update()
Update an existing item.

```python
async def update(
    item_id: Any,
    data: Dict[str, Any]
) -> Any
```

**Parameters**:
- `item_id` - Primary key value
- `data` - Dictionary with updated field values

**Returns**: Updated model instance or None

**Example**:
```python
product = await repository.update(1, {"price": 899.99})
```

##### soft_delete()
Soft delete an item (marks as deleted).

```python
async def soft_delete(item_id: Any) -> bool
```

**Parameters**:
- `item_id` - Primary key value

**Returns**: True if successful, False otherwise

**Example**:
```python
success = await repository.soft_delete(1)
```

##### restore()
Restore a soft-deleted item.

```python
async def restore(item_id: Any) -> bool
```

**Parameters**:
- `item_id` - Primary key value

**Returns**: True if successful, False otherwise

**Example**:
```python
success = await repository.restore(1)
```

##### force_delete()
Permanently delete an item from database.

```python
async def force_delete(item_id: Any) -> bool
```

**Parameters**:
- `item_id` - Primary key value

**Returns**: True if successful, False otherwise

**Example**:
```python
success = await repository.force_delete(1)
```

##### bulk_create()
Create multiple items at once.

```python
async def bulk_create(
    data_list: List[Dict[str, Any]]
) -> List[Any]
```

**Parameters**:
- `data_list` - List of dictionaries with field values

**Returns**: List of created model instances

**Example**:
```python
products = await repository.bulk_create([
    {"name": "Product 1", "price": 10},
    {"name": "Product 2", "price": 20}
])
```

##### bulk_update()
Update multiple items at once.

```python
async def bulk_update(
    data_list: List[Dict[str, Any]]
) -> List[Any]
```

**Parameters**:
- `data_list` - List of dictionaries with id and updated fields

**Returns**: List of updated model instances

**Example**:
```python
products = await repository.bulk_update([
    {"id": 1, "price": 15},
    {"id": 2, "price": 25}
])
```

##### bulk_delete()
Soft delete multiple items at once.

```python
async def bulk_delete(ids: List[int]) -> int
```

**Parameters**:
- `ids` - List of primary key values

**Returns**: Number of items deleted

**Example**:
```python
count = await repository.bulk_delete([1, 2, 3])
```

##### exists()
Check if an item exists.

```python
async def exists(
    item_id: Any,
    include_deleted: bool = False
) -> bool
```

**Parameters**:
- `item_id` - Primary key value
- `include_deleted` - Include soft-deleted items

**Returns**: True if exists, False otherwise

**Example**:
```python
exists = await repository.exists(1)
```

##### count()
Count items matching filters.

```python
async def count(
    include_deleted: bool = False,
    **filters
) -> int
```

**Parameters**:
- `include_deleted` - Include soft-deleted items
- `**filters` - Filter conditions

**Returns**: Count of matching items

**Example**:
```python
total = await repository.count(category="Electronics")
```

##### search()
Search items by text in specified fields.

```python
async def search(
    query: str,
    fields: List[str]
) -> PaginatedResponse
```

**Parameters**:
- `query` - Search text
- `fields` - List of field names to search

**Returns**: `PaginatedResponse` with matching items

**Example**:
```python
result = await repository.search(
    query="laptop",
    fields=["name", "description"]
)
```

---

### core.bases.base_service

#### BaseService

Base service class for business logic.

```python
from core.bases.base_service import BaseService

class MyService(BaseService):
    def __init__(self, repository):
        super().__init__(repository)
```

**Constructor Parameters**:
- `repository: BaseRepository` - Repository instance

**Methods**:

##### get_all()
Get all items.

```python
async def get_all(
    include_deleted: bool = False,
    **filters
) -> Dict[str, Any]
```

**Returns**: 
```python
{
    "data": [items],
    "message": "Retrieved N items successfully"
}
```

##### get_by_id()
Get single item by ID.

```python
async def get_by_id(
    item_id: Any,
    include_deleted: bool = False,
    **filters
) -> Dict[str, Any]
```

**Returns**: 
```python
{
    "data": item,
    "message": "Item retrieved successfully"
}
```

**Raises**:
- `NotFoundException` - If item not found

##### get_list()
Get paginated list.

```python
async def get_list(
    page: int = 1,
    per_page: int = 10,
    include_deleted: bool = False,
    **filters
) -> Dict[str, Any]
```

**Returns**: 
```python
{
    "items": [items],
    "total": 100,
    "page": 1,
    "per_page": 10,
    "pages": 10,
    "message": "Success"
}
```

##### create()
Create new item.

```python
async def create(
    obj_in: Any,
    **additional_data
) -> Dict[str, Any]
```

**Parameters**:
- `obj_in` - Pydantic model or dict with field values
- `**additional_data` - Additional fields to add

**Returns**: 
```python
{
    "data": item,
    "message": "Item created successfully"
}
```

**Raises**:
- `ValidationException` - If validation fails

##### update()
Update existing item.

```python
async def update(
    item_id: Any,
    obj_in: Any,
    exclude_unset: bool = True,
    **additional_data
) -> Dict[str, Any]
```

**Parameters**:
- `item_id` - Primary key value
- `obj_in` - Pydantic model or dict with updated fields
- `exclude_unset` - Only update provided fields
- `**additional_data` - Additional fields to add

**Returns**: 
```python
{
    "data": item,
    "message": "Item updated successfully"
}
```

**Raises**:
- `NotFoundException` - If item not found
- `ValidationException` - If validation fails

##### soft_delete()
Soft delete item.

```python
async def soft_delete(item_id: int) -> Dict[str, Any]
```

**Returns**: 
```python
{
    "data": None,
    "message": "Item soft deleted successfully"
}
```

##### restore()
Restore soft-deleted item.

```python
async def restore(item_id: Any) -> Dict[str, Any]
```

**Returns**: 
```python
{
    "data": None,
    "message": "Item restored successfully"
}
```

##### force_delete()
Permanently delete item.

```python
async def force_delete(item_id: Any) -> Dict[str, Any]
```

**Returns**: 
```python
{
    "data": None,
    "message": "Item permanently deleted successfully"
}
```

##### bulk_create()
Create multiple items.

```python
async def bulk_create(
    objs_in: List[Any],
    **additional_data
) -> Dict[str, Any]
```

**Returns**: 
```python
{
    "data": [items],
    "message": "Successfully created N items"
}
```

##### bulk_delete()
Delete multiple items.

```python
async def bulk_delete(ids: List[int]) -> Dict[str, Any]
```

**Returns**: 
```python
{
    "data": count,
    "message": "Successfully deleted N items"
}
```

**Validation Methods** (override in subclass):

```python
async def _validate_create(self, create_data: dict):
    """Validate before creating."""
    pass

async def _validate_update(self, item_id, update_data: dict, existing_item):
    """Validate before updating."""
    pass

async def _validate_delete(self, item_id, existing_item):
    """Validate before soft deleting."""
    pass

async def _validate_force_delete(self, item_id, existing_item):
    """Validate before force deleting."""
    pass
```

---

### core.bases.base_router

#### BaseRouter

Base router class for FastAPI endpoints.

```python
from core.bases.base_router import BaseRouter

class MyRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            resource_name="myresource",
            prefix="/api/myresource",
            tags=["MyResource"]
        )
```

**Constructor Parameters**:
- `resource_name: str` - Resource name for permissions
- `tags: Optional[List[str]]` - OpenAPI tags
- `prefix: str` - URL prefix (default: "")
- `create_schema: Optional[Type[BaseModel]]` - Pydantic schema for create
- `update_schema: Optional[Type[BaseModel]]` - Pydantic schema for update
- `response_schema: Optional[Type[BaseModel]]` - Pydantic schema for response
- `dependencies: Optional[List[Callable]]` - FastAPI dependencies
- `is_app: bool` - Create FastAPI app instead of router
- `app_name: Optional[str]` - App name for permissions

**Class Attributes**:
- `_need_auth: bool` - Require authentication (default: True)
- `_middlewares: List[BaseMiddleware]` - Middleware list

**Methods**:

##### get_router()
Get the FastAPI router instance.

```python
def get_router() -> APIRouter
```

**Returns**: `APIRouter` instance

**Example**:
```python
router = MyRouter().get_router()
app.include_router(router)
```

##### include_router()
Include another router.

```python
def include_router(router: APIRouter, **kwargs) -> None
```

**Parameters**:
- `router` - APIRouter to include
- `**kwargs` - Additional arguments for include_router

---

### core.router

#### add_route()

Decorator to register custom routes.

```python
from core.router import add_route
from core.config import PermissionAction

@add_route("/custom", "GET", PermissionAction.READ)
async def custom_endpoint(self):
    return {"message": "Custom"}
```

**Parameters**:
- `path: str` - URL path
- `method: str` - HTTP method ("GET", "POST", "PUT", "DELETE", etc.)
- `action: PermissionAction` - Permission action required
- `need_auth: Optional[bool]` - Override auth requirement
- `**kwargs` - Additional FastAPI route parameters

---

### core.exceptions

Custom exceptions for error handling.

#### RootCoreException
Base exception class.

```python
from core.exceptions import RootCoreException

raise RootCoreException("Error message")
```

#### NotFoundException
Item not found error.

```python
from core.exceptions import NotFoundException

raise NotFoundException("Item with id 1 not found")
```

#### ValidationException
Validation error.

```python
from core.exceptions import ValidationException

raise ValidationException("Price cannot be negative")
```

#### ServiceException
Service layer error.

```python
from core.exceptions import ServiceException

raise ServiceException("Error in service", inner_exception)
```

#### OperationException
Operation failed error.

```python
from core.exceptions import OperationException

raise OperationException("Failed to delete item")
```

---

### core.config

#### settings

Application settings instance.

```python
from core.config import settings

# Access settings
database_uri = settings.DATABASE_URI
secret_key = settings.SECRET_KEY
```

**Available Settings**:
- `DATABASE_URI: str` - Database connection string
- `ASYNC_DATABASE_URI: str` - Async database connection string
- `SECRET_KEY: str` - Secret key for JWT
- `ALGORITHM: str` - JWT algorithm
- `ACCESS_TOKEN_EXPIRE_MINUTES: int` - Token expiration
- `PROJECT_NAME: str` - Project name
- `PROJECT_INFO: str` - Project description
- `PROJECT_VERSION: str` - Project version
- `TIME_ZONE: str` - Timezone
- `UPLOAD_FOLDER: str` - Upload directory
- `STATIC_DIR: str` - Static files directory

#### PermissionAction

Enum for permission actions.

```python
from core.config import PermissionAction

# Available actions:
PermissionAction.CREATE
PermissionAction.READ
PermissionAction.UPDATE
PermissionAction.DELETE
PermissionAction.FORCE_DELETE
PermissionAction.RESTORE
PermissionAction.LOGS
PermissionAction.MANAGE
PermissionAction.COPY
PermissionAction.EXPORT
```

---

### core.response.schemas

#### PaginatedResponse

Response schema for paginated data.

```python
from core.response.schemas import PaginatedResponse

response = PaginatedResponse(
    data=[items],
    total=100,
    page=1,
    per_page=10,
    message="Success"
)
```

**Fields**:
- `data: List[Any]` - List of items
- `total: int` - Total count
- `page: int` - Current page
- `per_page: int` - Items per page
- `pages: int` - Total pages (calculated)
- `message: str` - Response message

---

## Response Formats

All service methods return standardized responses:

### Single Item Response
```python
{
    "data": {
        "id": 1,
        "name": "Product",
        ...
    },
    "message": "Item retrieved successfully"
}
```

### List Response (without pagination)
```python
{
    "data": [
        {"id": 1, "name": "Product 1"},
        {"id": 2, "name": "Product 2"}
    ],
    "message": "Retrieved 2 items successfully"
}
```

### Paginated Response
```python
{
    "items": [
        {"id": 1, "name": "Product 1"},
        {"id": 2, "name": "Product 2"}
    ],
    "total": 100,
    "page": 1,
    "per_page": 10,
    "pages": 10,
    "message": "Success"
}
```

### Error Response
```python
{
    "detail": "Error message",
    "success": False
}
```

---

## Type Hints

Important type hints used throughout the library:

```python
from typing import Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel
from sqlmodel import SQLModel

# Common types
ItemId = Union[int, str]
FilterDict = Dict[str, Any]
DataDict = Dict[str, Any]
ResponseDict = Dict[str, Any]
```

---

This API reference covers all public methods and classes in the Root Core library. For more examples and usage patterns, see the main documentation README.
