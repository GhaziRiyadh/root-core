# Sample Web API using RootCore

This is a sample ASP.NET Core Web API project demonstrating the usage of the RootCore library.

## Features

- Product CRUD API using RootCore base classes
- SQLite database with Entity Framework Core
- Automatic soft-delete support
- Swagger/OpenAPI documentation
- All CRUD endpoints inherited from `BaseController`

## Running the Application

1. Build the solution:
```bash
dotnet build
```

2. Run the application:
```bash
dotnet run
```

3. Open your browser and navigate to:
   - Swagger UI: `https://localhost:5001/swagger` (or the port shown in console)
   - OpenAPI spec: `https://localhost:5001/openapi/v1.json`

## Available Endpoints

All endpoints are automatically available from the `ProductsController` which inherits from `BaseController<Product>`:

### Products API

- `GET /api/products` - Get paginated list of products
  - Query params: `page`, `perPage`, `includeDeleted`
  
- `GET /api/products/all` - Get all products without pagination
  - Query params: `includeDeleted`
  
- `GET /api/products/{id}` - Get a product by ID
  - Query params: `includeDeleted`
  
- `POST /api/products` - Create a new product
  - Body: `{ "name": "string", "description": "string", "price": 0, "stock": 0 }`
  
- `PUT /api/products/{id}` - Update a product
  - Body: `{ "name": "string", "description": "string", "price": 0, "stock": 0 }`
  
- `DELETE /api/products/{id}` - Soft delete a product (sets IsDeleted flag)
  
- `POST /api/products/{id}/restore` - Restore a soft-deleted product
  
- `DELETE /api/products/{id}/force` - Permanently delete a product
  
- `GET /api/products/{id}/exists` - Check if a product exists
  - Query params: `includeDeleted`
  
- `GET /api/products/count` - Count products
  - Query params: `includeDeleted`
  
- `POST /api/products/bulk` - Create multiple products
  - Body: Array of product objects
  
- `POST /api/products/bulk-delete` - Delete multiple products
  - Body: Array of product IDs

## Example Requests

### Create a Product
```bash
curl -X POST https://localhost:5001/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 1299.99,
    "stock": 10
  }'
```

Response:
```json
{
  "data": {
    "id": 1,
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 1299.99,
    "stock": 10,
    "isDeleted": false
  },
  "message": "Item created successfully",
  "success": true
}
```

### Get All Products (Paginated)
```bash
curl https://localhost:5001/api/products?page=1&perPage=10
```

Response:
```json
{
  "items": [
    {
      "id": 1,
      "name": "Laptop",
      "description": "High-performance laptop",
      "price": 1299.99,
      "stock": 10,
      "isDeleted": false
    }
  ],
  "total": 1,
  "page": 1,
  "perPage": 10,
  "pages": 1,
  "message": "Success"
}
```

### Update a Product
```bash
curl -X PUT https://localhost:5001/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Laptop",
    "description": "High-performance gaming laptop",
    "price": 1499.99,
    "stock": 8
  }'
```

### Soft Delete a Product
```bash
curl -X DELETE https://localhost:5001/api/products/1
```

### Restore a Deleted Product
```bash
curl -X POST https://localhost:5001/api/products/1/restore
```

## Code Structure

```
SampleWebApi/
├── Controllers/
│   └── ProductsController.cs   - API controller (inherits from BaseController)
├── Data/
│   └── ApplicationDbContext.cs - EF Core DbContext
├── Models/
│   └── Product.cs              - Product entity (inherits from BaseModel)
├── Program.cs                  - Application startup
└── appsettings.json           - Configuration
```

## Key Points

1. **No Repository or Service Implementation Needed**: The `ProductsController` directly uses `BaseService<Product>` and `BaseRepository<Product>` provided by RootCore.

2. **Automatic CRUD**: All CRUD endpoints are inherited from `BaseController<Product>`.

3. **Soft Delete**: Products are never actually deleted from the database by default. They're marked with `IsDeleted = true`.

4. **Easy Customization**: You can override methods in the controller, service, or repository to add custom behavior.

## Extending the Sample

### Add Custom Endpoints

```csharp
public class ProductsController : BaseController<Product>
{
    // ... constructor

    [HttpGet("search")]
    public async Task<ActionResult> SearchByName([FromQuery] string name)
    {
        // Add custom search logic
    }
}
```

### Add Custom Validation

Create a custom service:

```csharp
public class ProductService : BaseService<Product>
{
    public ProductService(BaseRepository<Product> repository) : base(repository)
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

Then register it in Program.cs:
```csharp
builder.Services.AddScoped<ProductService>();
// Update controller to use ProductService instead of BaseService<Product>
```

## Database

The sample uses SQLite with a database file named `sample.db` which will be created in the project directory on first run.

To reset the database, simply delete the `sample.db` file and restart the application.
