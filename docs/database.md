# Database & Models

The project uses **SQLModel** (which wraps SQLAlchemy) for ORM and database interactions. It supports both asynchronous and synchronous sessions, with a strong focus on soft deletes and audit logging.

## Database Connection (`core/database.py`)

The database connection is managed via `create_async_engine` for async operations and `create_engine` for sync operations.

### Sessions

- **`get_session()`**: Async context manager for database sessions. Used in FastAPI dependencies.
- **`get_local_session()`**: Sync context manager. Useful for scripts or non-async contexts.

### Base Model

All models should inherit from `BaseModel` (defined in `core/database.py`), which provides:

- **`id`**: Primary key (integer).
- **`is_deleted`**: Boolean flag for soft deletes.

## Repository Pattern (`core/bases/base_repository.py`)

The `BaseRepository` class provides a generic implementation for common database operations. It handles:

- **CRUD**: `create`, `get`, `update`, `delete` (soft), `force_delete`.
- **Bulk Operations**: `bulk_create`, `bulk_update`, `bulk_delete`.
- **Querying**: `list` (paginated), `search`, `count`, `exists`.
- **Soft Deletes**: Automatically filters out deleted records unless `include_deleted=True` is passed.
- **Audit Logging**: Automatically logs changes (`create`, `update`, `delete`, `restore`) to a `Log` model.

### Usage

To create a repository for a model:

```python
from core.bases.base_repository import BaseRepository
from my_app.models import MyModel

class MyModelRepository(BaseRepository[MyModel]):
    model = MyModel
```

## Seeding (`core/bases/base_seed.py`)

The `BaseSeeder` abstract class provides a standard way to seed initial data.

- **`data()`**: Implement this method to return a list of model instances to seed.
- **`execute()`**: Runs the seeding process, skipping existing records and resetting auto-increment counters if necessary.
