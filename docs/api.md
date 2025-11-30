# API & CRUD

The project uses a powerful base router and CRUD API system to automatically generate RESTful endpoints for your models.

## Base Router (`core/bases/base_router.py`)

The `BaseRouter` class is the foundation for all API routers. It handles:

- **Authentication**: Automatically applies `get_current_active_user` dependency if `_need_auth` is True.
- **Middleware**: Applies registered middlewares.
- **Route Registration**: Automatically registers methods decorated with `@add_route`.
- **Permissions**: Wraps endpoints with `require_permissions` to enforce role-based access control.

## CRUD API (`core/bases/crud_api.py`)

The `CRUDApi` class inherits from `BaseRouter` and provides a full suite of CRUD endpoints for a given service.

### Standard Endpoints

- **GET `/{id}/`**: Get item by ID.
- **GET `/`**: List items with pagination (`page`, `per_page`, `sort_by`, `sort_order`).
- **GET `/all`**: List all items without pagination.
- **POST `/`**: Create a new item.
- **PUT `/{id}/`**: Update an item.
- **DELETE `/{id}/`**: Soft delete an item.
- **PATCH `/{id}/restore`**: Restore a soft-deleted item.
- **DELETE `/{id}/force`**: Permanently delete an item.

### Bulk Operations

- **POST `/bulk`**: Bulk create items.
- **PUT `/bulk`**: Bulk update items.
- **POST `/delete/bulk`**: Bulk soft delete items.

### Utility Endpoints

- **GET `/count`**: Get total count of items.
- **GET `/{id}/exists`**: Check if an item exists.
- **GET `/logs`**: Get audit logs for the resource.
- **GET `/model/fields`**: Get model field definitions (for dynamic UIs).
- **GET `/model/form-config`**: Get dynamic form configuration.

### Usage

To create a CRUD router for a resource:

```python
from core.bases.crud_api import CRUDApi
from my_app.services import MyService
from my_app.schemas import MyCreateSchema, MyUpdateSchema

router = CRUDApi(
    service=MyService(),
    resource_name="my_resource",
    create_schema=MyCreateSchema,
    update_schema=MyUpdateSchema,
).get_router()
```
