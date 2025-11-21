# Architecture Guide - Root Core Python Library

## Overview

Root Core follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│           FastAPI Application           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Router Layer (API)              │
│  - Handle HTTP requests/responses       │
│  - Route registration                   │
│  - Request validation                   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Service Layer (Business)        │
│  - Business logic                       │
│  - Validation rules                     │
│  - Orchestration                        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       Repository Layer (Data)           │
│  - Data access                          │
│  - Query construction                   │
│  - ORM operations                       │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Database (SQLModel)             │
│  - Entity models                        │
│  - Relationships                        │
│  - Migrations                           │
└─────────────────────────────────────────┘
```

## Layers Explained

### 1. Router Layer

**Responsibility**: Handle HTTP requests and responses

**Key Features**:
- Automatic CRUD endpoint generation
- Route registration with FastAPI
- Request/response serialization
- Authentication/authorization integration
- Custom endpoint support

**Base Class**: `BaseRouter`

```python
from core.bases.base_router import BaseRouter

class ProductRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            resource_name="products",
            prefix="/api/products",
            tags=["Products"]
        )
```

**Generated Endpoints**:
- `GET /api/products` - List with pagination
- `GET /api/products/{id}` - Get by ID
- `POST /api/products` - Create
- `PUT /api/products/{id}` - Update
- `DELETE /api/products/{id}` - Soft delete
- `POST /api/products/{id}/restore` - Restore
- `DELETE /api/products/{id}/force` - Force delete

### 2. Service Layer

**Responsibility**: Business logic and validation

**Key Features**:
- CRUD operations orchestration
- Business rule validation
- Data transformation
- Exception handling
- Standardized responses

**Base Class**: `BaseService`

```python
from core.bases.base_service import BaseService

class ProductService(BaseService):
    def __init__(self, repository):
        super().__init__(repository)
    
    async def _validate_create(self, create_data: dict):
        # Business validation logic
        if create_data.get('price') < 0:
            raise ValidationException("Price cannot be negative")
```

**Key Methods**:
- `get_all()` - Retrieve all items
- `get_by_id()` - Get single item
- `get_list()` - Paginated list
- `create()` - Create with validation
- `update()` - Update with validation
- `soft_delete()` - Soft delete
- `restore()` - Restore deleted
- `force_delete()` - Permanent delete

### 3. Repository Layer

**Responsibility**: Data access and persistence

**Key Features**:
- Database queries
- CRUD operations
- Filtering and searching
- Pagination
- Bulk operations

**Base Class**: `BaseRepository`

```python
from core.bases.base_repository import BaseRepository

class ProductRepository(BaseRepository):
    def __init__(self):
        super().__init__(Product)
    
    async def get_by_category(self, category: str):
        return await self.get_all(category=category)
```

**Key Methods**:
- `get()` - Get by ID
- `get_one()` - Get single by filter
- `get_all()` - Get all items
- `list()` - Paginated query
- `create()` - Insert record
- `update()` - Update record
- `delete()` - Remove record

### 4. Model Layer

**Responsibility**: Data structure and relationships

**Key Features**:
- Entity definitions
- Field validation
- Relationships
- Soft delete support

**Base Class**: `BaseModel`

```python
from core.database import BaseModel
from sqlmodel import Field, Relationship

class Product(BaseModel, table=True):
    __tablename__ = "products"
    
    name: str = Field(max_length=200)
    price: float = Field(ge=0)
    category_id: int = Field(foreign_key="categories.id")
    
    # Relationship
    category: "Category" = Relationship(back_populates="products")
```

## Design Patterns

### 1. Repository Pattern

Separates data access logic from business logic:

```python
# Repository handles data access
class ProductRepository(BaseRepository):
    async def get_expensive_products(self, min_price: float):
        query = select(Product).where(Product.price >= min_price)
        return await self._execute_query(query)

# Service uses repository
class ProductService(BaseService):
    async def get_premium_products(self):
        return await self.repository.get_expensive_products(100.0)
```

### 2. Service Pattern

Encapsulates business logic:

```python
class ProductService(BaseService):
    async def apply_discount(self, product_id: int, discount_percent: float):
        # Get product
        product = await self.get_by_id(product_id)
        
        # Business logic
        if discount_percent > 50:
            raise ValidationException("Discount cannot exceed 50%")
        
        new_price = product['data'].price * (1 - discount_percent / 100)
        
        # Update through repository
        return await self.update(product_id, {"price": new_price})
```

### 3. Singleton Pattern

Base classes use singleton pattern to ensure single instance:

```python
class BaseRouter:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 4. Decorator Pattern

Routes are registered using decorators:

