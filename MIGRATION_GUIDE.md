# Migration Guide: Python FastAPI to ASP.NET Core

This guide helps you migrate from the Python FastAPI version of root-core to the ASP.NET Core version.

## Overview

Both versions provide the same core functionality with framework-appropriate implementations:
- Base classes for Repository, Service, and Controller/Router patterns
- Soft-delete support at the database level
- Standardized API responses
- CRUD operations with pagination
- JWT authentication support

## Key Differences

### Language & Runtime
- **Python**: Dynamic typing with optional type hints, interpreted
- **C#**: Strong static typing, compiled

### Database ORM
- **Python**: SQLModel/SQLAlchemy with async support
- **C#**: Entity Framework Core with async support

### Dependency Injection
- **Python**: Manual or using FastAPI's `Depends()`
- **C#**: Built-in ASP.NET Core DI container

### Configuration
- **Python**: Environment variables or Python settings classes
- **C#**: appsettings.json with strongly-typed configuration

## Code Comparison

### 1. Defining Models

#### Python (SQLModel)
```python
from sqlmodel import Field, SQLModel
from core.database import BaseModel

class Product(BaseModel, table=True):
    name: str
    price: float = Field(ge=0)
    description: str | None = None
```

#### C# (Entity Framework Core)
```csharp
using RootCore.Database;

public class Product : BaseModel
{
    public string Name { get; set; } = string.Empty;
    public decimal Price { get; set; }
    public string? Description { get; set; }
}
```

### 2. Database Context

#### Python (SQLAlchemy)
```python
from sqlmodel.ext.asyncio.session import AsyncSession
from core.database import engine

async with AsyncSession(engine) as session:
    # Use session
```

#### C# (Entity Framework Core)
```csharp
using Microsoft.EntityFrameworkCore;
using RootCore.Database;

public class ApplicationDbContext : BaseDbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) 
        : base(options)
    {
    }
    
    public DbSet<Product> Products { get; set; }
}
```

### 3. Repository

#### Python
```python
from core.bases.base_repository import BaseRepository

class ProductRepository(BaseRepository):
    def __init__(self):
        super().__init__(Product)
```

#### C#
```csharp
using RootCore.Bases;

public class ProductRepository : BaseRepository<Product>
{
    public ProductRepository(ApplicationDbContext context) 
        : base(context)
    {
    }
}
```

### 4. Service

#### Python
```python
from core.bases.base_service import BaseService
from core.exceptions import ValidationException

class ProductService(BaseService):
    def __init__(self, repository: ProductRepository):
        super().__init__(repository)
    
    async def _validate_create(self, create_data: dict) -> None:
        if create_data.get('price', 0) < 0:
            raise ValidationException("Price cannot be negative")
```

#### C#
```csharp
using RootCore.Bases;
using RootCore.Exceptions;

public class ProductService : BaseService<Product>
{
    public ProductService(BaseRepository<Product> repository) 
        : base(repository)
    {
    }
    
    protected override Task ValidateCreateAsync(Product entity)
    {
        if (entity.Price < 0)
        {
            throw new ValidationException("Price cannot be negative");
        }
        return Task.CompletedTask;
    }
}
```

### 5. Router/Controller

#### Python (FastAPI)
```python
from fastapi import APIRouter, Depends
from core.bases.base_router import BaseRouter
from core.router import add_route
from core.config import PermissionAction

class ProductRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            resource_name="products",
            prefix="/api/products",
            tags=["Products"]
        )
    
    @add_route("/custom", "GET", PermissionAction.READ)
    async def custom_endpoint(self):
        return {"message": "Custom endpoint"}

router = ProductRouter().get_router()
```

#### C# (ASP.NET Core)
```csharp
using Microsoft.AspNetCore.Mvc;
using RootCore.Bases;

[ApiController]
[Route("api/[controller]")]
public class ProductsController : BaseController<Product>
{
    public ProductsController(BaseService<Product> service) 
        : base(service)
    {
    }
    
    [HttpGet("custom")]
    public async Task<ActionResult> CustomEndpoint()
    {
        return Ok(new { message = "Custom endpoint" });
    }
}
```

### 6. Application Setup

#### Python (main.py)
```python
from fastapi import FastAPI
from core.database import engine, BaseModel

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

app.include_router(router)
```

#### C# (Program.cs)
```csharp
var builder = WebApplication.CreateBuilder(args);

// Add DbContext
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection")));

// Register services
builder.Services.AddScoped<BaseRepository<Product>>();
builder.Services.AddScoped<BaseService<Product>>();
builder.Services.AddControllers();

var app = builder.Build();

// Ensure database is created
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    context.Database.EnsureCreated();
}

app.MapControllers();
app.Run();
```

### 7. Configuration

#### Python (.env or settings.py)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URI: str = "sqlite:///database.db"
    SECRET_KEY: str = "supersecretkey"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
```

#### C# (appsettings.json)
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Data Source=database.db"
  },
  "AppSettings": {
    "SecretKey": "supersecretkey",
    "AccessTokenExpireMinutes": 30
  }
}
```

