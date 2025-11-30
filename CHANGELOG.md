# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-11-30

### Added

- **Framework Layer**: Core now functions as a reusable framework layer over FastAPI
- **CoreApp Class**: Simplified FastAPI application setup with automatic configuration
- **Command System Refactoring**:
  - Split commands into separate class files in `core/commands/`
  - Auto-discovery of app-specific commands from `<APPS_DIR>/*/commands/*.py`
  - Clean `BaseCommand` interface without project-specific dependencies
- **Unified APPS_DIR Configuration**:
  - Single `APPS_DIR` setting controls all app discovery
  - Command discovery uses `APPS_DIR`
  - Router discovery uses `APPS_DIR`
  - Model discovery uses `APPS_DIR`
  - Permission generation uses `APPS_DIR`
- **Model Auto-Discovery for Migrations**:
  - Automatic model discovery from all apps in `APPS_DIR`
  - No need to manually import models in migration files
  - Alembic automatically detects all models
- **Comprehensive Documentation**:
  - `docs/index.md` - Project overview and setup
  - `docs/database.md` - Database layer documentation
  - `docs/api.md` - API layer documentation
  - `docs/architecture.md` - Core architecture documentation
  - `docs/app-commands.md` - Guide for creating app-specific commands
  - `docs/migrations.md` - Model auto-discovery for migrations

### Changed

- **main.py**: Simplified to use `CoreApp` wrapper
- **cli.py**: Now a clean entry point using `core.cli_entry`
- **core/utils/utils.py**: `get_apps()` now uses `settings.APPS_DIR`
- **core/models.py**: Uses `APPS_DIR` instead of hardcoded paths
- **migrations/env.py**: Fixed to import `core.models` for auto-discovery

### Fixed

- Removed hardcoded `src/apps` paths throughout the codebase
- Fixed import errors related to `src` vs `core` paths
- Corrected `BaseCommand` to remove circular dependencies

### Removed

- `core/commands/scaffold.py` - Split into individual command classes

## [0.1.0] - Initial Release

### Added

- Initial FastAPI and MySQL core application
- Base classes for Repository, Service, Router, and Middleware
- CRUD API functionality
- Authentication system
- Database connection management
- Exception handling
