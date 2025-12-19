# AI Coding Standards & Project Guide

This document serves as a guide for AI agents and developers working on this codebase. It outlines the project structure, architectural patterns, and standard practices for implementing features.

## 1. Project Overview

 This project is a **Python/FastAPI** application using **SQLModel** (SQLAlchemy + Pydantic) for ORM and schema validation. It follows a layered architecture (Service-Repository pattern).

### Core Technologies

- **Framework**: FastAPI
- **Database**: PostgreSQL (Async) via SQLModel/SQLAlchemy
- **Migration**: Alembic
- **Package Manager**: Poetry

## 2. Directory Structure

```
root/
├── core/               # Framework core (Do not modify unless necessary)
│   ├── bases/          # Base classes (BaseRepository, BaseService, CRUDApi)
│   ├── response/       # Custom response handlers
│   └── ...
├── apps/               # Business Logic - CREATE APPS HERE
│   ├── <app_name>/
│   │   ├── commands/   # CLI commands
│   │   ├── models/     # Database models (SQLModel)
│   │   ├── schemas/    # Pydantic schemas (Create/Update)
│   │   ├── repository/ # Data access layer
│   │   ├── services/   # Business logic layer
│   │   ├── routes.py   # API definitions
│   │   └── ...
├── docs/               # Documentation
└── ...
```

## 3. Implementing a New Feature (CRUD)

To add a new resource (e.g., `Product`), follow these steps in order:

### Step 1: Define the Model (`models/product.py`)

Inherit from `core.database.BaseModel`.

```python
from sqlmodel import Field
from core.database import BaseModel

class Product(BaseModel, table=True):
    __tablename__ = "products"
    
    name: str = Field(index=True)
    price: float
    description: str | None = None
```

### Step 2: Define Schemas (`schemas/product.py`)

Define Create, Update, and Response schemas.

```python
from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    price: float
    description: str | None = None

class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    description: str | None = None
```

### Step 3: Create Repository (`repository/product_repo.py`)

Inherit from `core.bases.base_repository.BaseRepository`.

```python
from core.bases.base_repository import BaseRepository
from ..models.product import Product

class ProductRepository(BaseRepository[Product]):
    model = Product
    _search_fields = ["name", "description"] # Fields enabled for ?query=... search
```

### Step 4: Create Service (`services/product_service.py`)

Inherit from `core.bases.base_service.BaseService`.

```python
from core.bases.base_service import BaseService
from ..repository.product_repo import ProductRepository

class ProductService(BaseService[Product]):
    def __init__(self, repository: ProductRepository):
        super().__init__(repository)
        # Optional: Set serializer class to automatically format responses
        # self.serializer_class = ProductSerializer
        # Optional: Set serializer class to automatically format responses
        # self.serializer_class = ProductSerializer
```

### Step 5: Define Router (`routes.py`)

Use `core.bases.crud_api.CRUDApi` for instant CRUD endpoints.

```python
from fastapi import APIRouter
from core.bases.crud_api import CRUDApi
from .services.product_service import ProductService
from .schemas.product import ProductCreate, ProductUpdate
from .repository.product_repo import ProductRepository
from core.database import get_session

# Dependency Injection setup
def get_product_service(session=Depends(get_session)):
    repo = ProductRepository(get_session=lambda: session)
    return ProductService(repo)

# Initialize generic CRUD
router = CRUDApi(
    service=get_product_service(), # Note: In actual implementation, manage DIs properly
    resource_name="products",
    create_schema=ProductCreate,
    update_schema=ProductUpdate,
    tags=["Products"]
)

# Add custom routes using @router.add_route if needed
```

*Note: Ensure dependencies are correctly injected. The `CRUDApi` usually expects an instantiated service or acts as a class that FastAP I delegates to.*

## 4. Standard Response Formats

**ALWAYS** use the helper functions in `core.response.handlers` to return data. Do not return raw dicts or objects directly from endpoints.

### Success Response

```python
from core.response.handlers import success_response

return success_response(
    data={"id": 1, "name": "Item"}, 
    message="Created successfully",
    status_code=201
)
```

Output:

```json
{
  "success": true,
  "message": "Created successfully",
  "data": { ... }
}
```

### Error Response

Use exceptions from `core.exceptions` which are automatically caught, OR return explicitly:

```python
from core.response.handlers import error_response

return error_response(
    error_code="INVALID_INPUT",
    message="Price must be positive",
    status_code=400
)
```

### Paginated Response

Used automatically by `BaseService.get_list`, but if you need it manually:

```python
from core.response.handlers import paginated_response

return paginated_response(
    items=items_list,
    total=100,
    page=1,
    per_page=10,
    pages=10
)
```

## 5. Custom Commands

To create CLI commands, create a file in `apps/<your_app>/commands/`.

```python
from core.bases.base_command import BaseCommand

class SyncProductsCommand(BaseCommand):
    def execute(self, force: bool = False):
        """Syncs products from external source."""
        print(f"Syncing products... Force={force}")
```

This is actionable via `python cli.py sync-products`.

## 6. Key Conventions

- **Soft Deletes**: All models inheriting `BaseModel` have soft-delete (`is_deleted`) enabled by default. `BaseRepository` handles filtering automatically.
- **Logging**: `BaseRepository` automatically logs CREATE, UPDATE, DELETE actions if a `Log` model is configured.
- **Async**: Use `async/await` for all DB operations.
- **Type Hinting**: Use strict type hints for Pydantic models and function signatures.

## 7. Serializers (DRF Style)

For complex response formatting, use the `BaseSerializer` pattern (inspired by Django REST Framework) instead of raw Pydantic schemas or custom return functions. This allows for dynamic fields and context-aware serialization.

### Example Usage

```python
# core/apps/auth/serializers.py
from core.bases.serializer import BaseSerializer, SerializerMethodField
from core.apps.auth.models.user import User

class UserSerializer(BaseSerializer):
    class Meta:
        model = User
        
    full_name = SerializerMethodField()

    def get_full_name(self, obj) -> str:
        return f"{obj.first_name} {obj.last_name}"

# In your Service/Route:
user = await repo.get(1)
serializer = UserSerializer(user)
return success_response(data=serializer.data)
```

**Features:**

- `Meta.model`: Automatically includes model fields.
- `SerializerMethodField`: Define `get_<field_name>` to compute values.
- `many=True`: Handle lists easily (`UserSerializer(users, many=True)`).
- `context`: Pass extra data (`UserSerializer(user, context={'request': request})`).
- **Service Integration**: Set `self.serializer_class` in your Service to automatically format all return values.

### Write Operations (Create/Update)

The serializer also handles input validation and saving.

```python
# 1. Validation Logic
class UserSerializer(BaseSerializer):
    class Meta:
        model = User
        
    def create(self, validated_data):
        # Override for custom logic
        validated_data['username'] = validated_data['email'].split('@')[0]
        # Must call repo if you override
        return await self.instance.service.repository.create(validated_data) # or similar

# 2. Service Usage
# By just setting serializer_class = UserSerializer, create/update now use it:
# await service.create({"email": "foo@bar.com"}) 
# -> Validates using Pydantic model
# -> Calls serializer.save() -> serializer.create()
```
