# ROOT CORE - Modular Monolith Framework

A modular monolith FastAPI framework for building scalable applications with clean architecture.

## Architecture

This project follows a **Modular Monolith** architecture pattern:

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

## Project Structure

```
root-core/
├── core/                    # Core framework
│   ├── apps/               # Application modules
│   │   ├── auth/          # Authentication module
│   │   ├── archive/       # Archive/file management module
│   │   └── base/          # Base utilities module
│   ├── bases/             # Base classes (Router, Service, Repository)
│   ├── module_registry.py # Module registration and discovery
│   └── app.py             # Main FastAPI application
├── main.py                 # Application entry point
├── migrations/             # Database migrations
└── tests/                  # Test suite
```

## Installation

```bash
# Install dependencies with Poetry
poetry install

# Run the application
poetry run python main.py
```

## Creating New Modules

1. Create a new directory under `core/apps/`
2. Add models, routers, services, repositories, and schemas
3. Register routers in the module's `__init__.py`
4. Add the module to `core/module_registry.py`

## Features

- **FastAPI** - Modern, fast web framework
- **SQLModel** - SQL databases with Pydantic models
- **JWT Authentication** - Secure token-based auth
- **RBAC** - Role-based access control
- **Soft Delete** - Automatic soft delete support
- **Audit Logging** - Track changes to records