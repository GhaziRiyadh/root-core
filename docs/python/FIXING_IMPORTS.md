# Fixing Import Issues - Root Core Python Library

## The Problem

When trying to use root-core as a pip-installed library in your FastAPI application, you may encounter import errors like:

```python
ImportError: cannot import name 'BaseModel' from 'src.core.database'
ModuleNotFoundError: No module named 'src'
```

This occurs because the library code contains references to `src.core` instead of just `core`.

## Quick Fix

### Option 1: Fix Imports in Your Project (Recommended)

When using the library, always import from `core`, not `src.core`:

```python
# ✅ Correct
from core.database import BaseModel
from core.bases.base_router import BaseRouter
from core.bases.base_service import BaseService
from core.config import settings

# ❌ Wrong
from src.core.database import BaseModel
from src.core.bases.base_router import BaseRouter
```

### Option 2: Add src Directory to Python Path

If the library code itself has `src.core` imports, add this to your main application file:

```python
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Now imports will work
from core.database import BaseModel
```

### Option 3: Fix Library Imports (If you have source)

If you have cloned the repository and want to fix it permanently:

1. **Clone the repository**:
```bash
git clone https://github.com/GhaziRiyadh/root-core.git
cd root-core
```

2. **Find and replace all imports**:
```bash
# On Linux/Mac
find core -name "*.py" -type f -exec sed -i 's/from src\.core/from core/g' {} +
find core -name "*.py" -type f -exec sed -i 's/import src\.core/import core/g' {} +

# On Windows (PowerShell)
Get-ChildItem -Path core -Filter *.py -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace 'from src\.core', 'from core' | Set-Content $_.FullName
    (Get-Content $_.FullName) -replace 'import src\.core', 'import core' | Set-Content $_.FullName
}
```

3. **Install in development mode**:
```bash
pip install -e .
```

## Detailed Explanation

### Why This Happens

The root-core library was originally developed as part of a larger project with the following structure:

```
project/
├── src/
│   └── core/
│       ├── __init__.py
│       ├── database.py
│       └── bases/
```

When extracted as a standalone library, the structure became:

```
root-core/
├── core/
│   ├── __init__.py
│   ├── database.py
│   └── bases/
└── pyproject.toml
```

However, some imports in the code still reference `src.core`, which causes issues.

### Files That May Have This Issue

Check these files for `src.core` imports:

- `core/bases/base_router.py`
- `core/bases/base_service.py`
- `core/bases/base_repository.py`
- `core/router.py`
- `core/database.py`
- Any files in `core/apps/`

### Example: Fixing base_router.py