```python
from core.router import add_route
from core.config import PermissionAction

@add_route("/custom", "GET", PermissionAction.READ)
async def custom_endpoint(self):
    return {"message": "Custom endpoint"}
```

## Data Flow

### Create Operation Flow

```
1. Client Request
   POST /api/products
   {
     "name": "New Product",
     "price": 29.99
   }
   ↓
2. Router Layer
   - Validate request schema
   - Extract data
   ↓
3. Service Layer
   - Call _validate_create()
   - Check business rules
   ↓
4. Repository Layer
   - Create database record
   - Return created entity
   ↓
5. Service Layer
   - Transform data with _return_one_data()
   - Build response
   ↓
6. Router Layer
   - Return HTTP 201 Created
   {
     "data": {...},
     "message": "Item created successfully"
   }
```

### Query Operation Flow

```
1. Client Request
   GET /api/products?page=1&per_page=10
   ↓
2. Router Layer
   - Extract query parameters
   ↓
3. Service Layer
   - Validate pagination params
   ↓
4. Repository Layer
   - Build query with filters
   - Apply soft-delete filter
   - Execute query
   - Count total records
   ↓
5. Service Layer
   - Transform data with _return_multi_data()
   - Build paginated response
   ↓
6. Router Layer
   - Return HTTP 200 OK
   {
     "items": [...],
     "total": 100,
     "page": 1,
     "per_page": 10,
     "pages": 10
   }
```

## Soft Delete Implementation

### How It Works

1. **Database Level**:
   - `is_deleted` boolean field on `BaseModel`
   - Default value: `False`

2. **Query Level**:
   - Global filter applied automatically
   - Excludes records where `is_deleted = True`

3. **Service Level**:
   - `soft_delete()` - Sets `is_deleted = True`
   - `restore()` - Sets `is_deleted = False`
   - `force_delete()` - Actually removes record

### Implementation Details

```python
# In BaseModel
class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_deleted: bool = Field(default=False)

# In database.py - Global filter
@event.listens_for(Session, "do_orm_execute")
def _apply_soft_delete_filter(execute_state):
    if execute_state.is_select and not execute_state.execution_options.get("include_deleted", False):
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(BaseModel, exclude_deleted_records, include_aliases=True)
        )

def exclude_deleted_records(cls):
    if hasattr(cls, "is_deleted"):
        return cls.is_deleted == False
    return True
```

### Usage

```python
# Soft delete
await service.soft_delete(item_id=1)
# SQL: UPDATE products SET is_deleted = TRUE WHERE id = 1

# Query (automatically filtered)
products = await service.get_all()
# SQL: SELECT * FROM products WHERE is_deleted = FALSE

# Query including deleted
products = await service.get_all(include_deleted=True)
# SQL: SELECT * FROM products

# Restore
await service.restore(item_id=1)
# SQL: UPDATE products SET is_deleted = FALSE WHERE id = 1

# Force delete
await service.force_delete(item_id=1)
# SQL: DELETE FROM products WHERE id = 1
```

## Authentication & Authorization

### Permission System

```python
from core.config import PermissionAction

class PermissionAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    FORCE_DELETE = "force_delete"
    RESTORE = "restore"
    LOGS = "logs"
    MANAGE = "management"
    COPY = "copy"
    EXPORT = "export"
```

### Route Protection

```python
from core.router import add_route
from core.config import PermissionAction

class ProductRouter(BaseRouter):
    _need_auth = True  # Require authentication for all routes
    
    @add_route("/public", "GET", PermissionAction.READ, need_auth=False)
    async def public_endpoint(self):
        """Public endpoint - no auth required"""
        return {"message": "Public data"}
    
    @add_route("/admin", "POST", PermissionAction.MANAGE)
    async def admin_endpoint(self):
        """Admin only endpoint"""
        return {"message": "Admin data"}
```

### Middleware Integration

```python
from core.bases.base_middleware import BaseMiddleware

class LoggingMiddleware(BaseMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request
        print(f"Request: {request.method} {request.url}")
        
        response = await call_next(request)
        
        # Log response
        print(f"Response: {response.status_code}")
        
        return response

class ProductRouter(BaseRouter):
    _middlewares = [LoggingMiddleware()]
    
    def __init__(self):
        super().__init__(resource_name="products")
```

## Error Handling

### Exception Hierarchy

```python
from core.exceptions import (
    RootCoreException,      # Base exception
    NotFoundException,       # Item not found
    ValidationException,     # Validation failed
    ServiceException,        # Service error
    OperationException       # Operation failed
)
```

### Usage in Services

