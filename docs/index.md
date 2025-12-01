# Core Framework Documentation

Welcome to the Core Framework documentation. This framework provides a foundation for building **Modular Monolith** applications with FastAPI and SQLModel.

## Quick Start

### Installation

```bash
# Install dependencies with Poetry
poetry install

# Run the application
poetry run python main.py
```

### Access the API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Architecture

This project follows a **Modular Monolith** architecture pattern where all modules run in a single process but are organized with clear boundaries:

```
┌────────────────────────────────────────┐
│         Main Application (:8000)       │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │  Auth    │ │ Archive  │ │  Base  │ │
│  │  Module  │ │  Module  │ │ Module │ │
│  └──────────┘ └──────────┘ └────────┘ │
└────────────────────────────────────────┘
                    │
              ┌─────┴─────┐
              │  Database │
              └───────────┘
```

## Core Guides

### 🏗️ [Module Structure](module-structure.md)

How to create and organize modules:

- Module directory structure
- Models, Schemas, Repositories, Services, Routers
- Module registration

### 🔐 [Security Manager](security-manager.md)

Authentication and authorization:

- JWT token management
- Password hashing
- Permission checking
- Custom security implementations

### 🗄️ [Database Management](database-commands.md)

Database commands and migrations:

- `db-init` - Create and initialize databases
- `db-migrate` - Generate migrations
- `db-upgrade` / `db-downgrade` - Apply/rollback migrations

### 🔄 [Migrations](migrations.md)

Database migration management:

- Auto-discovery of models
- App-specific migrations
- Alembic integration

## Key Features

✅ **Modular Architecture** - Clean separation of concerns with modules  
✅ **Type Safety** - Full type hints with Pydantic and SQLModel  
✅ **Auto CRUD** - Generic CRUD API with `CRUDApi` base class  
✅ **Soft Delete** - Built-in soft delete support  
✅ **Audit Logging** - Automatic change tracking  
✅ **RBAC** - Role-based access control  
✅ **CLI Tools** - Powerful commands for app management  

## Project Structure

```
root-core/
├── core/                      # Core framework
│   ├── apps/                  # Application modules
│   │   ├── auth/             # Authentication module
│   │   ├── archive/          # File/archive module
│   │   └── base/             # Base utilities
│   ├── bases/                # Base classes
│   │   ├── base_router.py    # Router base class
│   │   ├── base_service.py   # Service base class
│   │   ├── base_repository.py # Repository base class
│   │   └── crud_api.py       # Generic CRUD router
│   ├── module_registry.py    # Module discovery
│   ├── security_manager.py   # Authentication
│   └── app.py                # FastAPI application
├── main.py                   # Entry point
├── migrations/               # Database migrations
├── docs/                     # Documentation
└── tests/                    # Test suite
```

## CLI Commands

### App Management

```bash
# Create new app
poetry run python cli.py app-create <name>

# List apps
poetry run python cli.py list-apps
```

### Database Management

```bash
# Initialize database
poetry run python cli.py db-init

# Create migration
poetry run python cli.py db-migrate "Migration message"

# Apply migrations
poetry run python cli.py db-upgrade
```

## Creating a New Module

### 1. Create Module Structure

```bash
mkdir -p core/apps/my_module/{models,schemas,repositories,services,routers,utils}
touch core/apps/my_module/__init__.py
```

### 2. Create Model

```python
# core/apps/my_module/models/item.py
from sqlmodel import Field
from core.database import BaseModel

class Item(BaseModel, table=True):
    __tablename__ = "items"
    
    name: str = Field(index=True)
    description: str | None = None
```

### 3. Create Repository

```python
# core/apps/my_module/repositories/item_repository.py
from core.bases.base_repository import BaseRepository
from ..models.item import Item

class ItemRepository(BaseRepository[Item]):
    model = Item
```

### 4. Create Service

```python
# core/apps/my_module/services/item_service.py
from core.bases.base_service import BaseService
from ..repositories.item_repository import ItemRepository

class ItemService(BaseService):
    def __init__(self, repository: ItemRepository):
        super().__init__(repository)
```

### 5. Create Router

```python
# core/apps/my_module/routers/item_router.py
from core.bases.crud_api import CRUDApi
from core.database import get_session
from ..services.item_service import ItemService
from ..repositories.item_repository import ItemRepository

def get_service():
    return ItemService(ItemRepository(get_session))

class ItemRouter(CRUDApi):
    def __init__(self):
        super().__init__(
            service=get_service(),
            resource_name="items",
            tags=["Items"],
        )

router = ItemRouter()
```

### 6. Register Module

```python
# core/apps/my_module/__init__.py
from .routers.item_router import router as item_router
routers = [item_router]
```

```python
# core/module_registry.py - Add import
from core.apps.my_module import routers as my_module_routers

def get_all_routers():
    return [
        ...
        *my_module_routers,
    ]
```

## Development Workflow

### 1. Start Development Server

```bash
poetry run python main.py
```

### 2. Make Changes

Edit modules in `core/apps/`

### 3. Run Migrations

```bash
poetry run python cli.py db-migrate "Add new table"
poetry run python cli.py db-upgrade
```

### 4. Test

```bash
poetry run pytest
```

## Best Practices

1. **Module Isolation** - Keep modules independent, avoid cross-module imports
2. **Repository Pattern** - All database access through repositories
3. **Service Layer** - Business logic in services, not routers
4. **Type Hints** - Use type hints everywhere
5. **Soft Delete** - Use soft delete for important data
6. **Logging** - Use the built-in audit logging

## Resources

- [Module Structure](module-structure.md) - Detailed module guide
- [Security Manager](security-manager.md) - Authentication setup
- [Database Commands](database-commands.md) - Database management
- [Migrations](migrations.md) - Database migrations

## Support

For issues or questions, check the project repository:
https://github.com/GhaziRiyadh/root-core
