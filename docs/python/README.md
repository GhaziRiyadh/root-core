# Root Core - Python FastAPI Library Documentation

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [API Reference](#api-reference)
5. [Usage Examples](#usage-examples)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Installation

### As a Pip Package

To use root-core as a pip-installable library in your FastAPI project:

#### Option 1: Install from source
```bash
pip install git+https://github.com/GhaziRiyadh/root-core.git
```

#### Option 2: Install in development mode
```bash
git clone https://github.com/GhaziRiyadh/root-core.git
cd root-core
pip install -e .
```

#### Option 3: Using Poetry
```bash
poetry add git+https://github.com/GhaziRiyadh/root-core.git
```

### Requirements

```
fastapi>=0.104.0
sqlmodel>=0.0.14
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python>=3.13
```

## Quick Start

### 1. Define Your Model

```python
from sqlmodel import Field, SQLModel
from core.database import BaseModel

class Product(BaseModel, table=True):
    """Product model with soft-delete support."""
    __tablename__ = "products"
    
    name: str = Field(index=True, max_length=200)
    description: str | None = None
    price: float = Field(ge=0, description="Price must be non-negative")
    stock: int = Field(default=0, ge=0)
```

### 2. Create Repository (Optional)

```python
from core.bases.base_repository import BaseRepository

class ProductRepository(BaseRepository):
    """Repository for Product model."""
    
    def __init__(self):
        super().__init__(Product)
    
    # Add custom queries if needed
    async def get_by_name(self, name: str):
        """Get product by name."""
        return await self.get_one(name=name)
```

### 3. Create Service (Optional)

```python
from core.bases.base_service import BaseService
from core.exceptions import ValidationException

class ProductService(BaseService):
    """Service for Product business logic."""
    
    def __init__(self, repository: ProductRepository):
        super().__init__(repository)
    
    async def _validate_create(self, create_data: dict) -> None:
        """Validate product creation."""
        if create_data.get('price', 0) < 0:
            raise ValidationException("Price cannot be negative")
        
        # Check for duplicate name
        existing = await self.repository.get_one(name=create_data.get('name'))
        if existing:
            raise ValidationException(f"Product with name '{create_data['name']}' already exists")
```

### 4. Create Router

```python
from fastapi import APIRouter, Depends
from core.bases.base_router import BaseRouter
from core.router import add_route
from core.config import PermissionAction

class ProductRouter(BaseRouter):
    """Router for Product endpoints."""
    
    def __init__(self):
        super().__init__(
            resource_name="products",
            prefix="/api/products",
            tags=["Products"],
            create_schema=ProductCreate,
            update_schema=ProductUpdate,
            response_schema=ProductResponse
        )
    
    @add_route("/featured", "GET", PermissionAction.READ)
    async def get_featured_products(self):
        """Get featured products."""
        # Custom endpoint logic
        products = await self.service.get_many(limit=10)
        return products

# Get the FastAPI router
router = ProductRouter().get_router()
```

### 5. Setup FastAPI Application

```python
from fastapi import FastAPI
from core.database import engine, BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

app = FastAPI(
    title="My API",
    version="1.0.0"
)

@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(BaseModel.metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    await engine.dispose()

# Include the router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Core Concepts

### Base Model

All models should inherit from `BaseModel` to get soft-delete support:

```python
from core.database import BaseModel

class MyModel(BaseModel, table=True):
    # Automatically includes:
    # - id: int (primary key)
    # - is_deleted: bool (soft delete flag)
    # - created_at: datetime (optional)
    # - updated_at: datetime (optional)
    
    name: str
    # ... your fields
```

### Soft Delete

Soft delete marks records as deleted without removing them from the database:

```python
# Soft delete (sets is_deleted=True)
await service.soft_delete(item_id=1)

# Query excludes soft-deleted by default
items = await service.get_all()  # Only non-deleted

# Include soft-deleted items
items = await service.get_all(include_deleted=True)

# Restore soft-deleted item
await service.restore(item_id=1)

# Permanently delete (removes from database)
await service.force_delete(item_id=1)
```

### Repository Pattern

Repository handles data access:

```python
from core.bases.base_repository import BaseRepository

class MyRepository(BaseRepository):
    def __init__(self):
        super().__init__(MyModel)
    
    # Available methods:
    # - get(item_id, **filters)
    # - get_one(**filters)
    # - get_all(**filters)
    # - list(page, per_page, **filters)
    # - get_many(skip, limit, **filters)
    # - create(data)
    # - update(item_id, data)
    # - soft_delete(item_id)
    # - restore(item_id)
    # - force_delete(item_id)
    # - bulk_create(data_list)
    # - bulk_update(data_list)
    # - bulk_delete(ids)
    # - exists(item_id)
    # - count(**filters)
    # - search(query, fields)
```

### Service Pattern

Service handles business logic:

```python
from core.bases.base_service import BaseService

class MyService(BaseService):
    def __init__(self, repository):
        super().__init__(repository)
    
    # Override validation methods:
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

### Router Pattern

Router creates FastAPI endpoints:

```python
from core.bases.base_router import BaseRouter
from core.router import add_route
from core.config import PermissionAction

class MyRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            resource_name="myresource",
            prefix="/api/myresource",
            tags=["MyResource"]
        )
    
    # Add custom routes using decorator
    @add_route("/custom", "GET", PermissionAction.READ)
    async def custom_endpoint(self):
        return {"message": "Custom endpoint"}
```

## API Reference

### BaseModel

```python
class BaseModel(SQLModel):
    """Base model with soft-delete support."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    is_deleted: bool = Field(default=False)
    # created_at: datetime (optional)
    # updated_at: datetime (optional)
```

### BaseRepository

```python
class BaseRepository:
    """Base repository for data access."""
    
    async def get(item_id: Any, include_deleted: bool = False, **filters) -> Any
    async def get_one(**filters) -> Any
    async def get_all(include_deleted: bool = False, **filters) -> List[Any]
    async def list(page: int, per_page: int, include_deleted: bool = False, **filters) -> PaginatedResponse
    async def get_many(skip: int, limit: int, include_deleted: bool = False, **filters) -> List[Any]
    async def create(data: Dict[str, Any]) -> Any
    async def update(item_id: Any, data: Dict[str, Any]) -> Any
    async def soft_delete(item_id: Any) -> bool
    async def restore(item_id: Any) -> bool
    async def force_delete(item_id: Any) -> bool
    async def bulk_create(data_list: List[Dict[str, Any]]) -> List[Any]
    async def bulk_update(data_list: List[Dict[str, Any]]) -> List[Any]
    async def bulk_delete(ids: List[int]) -> int
    async def exists(item_id: Any, include_deleted: bool = False) -> bool
    async def count(include_deleted: bool = False, **filters) -> int
    async def search(query: str, fields: List[str]) -> PaginatedResponse
```

### BaseService

```python
class BaseService:
    """Base service for business logic."""
    
    async def get_all(include_deleted: bool = False, **filters) -> Dict[str, Any]
    async def get_by_id(item_id: Any, include_deleted: bool = False, **filters) -> Dict[str, Any]
    async def get_list(page: int, per_page: int, include_deleted: bool = False, **filters) -> Dict[str, Any]
    async def get_many(skip: int, limit: int, include_deleted: bool = False, **filters) -> Dict[str, Any]
    async def create(obj_in: Any, **additional_data) -> Dict[str, Any]
    async def update(item_id: Any, obj_in: Any, exclude_unset: bool = True, **additional_data) -> Dict[str, Any]
    async def soft_delete(item_id: int) -> Dict[str, Any]
    async def restore(item_id: Any) -> Dict[str, Any]
    async def force_delete(item_id: Any) -> Dict[str, Any]
    async def exists(item_id: Any, include_deleted: bool = False) -> Dict[str, Any]
    async def count(include_deleted: bool = False, **filters) -> Dict[str, Any]
    async def bulk_create(objs_in: List[Any], **additional_data) -> Dict[str, Any]
    async def bulk_update(objs_in: List[Any], **additional_data) -> Dict[str, Any]
    async def bulk_delete(ids: List[int]) -> Dict[str, Any]
    async def search(query: str) -> Dict[str, Any]
```

### BaseRouter

```python
class BaseRouter:
    """Base router for FastAPI endpoints."""
    
    def __init__(
        resource_name: str,
        tags: Optional[List[str]] = None,
        prefix: str = "",
        create_schema: Optional[Type[BaseModel]] = None,
        update_schema: Optional[Type[BaseModel]] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        dependencies: Optional[List[Callable]] = None,
        is_app: bool = False,
        app_name: Optional[str] = None
    )
    
    def get_router() -> APIRouter
    def include_router(router: APIRouter, **kwargs) -> None
```

## Usage Examples

### Complete Example: Todo API

```python
# models.py
from sqlmodel import Field
from core.database import BaseModel

class Todo(BaseModel, table=True):
    __tablename__ = "todos"
    
    title: str = Field(max_length=200)
    description: str | None = None
    completed: bool = Field(default=False)
    priority: int = Field(default=1, ge=1, le=5)

# schemas.py
from pydantic import BaseModel

class TodoCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False
    priority: int = 1

class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    priority: int | None = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    priority: int
    is_deleted: bool

# repository.py
from core.bases.base_repository import BaseRepository

class TodoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Todo)
    
    async def get_by_priority(self, priority: int):
        return await self.get_all(priority=priority)
    
    async def get_completed(self):
        return await self.get_all(completed=True)

# service.py
from core.bases.base_service import BaseService
from core.exceptions import ValidationException

class TodoService(BaseService):
    def __init__(self, repository: TodoRepository):
        super().__init__(repository)
    
    async def _validate_create(self, create_data: dict):
        if not create_data.get('title'):
            raise ValidationException("Title is required")
        
        if create_data.get('priority', 1) not in range(1, 6):
            raise ValidationException("Priority must be between 1 and 5")
    
    async def mark_completed(self, item_id: int):
        """Mark todo as completed."""
        return await self.update(item_id, {"completed": True})

# router.py
from core.bases.base_router import BaseRouter
from core.router import add_route
from core.config import PermissionAction

class TodoRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            resource_name="todos",
            prefix="/api/todos",
            tags=["Todos"],
            create_schema=TodoCreate,
            update_schema=TodoUpdate,
            response_schema=TodoResponse
        )
    
    @add_route("/{item_id}/complete", "POST", PermissionAction.UPDATE)
    async def mark_complete(self, item_id: int):
        """Mark a todo as completed."""
        result = await self.service.mark_completed(item_id)
        return result
    
    @add_route("/completed", "GET", PermissionAction.READ)
    async def get_completed(self):
        """Get all completed todos."""
        result = await self.repository.get_completed()
        return {"data": result, "message": "Retrieved completed todos"}

router = TodoRouter().get_router()

# main.py
from fastapi import FastAPI
from core.database import engine, BaseModel

app = FastAPI(title="Todo API", version="1.0.0")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Configuration

### Environment Variables

Create a `.env` file:

```env
# Database
DATABASE_URL=sqlite:///./database.db
ASYNC_DATABASE_URL=sqlite+aiosqlite:///./database.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
PROJECT_NAME=My FastAPI Project
PROJECT_INFO=My Project Description
PROJECT_VERSION=1.0.0
TIME_ZONE=Asia/Aden
UPLOAD_FOLDER=uploads
STATIC_DIR=static
```

### Settings Configuration

```python
from core.config import settings

# Access settings
print(settings.DATABASE_URI)
print(settings.SECRET_KEY)
print(settings.PROJECT_NAME)
```

### Custom Settings

```python
from pydantic_settings import BaseSettings
from core.env_manager import EnvManager

class CustomSettings(BaseSettings):
    CUSTOM_VALUE: str = EnvManager.get("CUSTOM_VALUE", "default")
    
    # Add your custom settings
    MAX_UPLOAD_SIZE: int = int(EnvManager.get("MAX_UPLOAD_SIZE", "10485760"))
```

## Troubleshooting

### Import Errors

**Problem**: `ImportError: cannot import name 'X' from 'src.core'`

**Solution**: The library uses `core` as the package name, not `src.core`. Update imports:

```python
# ❌ Wrong
from src.core.database import BaseModel

# ✅ Correct
from core.database import BaseModel
```

If you're seeing `src.core` imports in the library code itself, this is a known issue. Fix by:

1. Update all imports in the `core/` directory from `src.core` to just `core`
2. Or set up your project structure to include the `src` directory in your Python path

### Database Connection Issues

**Problem**: Database connection fails

**Solution**:
```python
# For SQLite
DATABASE_URL=sqlite:///./database.db
ASYNC_DATABASE_URL=sqlite+aiosqlite:///./database.db

# For PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/dbname
ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# For MySQL
DATABASE_URL=mysql://user:password@localhost/dbname
ASYNC_DATABASE_URL=mysql+aiomysql://user:password@localhost/dbname
```

### Soft Delete Not Working

**Problem**: Deleted items still appear in queries

**Solution**: Ensure you're using the async session correctly:

```python
from core.database import get_session

async with get_session() as session:
    # Queries here will automatically filter deleted items
    result = await session.exec(select(MyModel))
```

### Permission Issues

**Problem**: Routes require authentication but you want to disable it

**Solution**:
```python
class MyRouter(BaseRouter):
    _need_auth = False  # Disable authentication for all routes
    
    def __init__(self):
        super().__init__(resource_name="myresource")
    
    # Or disable for specific route
    @add_route("/public", "GET", PermissionAction.READ, need_auth=False)
    async def public_endpoint(self):
        return {"message": "Public endpoint"}
```

### Router Not Found

**Problem**: `AttributeError: 'NoneType' object has no attribute 'get_router'`

**Solution**: Ensure you're calling `get_router()` after router initialization:

```python
router_instance = MyRouter()
router = router_instance.get_router()  # Don't forget this step
app.include_router(router)
```

## Best Practices

### 1. Always Use Async/Await

```python
# ✅ Correct
async def get_products():
    products = await repository.get_all()
    return products

# ❌ Wrong - Don't use sync code
def get_products():
    products = repository.get_all()  # This will not work
    return products
```

### 2. Use Type Hints

```python
from typing import List, Optional

# ✅ Good
async def get_products() -> List[Product]:
    return await repository.get_all()

# ❌ Not recommended
async def get_products():
    return await repository.get_all()
```

### 3. Validate in Service Layer

```python
class ProductService(BaseService):
    async def _validate_create(self, create_data: dict):
        # Validate business rules here
        if create_data.get('price') < 0:
            raise ValidationException("Price cannot be negative")
```

### 4. Keep Repositories Simple

```python
# ✅ Good - Simple data access
class ProductRepository(BaseRepository):
    async def get_by_category(self, category: str):
        return await self.get_all(category=category)

# ❌ Bad - Business logic in repository
class ProductRepository(BaseRepository):
    async def create_with_validation(self, data):
        if data['price'] < 0:  # This belongs in service
            raise Exception("Invalid price")
        return await self.create(data)
```

### 5. Use Proper Exception Handling

```python
from core.exceptions import (
    NotFoundException,
    ValidationException,
    ServiceException
)

try:
    product = await service.get_by_id(id)
except NotFoundException:
    # Handle not found
    pass
except ValidationException:
    # Handle validation error
    pass
except ServiceException:
    # Handle service error
    pass
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Support

For issues and questions:
- GitHub Issues: https://github.com/GhaziRiyadh/root-core/issues
- Email: ghazriyadh2@gmail.com