```python
from core.exceptions import ValidationException, NotFoundException

class ProductService(BaseService):
    async def _validate_create(self, create_data: dict):
        if not create_data.get('name'):
            raise ValidationException("Product name is required")
        
        if create_data.get('price', 0) < 0:
            raise ValidationException("Price cannot be negative")
    
    async def update_stock(self, product_id: int, quantity: int):
        product = await self.repository.get(product_id)
        if not product:
            raise NotFoundException(f"Product {product_id} not found")
        
        new_stock = product.stock + quantity
        if new_stock < 0:
            raise ValidationException("Insufficient stock")
        
        return await self.update(product_id, {"stock": new_stock})
```

### Response Handler

```python
from core.response.handlers import handle_exceptions

@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "success": False}
    )

@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "success": False}
    )
```

## Best Practices

### 1. Layer Separation

```python
# ✅ Good - Clear separation
class ProductRepository(BaseRepository):
    async def get_by_sku(self, sku: str):
        return await self.get_one(sku=sku)

class ProductService(BaseService):
    async def _validate_create(self, create_data: dict):
        if create_data.get('price') < 0:
            raise ValidationException("Invalid price")

# ❌ Bad - Business logic in repository
class ProductRepository(BaseRepository):
    async def create_with_discount(self, data: dict):
        if data['price'] < 0:  # Validation in wrong layer
            raise Exception("Invalid price")
        data['price'] *= 0.9  # Business logic in wrong layer
        return await self.create(data)
```

### 2. Async/Await Consistency

```python
# ✅ Good - All async
async def get_products():
    products = await repository.get_all()
    return await service._return_multi_data(products)

# ❌ Bad - Mixing sync/async
async def get_products():
    products = repository.get_all()  # Missing await
    return service._return_multi_data(products)  # Missing await
```

### 3. Type Hints

```python
# ✅ Good - Proper typing
from typing import List, Dict, Any, Optional

async def get_products(
    page: int = 1,
    per_page: int = 10
) -> Dict[str, Any]:
    return await service.get_list(page, per_page)

# ❌ Bad - No type hints
async def get_products(page=1, per_page=10):
    return await service.get_list(page, per_page)
```

### 4. Error Handling

```python
# ✅ Good - Specific exceptions
try:
    product = await service.get_by_id(id)
except NotFoundException as e:
    return {"error": "Product not found"}
except ValidationException as e:
    return {"error": f"Validation failed: {e}"}

# ❌ Bad - Generic exception
try:
    product = await service.get_by_id(id)
except Exception as e:
    return {"error": "Something went wrong"}
```

## Performance Considerations

### 1. Database Queries

```python
# ✅ Good - Single query with relationships
products = await session.exec(
    select(Product)
    .options(selectinload(Product.category))
    .where(Product.is_deleted == False)
)

# ❌ Bad - N+1 query problem
products = await repository.get_all()
for product in products:
    category = await repository.get_category(product.category_id)
```

### 2. Pagination

```python
# ✅ Good - Always use pagination for lists
products = await service.get_list(page=1, per_page=20)

# ❌ Bad - Loading all records
products = await service.get_all()  # Could be millions of records
```

### 3. Bulk Operations

```python
# ✅ Good - Bulk insert
await service.bulk_create([
    {"name": "Product 1", "price": 10},
    {"name": "Product 2", "price": 20},
    {"name": "Product 3", "price": 30}
])

# ❌ Bad - Multiple individual inserts
for data in product_list:
    await service.create(data)
```

## Testing

### Unit Testing Services

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_create_product():
    # Mock repository
    repository = AsyncMock()
    repository.create = AsyncMock(return_value=Product(id=1, name="Test", price=10))
    
    # Create service
    service = ProductService(repository)
    
    # Test
    result = await service.create({"name": "Test", "price": 10})
    
    # Assert
    assert result['data'].id == 1
    assert result['message'] == "Item created successfully"
    repository.create.assert_called_once()
```

### Integration Testing Routes

```python
from fastapi.testclient import TestClient

def test_get_products():
    client = TestClient(app)
    response = client.get("/api/products")
    
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()

def test_create_product():
    client = TestClient(app)
    response = client.post(
        "/api/products",
        json={"name": "Test Product", "price": 29.99}
    )
    
    assert response.status_code == 201
    assert response.json()['data']['name'] == "Test Product"
```

## Summary

The Root Core architecture provides:
- ✅ Clear separation of concerns
- ✅ Reusable base classes
- ✅ Automatic CRUD generation
- ✅ Soft delete support
- ✅ Built-in pagination
- ✅ Exception handling
- ✅ Authentication/authorization
- ✅ Type safety
- ✅ Async/await support
- ✅ Testable design

This architecture enables rapid development while maintaining code quality and maintainability.
