# Project Overview

This project is a core foundation for building applications using **FastAPI** and **MySQL**. It provides a structured architecture with base classes for repositories, services, and routers to streamline development.

## Directory Structure

The project is organized into the following key directories within `core/`:

- **`apps/`**: Contains the application modules (e.g., `auth`, `archive`, `base`).
- **`bases/`**: Base classes for the architecture (Repository, Service, Router, CRUD API).
- **`helpers/`**: Helper functions and utilities.
- **`response/`**: Standardized response handling.
- **`schemas/`**: Pydantic schemas.
- **`services/`**: Shared services.
- **`utils/`**: General utility functions.
- **`database.py`**: Database connection and session management.
- **`config.py`**: Configuration management.
- **`router.py`**: Main router configuration.

## Setup

1. **Environment Variables**: Ensure you have a `.env` file configured (handled by `env_manager.py`).
2. **Dependencies**: Install dependencies using your package manager (e.g., `pip install -r requirements.txt` or `poetry install`).
3. **Database**: Configure your MySQL database connection in the environment variables.

## Key Features

- **FastAPI**: High-performance web framework.
- **MySQL**: Relational database support.
- **Base CRUD**: Simplified CRUD operations via `crud_api.py` and `base_repository.py`.
- **Modular Architecture**: scalable app structure.