**Before** (❌ Won't work as library):
```python
from src.core.apps.auth.middlewares.require_permissions import require_permissions
from src.core.bases.base_middleware import BaseMiddleware
from src.core.apps.auth.utils.utils import get_current_active_user
from src.core.utils.utils import get_current_app
```

**After** (✅ Works as library):
```python
from core.apps.auth.middlewares.require_permissions import require_permissions
from core.bases.base_middleware import BaseMiddleware
from core.apps.auth.utils.utils import get_current_active_user
from core.utils.utils import get_current_app
```

## Complete Working Example

Here's a complete example of using root-core as a library in your FastAPI project:

### 1. Install the Library

```bash
pip install git+https://github.com/GhaziRiyadh/root-core.git
```

### 2. Create Your Project Structure

```
my-fastapi-app/
├── main.py
├── models/
│   ├── __init__.py
│   └── product.py
├── routers/
│   ├── __init__.py
│   └── product_router.py
├── services/
│   ├── __init__.py
│   └── product_service.py
├── repositories/
│   ├── __init__.py
│   └── product_repository.py
├── .env
└── requirements.txt
```

### 3. models/product.py

```python
from sqlmodel import Field
from core.database import BaseModel  # Import from core, not src.core

class Product(BaseModel, table=True):
    """Product model."""
    __tablename__ = "products"
    
    name: str = Field(max_length=200)
    description: str | None = None
    price: float = Field(ge=0)
    stock: int = Field(default=0)
```

### 4. repositories/product_repository.py

```python
from core.bases.base_repository import BaseRepository  # Import from core
from models.product import Product

class ProductRepository(BaseRepository):
    """Product repository."""
    
    def __init__(self):
        super().__init__(Product)
```

### 5. services/product_service.py

```python
from core.bases.base_service import BaseService  # Import from core
from core.exceptions import ValidationException  # Import from core
from repositories.product_repository import ProductRepository

class ProductService(BaseService):
    """Product service."""
    
    def __init__(self, repository: ProductRepository):
        super().__init__(repository)
    
    async def _validate_create(self, create_data: dict):
        """Validate product creation."""
        if create_data.get('price', 0) < 0:
            raise ValidationException("Price cannot be negative")
```

### 6. routers/product_router.py

```python
from core.bases.base_router import BaseRouter  # Import from core
from core.router import add_route  # Import from core
from core.config import PermissionAction  # Import from core
from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int = 0

class ProductRouter(BaseRouter):
    """Product router."""
    
    def __init__(self):
        super().__init__(
            resource_name="products",
            prefix="/api/products",
            tags=["Products"],
            create_schema=ProductCreate
        )

# Get the router instance
router = ProductRouter().get_router()
```

### 7. main.py

```python
from fastapi import FastAPI
from core.database import engine, BaseModel  # Import from core
import sys
from pathlib import Path

# Ensure core package is importable
sys.path.insert(0, str(Path(__file__).parent))

# Import your routers
from routers.product_router import router as product_router

app = FastAPI(
    title="My Product API",
    version="1.0.0"
)

@app.on_event("startup")
async def startup():
    """Initialize database."""
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

# Include routers
app.include_router(product_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 8. .env

```env
DATABASE_URL=sqlite:///./app.db
ASYNC_DATABASE_URL=sqlite+aiosqlite:///./app.db
SECRET_KEY=your-secret-key-here
```

### 9. requirements.txt

```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlmodel>=0.0.14
git+https://github.com/GhaziRiyadh/root-core.git
```

## Running Your Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

The API will be available at: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`

## Troubleshooting

### Issue: Module Not Found

**Error**:
```
ModuleNotFoundError: No module named 'core'
```

**Solution**:
```python
import sys
from pathlib import Path

# Add to main.py before any core imports
sys.path.insert(0, str(Path(__file__).parent))
```

### Issue: Circular Import

**Error**:
```
ImportError: cannot import name 'X' from partially initialized module 'core'
```

**Solution**:
- Check for circular dependencies in your imports
- Use TYPE_CHECKING for type hints:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.database import BaseModel
```

### Issue: SQLAlchemy/SQLModel Errors

**Error**:
```
sqlalchemy.exc.InvalidRequestError: Table 'products' is already defined
```

**Solution**:
- Ensure models are only defined once
- Use `table=True` only in the model definition
- Don't redefine BaseModel

```python
# ✅ Correct
class Product(BaseModel, table=True):
    __tablename__ = "products"
    name: str

# ❌ Wrong - Don't redefine
class Product(BaseModel, table=True):
    id: int  # Already in BaseModel
    is_deleted: bool  # Already in BaseModel
    name: str
```

### Issue: Async/Await Not Working

**Error**:
```
RuntimeWarning: coroutine 'get_all' was never awaited
```

**Solution**:
Always use `await` with async functions:

```python
# ✅ Correct
products = await service.get_all()

# ❌ Wrong
products = service.get_all()
```

## Testing Your Setup

Create a simple test to verify everything works:

```python
# test_setup.py
import asyncio
from core.database import BaseModel, engine

async def test_database():
    """Test database connection."""
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    print("✅ Database setup successful!")

if __name__ == "__main__":
    asyncio.run(test_database())
```

Run it:
```bash
python test_setup.py
```

If you see "✅ Database setup successful!", your setup is working correctly!

## Summary

To use root-core as a library:

1. ✅ Always import from `core`, not `src.core`
2. ✅ Add project directory to Python path if needed
3. ✅ Use async/await consistently
4. ✅ Follow the example project structure
5. ✅ Test your setup before building features

If you continue to have issues:
- Check Python version (requires 3.13+)
- Verify all dependencies are installed
- Review the complete working example above
- Check for typos in import statements

For additional help, open an issue on GitHub: https://github.com/GhaziRiyadh/root-core/issues
