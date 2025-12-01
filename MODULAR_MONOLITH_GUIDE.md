# Modular Monolith Architecture

## Overview

This project implements a **Modular Monolith** architecture using FastAPI. All modules run in a single process but are organized with clear boundaries and separation of concerns.

## Architecture

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

## Module Structure

Each module follows a consistent structure:

```
core/apps/<module_name>/
├── __init__.py          # Module initialization and router exports
├── models/              # SQLModel database models
├── schemas/             # Pydantic schemas for API
├── repositories/        # Data access layer
├── services/            # Business logic layer
├── routers/             # FastAPI routers
├── middlewares/         # Module-specific middleware
├── utils/               # Utility functions
└── enums/               # Enumerations
```

## Module Registration

Modules are registered in `core/module_registry.py`:

```python
from core.apps.auth import routers as auth_routers
from core.apps.archive import routers as archive_routers
from core.apps.base import routers as base_routers

def get_all_routers():
    return [
        *auth_routers,
        *archive_routers,
        *base_routers,
    ]
```

## Advantages of Modular Monolith

1. **Simpler Deployment**: Single process to deploy and manage
2. **Easier Development**: No need for complex service discovery
3. **Shared Resources**: Can share database connections, caching, etc.
4. **Faster Communication**: In-process calls instead of HTTP
5. **Lower Resource Usage**: One Python process instead of multiple
6. **Easier Debugging**: Single process to debug and trace

## Creating a New Module

1. Create directory structure:
   ```bash
   mkdir -p core/apps/my_module/{models,schemas,repositories,services,routers,utils}
   ```

2. Create `__init__.py` with router exports:
   ```python
   from .routers.my_router import router as my_router
   routers = [my_router]
   ```

3. Register in `core/module_registry.py`:
   ```python
   from core.apps.my_module import routers as my_routers
   # Add to get_all_routers()
   ```

## Running the Application

```bash
# Install dependencies
poetry install

# Run the application
poetry run python main.py

# Or with uvicorn directly
poetry run uvicorn main:app --reload --port 8000
```

## API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
