# RootCore - ASP.NET Core Library

This is an ASP.NET Core class library that provides base classes and patterns for building web applications with CRUD operations, soft-delete support, and standardized responses.

## Overview

RootCore is converted from a Python FastAPI library to ASP.NET Core, providing similar functionality with the following key features:

- **Base Classes**: Repository, Service, and Controller patterns
- **Entity Framework Core**: Database access with soft-delete support
- **Standardized Responses**: Consistent API responses and error handling
- **CRUD Operations**: Full Create, Read, Update, Delete operations
- **Soft Delete**: Logical deletion with restore capability
- **Pagination**: Built-in pagination support
- **JWT Authentication**: Token-based authentication support

## Installation

Add the RootCore library to your ASP.NET Core project:

```bash
dotnet add reference path/to/RootCore/RootCore.csproj
```

## Project Structure

```
RootCore/
├── Bases/
│   ├── BaseController.cs      - Base API controller with CRUD endpoints
│   ├── BaseRepository.cs      - Base repository with data access
│   └── BaseService.cs         - Base service with business logic
├── Configuration/
│   └── AppSettings.cs         - Application configuration
├── Database/
│   ├── BaseModel.cs           - Base entity model
│   └── BaseDbContext.cs       - Base database context
├── Exceptions/
│   └── CoreExceptions.cs      - Custom exception types
└── Response/
    └── Schemas.cs             - Response schemas
```

## Usage

### 1. Create Your Entity Model

```csharp
using RootCore.Database;

public class Product : BaseModel
{
    public string Name { get; set; }
    public decimal Price { get; set; }
    public string Description { get; set; }
}
```

### 2. Create Your DbContext

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

### 3. Create Your Repository (Optional - if custom queries needed)

```csharp
using RootCore.Bases;

public class ProductRepository : BaseRepository<Product>
{
    public ProductRepository(ApplicationDbContext context) : base(context)
    {
    }
    
    // Add custom queries here if needed
}
```

### 4. Create Your Service (Optional - if custom business logic needed)

```csharp
using RootCore.Bases;
using RootCore.Exceptions;

public class ProductService : BaseService<Product>
{
    public ProductService(ProductRepository repository) : base(repository)
    {
    }
    
    // Override validation methods if needed
    protected override Task ValidateCreateAsync(Product entity)
    {
        if (string.IsNullOrEmpty(entity.Name))
        {
            throw new ValidationException("Product name is required");
        }
        return Task.CompletedTask;
    }
}
```

### 5. Create Your Controller

```csharp
using Microsoft.AspNetCore.Mvc;
using RootCore.Bases;

[Route("api/[controller]")]
public class ProductsController : BaseController<Product>
{
    public ProductsController(ProductService service) : base(service)
    {
    }
    
    // Inherited endpoints:
    // GET api/products - Get paginated list
    // GET api/products/all - Get all items
    // GET api/products/{id} - Get by ID
    // POST api/products - Create
    // PUT api/products/{id} - Update
    // DELETE api/products/{id} - Soft delete
    // POST api/products/{id}/restore - Restore
    // DELETE api/products/{id}/force - Force delete
    // GET api/products/{id}/exists - Check exists
    // GET api/products/count - Count items
    // POST api/products/bulk - Bulk create
    // POST api/products/bulk-delete - Bulk delete
}
```

### 6. Register Services in Program.cs

```csharp
using Microsoft.EntityFrameworkCore;
using RootCore.Configuration;

var builder = WebApplication.CreateBuilder(args);

// Add configuration
builder.Services.Configure<AppSettings>(builder.Configuration.GetSection("AppSettings"));

// Add DbContext
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection")));

// Register repositories and services
builder.Services.AddScoped<ProductRepository>();
builder.Services.AddScoped<ProductService>();

// Add controllers
builder.Services.AddControllers();

var app = builder.Build();

app.MapControllers();
app.Run();
```

## Features

### Soft Delete

All entities inheriting from `BaseModel` support soft delete:
- Deleted items are marked with `IsDeleted = true`
- Queries automatically exclude deleted items
- Use `includeDeleted` parameter to include deleted items
- Restore deleted items with the restore endpoint

### Pagination

The base controller provides pagination support:

```
GET /api/products?page=1&perPage=10
```

Returns:
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

All endpoints return standardized responses:

Success:
```json
{
  "data": {...},
  "message": "Item created successfully",
  "success": true
}
```

Error:
```json
{
  "message": "Item not found",
  "detail": "Additional error details",
  "success": false
}
```

## Configuration

Add to your `appsettings.json`:

```json
{
  "AppSettings": {
    "DatabaseUri": "Data Source=app.db",
    "SecretKey": "your-secret-key-here",
    "Algorithm": "HS256",
    "AccessTokenExpireMinutes": 30,
    "ProjectName": "My ASP.NET Project",
    "ProjectVersion": "1.0.0",
    "TimeZone": "UTC",
    "UploadFolder": "uploads",
    "StaticDir": "wwwroot"
  },
  "ConnectionStrings": {
    "DefaultConnection": "Data Source=app.db"
  }
}
```

## Migration from Python/FastAPI

Key differences from the Python version:

1. **Database**: SQLModel/SQLAlchemy → Entity Framework Core
2. **Routing**: FastAPI decorators → ASP.NET Core attributes
3. **Dependency Injection**: Built into ASP.NET Core
4. **Async/Await**: Similar pattern in both
5. **Configuration**: Python settings → appsettings.json
6. **Authentication**: JWT compatible in both frameworks

## Requirements

- .NET 10.0 or compatible
- Entity Framework Core
- Microsoft.AspNetCore.Mvc.Core
- Microsoft.AspNetCore.Authentication.JwtBearer

## License

This project maintains the same license as the original Python library.

## Contributing

Contributions are welcome! Please follow the existing code patterns and conventions.
