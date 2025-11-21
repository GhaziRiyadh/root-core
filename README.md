# ROOT CORE

A comprehensive library providing base classes and patterns for building web applications with CRUD operations, available in both **Python (FastAPI)** and **ASP.NET Core**.

## Overview

ROOT CORE provides a solid foundation for building web applications with:
- Base Repository, Service, and Controller/Router patterns
- Database models with soft-delete support
- Standardized API responses and error handling
- Full CRUD operations with pagination
- Authentication and authorization support

## Available Implementations

### Python FastAPI Version
Located in the `/core` directory. This is a Python library built on FastAPI and SQLModel/SQLAlchemy.

**Key Features:**
- FastAPI routers with automatic CRUD endpoints
- SQLModel/SQLAlchemy for database operations
- Async/await support throughout
- JWT authentication
- Dynamic field parsing and form generation

**Requirements:**
- Python 3.13+
- FastAPI
- SQLModel
- SQLAlchemy

[See Python Documentation](./core/)

### ASP.NET Core Version
Located in the `/RootCore` directory. This is a C# class library built on ASP.NET Core and Entity Framework Core.

**Key Features:**
- ASP.NET Core controllers with CRUD endpoints
- Entity Framework Core for database operations
- Async/await support throughout
- JWT authentication support
- Strongly-typed models and services

**Requirements:**
- .NET 8.0 or later
- Entity Framework Core
- Microsoft.AspNetCore.Mvc.Core
- Microsoft.AspNetCore.Authentication.JwtBearer

[See ASP.NET Documentation](./RootCore/README.md)

## Comparison

| Feature | Python (FastAPI) | ASP.NET Core |
|---------|------------------|--------------|
| Language | Python 3.13+ | C# / .NET 8.0+ |
| Database ORM | SQLModel/SQLAlchemy | Entity Framework Core |
| Web Framework | FastAPI | ASP.NET Core |
| Type Safety | Optional (with type hints) | Strong typing |
| Async Support | ✓ | ✓ |
| Soft Delete | ✓ | ✓ |
| Pagination | ✓ | ✓ |
| JWT Auth | ✓ | ✓ |
| DI Support | Manual/FastAPI Depends | Built-in |

## Quick Start

### Python Version

```python
from core.bases.base_router import BaseRouter
from core.bases.base_service import BaseService
from core.bases.base_repository import BaseRepository
from core.database import BaseModel

# Define your model
class Product(BaseModel, table=True):
    name: str
    price: float

# Use base classes for CRUD operations
repository = BaseRepository(Product)
service = BaseService(repository)
router = BaseRouter("products", create_schema=Product, response_schema=Product)
```

### ASP.NET Core Version

```csharp
using RootCore.Bases;
using RootCore.Database;

// Define your model
public class Product : BaseModel
{
    public string Name { get; set; }
    public decimal Price { get; set; }
}

// Use base classes for CRUD operations
public class ProductRepository : BaseRepository<Product> { }
public class ProductService : BaseService<Product> { }
public class ProductsController : BaseController<Product> { }
```

## Architecture

Both implementations follow the same architectural patterns:

```
┌─────────────────┐
│   Controller    │  ← HTTP endpoints, request/response handling
│    (Router)     │
└────────┬────────┘
         │
┌────────▼────────┐
│    Service      │  ← Business logic, validation
└────────┬────────┘
         │
┌────────▼────────┐
│   Repository    │  ← Data access, queries
└────────┬────────┘
         │
┌────────▼────────┐
│    Database     │  ← Entity models, DbContext/Session
└─────────────────┘
```

## Common Features

### Soft Delete
Both implementations support soft deletion where records are marked as deleted rather than being physically removed from the database.

### Pagination
Built-in pagination support with consistent response format:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "perPage": 10,
  "pages": 10,
  "message": "Success"
}
```

### Standardized Responses
All API endpoints return consistent response structures for both success and error cases.

### Authentication
JWT-based authentication support in both implementations with similar configuration patterns.

## Contributing

Contributions are welcome for both Python and ASP.NET Core versions! Please ensure:
- Code follows the existing patterns and conventions
- Tests are included for new features
- Documentation is updated as needed

## License

This project is provided as-is for use in your applications.

## Author

Ghazi Riyadh (ghazriyadh2@gmail.com)