```csharp
// In Program.cs
builder.Services.Configure<AppSettings>(
    builder.Configuration.GetSection("AppSettings"));
```

## Migration Steps

### Step 1: Set Up .NET Project

1. Install .NET SDK (10.0 or compatible)
2. Create a new ASP.NET Core project:
   ```bash
   dotnet new webapi -n YourProject
   ```
3. Add RootCore reference:
   ```bash
   dotnet add reference path/to/RootCore/RootCore.csproj
   ```

### Step 2: Migrate Models

Convert each Python model to a C# class:
- Inherit from `BaseModel`
- Convert type annotations to C# property types
- Add default values or make properties nullable as needed

### Step 3: Create DbContext

Create a class inheriting from `BaseDbContext`:
- Add `DbSet<T>` properties for each entity
- Override `OnModelCreating` if custom configuration is needed

### Step 4: Migrate Repositories (Optional)

If you have custom repositories:
- Inherit from `BaseRepository<T>`
- Convert async methods (Python's `async def` → C#'s `async Task`)
- Update query syntax to LINQ

### Step 5: Migrate Services (Optional)

If you have custom services:
- Inherit from `BaseService<T>`
- Override validation methods as needed
- Convert async methods to C# async/await pattern

### Step 6: Migrate Routes to Controllers

Convert FastAPI routers to ASP.NET Core controllers:
- Inherit from `BaseController<T>`
- Use attributes like `[HttpGet]`, `[HttpPost]` instead of decorators
- Convert route parameters and query strings

### Step 7: Update Configuration

1. Create `appsettings.json`
2. Configure services in `Program.cs`
3. Set up database connection
4. Register dependencies

### Step 8: Test

Build and run your application:
```bash
dotnet build
dotnet run
```

## Common Patterns

### Async/Await

#### Python
```python
async def get_product(product_id: int) -> Product:
    product = await repository.get(product_id)
    return product
```

#### C#
```csharp
public async Task<Product> GetProductAsync(int productId)
{
    var product = await _repository.GetByIdAsync(productId);
    return product;
}
```

### Exception Handling

#### Python
```python
try:
    product = await service.get_by_id(id)
except NotFoundException as e:
    raise HTTPException(status_code=404, detail=str(e))
```

#### C#
```csharp
try
{
    var product = await _service.GetByIdAsync(id);
}
catch (NotFoundException ex)
{
    return NotFound(new ErrorResponse(ex.Message));
}
```

### Response Formatting

Both versions use similar response structures:

#### Python
```python
return {
    "data": product,
    "message": "Product retrieved successfully"
}
```

#### C#
```csharp
return new ApiResponse<Product>(
    product,
    "Product retrieved successfully"
);
```

## API Endpoint Mapping

All CRUD endpoints remain the same:

| Method | Python Endpoint | C# Endpoint | Notes |
|--------|----------------|-------------|-------|
| GET | `/api/products` | `/api/products` | Paginated list |
| GET | `/api/products/all` | `/api/products/all` | All items |
| GET | `/api/products/{id}` | `/api/products/{id}` | Get by ID |
| POST | `/api/products` | `/api/products` | Create |
| PUT | `/api/products/{id}` | `/api/products/{id}` | Update |
| DELETE | `/api/products/{id}` | `/api/products/{id}` | Soft delete |
| POST | `/api/products/{id}/restore` | `/api/products/{id}/restore` | Restore |
| DELETE | `/api/products/{id}/force` | `/api/products/{id}/force` | Force delete |
| GET | `/api/products/{id}/exists` | `/api/products/{id}/exists` | Check exists |
| GET | `/api/products/count` | `/api/products/count` | Count |
| POST | `/api/products/bulk` | `/api/products/bulk` | Bulk create |
| POST | `/api/products/bulk-delete` | `/api/products/bulk-delete` | Bulk delete |

## Performance Considerations

### Python FastAPI
- Asynchronous by default
- Good for I/O-bound operations
- Interpreted, may have overhead

### C# ASP.NET Core
- Asynchronous with async/await
- Excellent for CPU and I/O-bound operations
- Compiled, generally faster execution
- Better memory management with value types

## Tips for Migration

1. **Start with Models**: Migrate your data models first
2. **Use Type Safety**: Leverage C#'s strong typing for better compile-time checks
3. **Leverage DI**: Use ASP.NET Core's built-in dependency injection
4. **Test Incrementally**: Migrate and test one controller at a time
5. **Keep API Contract**: Maintain the same endpoint structure for easy client migration
6. **Use Async**: Always use async/await for database operations
7. **Error Handling**: Implement similar exception handling patterns

## Need Help?

- Check the RootCore documentation: `/RootCore/README.md`
- Review the sample project: `/SampleWebApi/`
- Compare Python and C# implementations side by side

## Summary

The ASP.NET Core version maintains feature parity with the Python version while providing:
- Strong typing and compile-time safety
- Better performance for most scenarios
- Integrated dependency injection
- Rich ecosystem of .NET libraries
- Enterprise-ready scalability

Both versions share the same architectural patterns, making migration straightforward once you understand the language and framework differences.
