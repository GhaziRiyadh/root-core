# Python Library Usage Guide - Quick Summary

## ⚠️ Important: Fixing Import Issues

The main issue when using root-core as a pip library is **import path problems**. Some files in the library use `src.core` instead of `core`.

### Quick Fix

When using the library, **always import from `core`**, NOT `src.core`:

```python
# ✅ Correct
from core.database import BaseModel
from core.bases.base_router import BaseRouter
from core.bases.base_service import BaseService
from core.bases.base_repository import BaseRepository

# ❌ Wrong
from src.core.database import BaseModel
from src.core.bases.base_router import BaseRouter
```

**Full solution guide**: See [docs/python/FIXING_IMPORTS.md](FIXING_IMPORTS.md)

## Installation

```bash
# Option 1: Install from GitHub
pip install git+https://github.com/GhaziRiyadh/root-core.git

# Option 2: Install in development mode
git clone https://github.com/GhaziRiyadh/root-core.git
cd root-core
pip install -e .

# Option 3: Using Poetry
poetry add git+https://github.com/GhaziRiyadh/root-core.git
```

## Minimal Working Example

```python
# main.py
from fastapi import FastAPI
from sqlmodel import Field
from core.database import BaseModel, engine
from core.bases.base_router import BaseRouter

# 1. Define Model
class Product(BaseModel, table=True):
    __tablename__ = "products"
    name: str = Field(max_length=200)
    price: float = Field(ge=0)

# 2. Create Router
class ProductRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            resource_name="products",
            prefix="/api/products",
            tags=["Products"]
        )

# 3. Setup FastAPI
app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

# 4. Include Router
app.include_router(ProductRouter().get_router())

# Run with: uvicorn main:app --reload
```

This gives you 12+ CRUD endpoints automatically!

## Available Endpoints

When you create a router, you automatically get:

- `GET /api/products` - List with pagination
- `GET /api/products/all` - Get all
- `GET /api/products/{id}` - Get by ID
- `POST /api/products` - Create
- `PUT /api/products/{id}` - Update
- `DELETE /api/products/{id}` - Soft delete
- `POST /api/products/{id}/restore` - Restore
- `DELETE /api/products/{id}/force` - Force delete
- `GET /api/products/{id}/exists` - Check exists
- `GET /api/products/count` - Count items
- `POST /api/products/bulk` - Bulk create
- `POST /api/products/bulk-delete` - Bulk delete

## Common Issues & Solutions

### Issue 1: ImportError: cannot import name 'X' from 'src.core'

**Solution**: Import from `core` not `src.core`
```python
from core.database import BaseModel  # ✅ Correct
```

### Issue 2: ModuleNotFoundError: No module named 'core'

**Solution**: Add to your main.py:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### Issue 3: Database connection fails

**Solution**: Create `.env` file:
```env
DATABASE_URL=sqlite:///./database.db
ASYNC_DATABASE_URL=sqlite+aiosqlite:///./database.db
```

### Issue 4: Soft delete not working

**Solution**: Use `include_deleted` parameter:
```python
# Default: excludes deleted
items = await service.get_all()

# Include deleted
items = await service.get_all(include_deleted=True)
```

## Documentation Structure

Full documentation is available in `docs/python/`:

1. **[README.md](README.md)** - Complete guide with examples
2. **[FIXING_IMPORTS.md](FIXING_IMPORTS.md)** - **← Start here if you have import issues**
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture and design patterns
4. **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation

## Getting Help

- **Import problems?** → [FIXING_IMPORTS.md](FIXING_IMPORTS.md)
- **Need examples?** → [README.md](README.md)
- **API details?** → [API_REFERENCE.md](API_REFERENCE.md)
- **Architecture questions?** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **Still stuck?** → Open a GitHub issue

## Key Features

✅ Automatic CRUD endpoints
✅ Soft-delete support
✅ Pagination built-in
✅ Repository pattern
✅ Service pattern
✅ Type hints
✅ Async/await
✅ JWT authentication support
✅ Exception handling
✅ Bulk operations

## Next Steps

1. Install the library
2. Create a minimal example (see above)
3. Test it works: `uvicorn main:app --reload`
4. Read the full documentation for advanced features
5. Build your application!

---

**Having trouble?** The most common issue is import paths. Make sure you're importing from `core`, not `src.core`. See [FIXING_IMPORTS.md](FIXING_IMPORTS.md) for details.
