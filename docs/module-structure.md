# Module Structure Guide

This guide explains how modules are organized in the modular monolith architecture.

## Module Directory Structure

Each module follows a consistent structure:

```
core/apps/<module_name>/
├── __init__.py              # Module initialization and router exports
├── models/                  # SQLModel database models
│   ├── __init__.py
│   └── <model>.py
├── schemas/                 # Pydantic schemas for API
│   ├── __init__.py
│   └── <model>.py
├── repositories/            # Data access layer
│   ├── __init__.py
│   └── <model>_repository.py
├── services/                # Business logic layer
│   ├── __init__.py
│   └── <model>_service.py
├── routers/                 # FastAPI routers
│   ├── __init__.py
│   └── <model>_router.py
├── middlewares/             # Module-specific middleware (optional)
│   └── __init__.py
├── utils/                   # Utility functions (optional)
│   └── __init__.py
└── enums/                   # Enumerations (optional)
    └── __init__.py
```

## Layer Responsibilities

### Models (`models/`)

Database models using SQLModel. These represent your database tables.

```python
from sqlmodel import Field
from core.database import BaseModel

class User(BaseModel, table=True):
    __tablename__ = "users"
    
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    password: str
    is_active: bool = Field(default=True)
```

**Key Points:**
- Inherit from `BaseModel` for soft-delete support
- Use `table=True` to create database tables
- Define `__tablename__` explicitly

### Schemas (`schemas/`)

Pydantic schemas for request/response validation.

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
```

**Key Points:**
- Separate schemas for Create, Update, and Response
- Use Pydantic validators for data validation
- Never include sensitive data (like passwords) in response schemas

### Repositories (`repositories/`)

Data access layer handling all database operations.

```python
from core.bases.base_repository import BaseRepository
from ..models.user import User

class UserRepository(BaseRepository[User]):
    model = User
    _search_fields = ["username", "email"]
    
    # Custom methods
    async def get_by_username(self, username: str) -> User | None:
        async with self.get_session() as session:
            stmt = select(self.model).where(self.model.username == username)
            result = await session.exec(stmt)
            return result.first()
```

**Key Points:**
- Inherit from `BaseRepository[Model]`
- Set `model` class attribute
- Add `_search_fields` for search functionality
- Override methods for custom queries

### Services (`services/`)

Business logic layer handling operations and validation.

```python
from core.bases.base_service import BaseService
from core import exceptions
from ..repositories.user_repository import UserRepository

class UserService(BaseService):
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
    
    async def _validate_create(self, create_data: dict) -> None:
        # Check if username already exists
        existing = await self.repository.get_by_username(create_data.get("username"))
        if existing:
            raise exceptions.ConflictException(detail="Username already exists")
    
    async def get_by_username(self, username: str) -> dict:
        user = await self.repository.get_by_username(username)
        if not user:
            raise exceptions.NotFoundException(detail="User not found")
        return {"data": user, "message": "User found"}
```

**Key Points:**
- Inherit from `BaseService`
- Inject repository in constructor
- Override `_validate_create`, `_validate_update` for validation
- Raise appropriate exceptions

### Routers (`routers/`)

FastAPI routers handling HTTP endpoints.

```python
from core.bases.crud_api import CRUDApi
from core.router import add_route
from core.config import PermissionAction
from core.database import get_session
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserCreate, UserUpdate

def get_service():
    return UserService(UserRepository(get_session))

class UserRouter(CRUDApi):
    _need_auth = True  # Require authentication
    
    def __init__(self):
        super().__init__(
            service=get_service(),
            resource_name="users",
            create_schema=UserCreate,
            update_schema=UserUpdate,
            tags=["Users"],
        )
    
    # Custom endpoint
    @add_route(
        path="/by-username/{username}",
        method="GET",
        action=PermissionAction.READ,
    )
    async def get_by_username(self, username: str):
        return await self.service.get_by_username(username)

router = UserRouter()
```

**Key Points:**
- Use `CRUDApi` for automatic CRUD endpoints
- Use `@add_route` decorator for custom endpoints
- Set `_need_auth = False` for public endpoints
- Export router instance

## Module Registration

### 1. Module `__init__.py`

Export routers from the module:

```python
# core/apps/my_module/__init__.py
from .routers.user_router import router as user_router
from .routers.other_router import router as other_router

routers = [user_router, other_router]

# Export models for migrations
from .models.user import User
from .models.other import Other

__all__ = ["User", "Other"]
```

### 2. Module Registry

Register in `core/module_registry.py`:

```python
from core.apps.auth import routers as auth_routers
from core.apps.archive import routers as archive_routers
from core.apps.base import routers as base_routers
from core.apps.my_module import routers as my_module_routers  # Add this

def get_all_routers():
    return [
        *auth_routers,
        *archive_routers,
        *base_routers,
        *my_module_routers,  # Add this
    ]
```

## Built-in CRUD Endpoints

When using `CRUDApi`, you get these endpoints automatically:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/{resource}/` | List items (paginated) |
| GET | `/{resource}/all` | List all items |
| GET | `/{resource}/{id}/` | Get item by ID |
| POST | `/{resource}/` | Create item |
| PUT | `/{resource}/{id}/` | Update item |
| DELETE | `/{resource}/{id}/` | Soft delete item |
| PATCH | `/{resource}/{id}/restore` | Restore deleted item |
| DELETE | `/{resource}/{id}/force` | Permanently delete |
| GET | `/{resource}/count` | Count items |
| GET | `/{resource}/{id}/exists` | Check if exists |
| POST | `/{resource}/bulk` | Bulk create |
| PUT | `/{resource}/bulk` | Bulk update |
| POST | `/{resource}/delete/bulk` | Bulk delete |
| GET | `/{resource}/logs` | Get audit logs |

## Existing Modules

### Auth Module (`core/apps/auth/`)

Handles authentication and authorization:
- Users, Roles, Groups, Permissions
- JWT token management
- Role-based access control

### Archive Module (`core/apps/archive/`)

Handles file management:
- File uploads
- Document types
- Archive management

### Base Module (`core/apps/base/`)

Provides base utilities:
- Audit logging
- Common utilities

## Best Practices

1. **Keep Modules Independent**
   - Avoid importing from other modules
   - Use events for cross-module communication

2. **Use Repository Pattern**
   - All database access through repositories
   - No direct database calls in services or routers

3. **Service Layer Logic**
   - Put business logic in services
   - Keep routers thin (just HTTP handling)

4. **Consistent Naming**
   - `<model>_repository.py`
   - `<model>_service.py`
   - `<model>_router.py`

5. **Type Hints**
   - Use type hints everywhere
   - Helps with IDE support and documentation

6. **Validation**
   - Use Pydantic schemas for input validation
   - Use service `_validate_*` methods for business rules
