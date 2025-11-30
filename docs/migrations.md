# Model Auto-Discovery for Migrations

The framework automatically discovers and imports all models from your apps for Alembic migrations.

## How It Works

When you run Alembic migrations, `migrations/env.py` imports `core.models`, which:

1. Scans all apps in `APPS_DIR` for `models/` directories
2. Automatically imports all model files
3. Makes them available to Alembic for migration generation

## Configuration

Set `APPS_DIR` in your `.env`:

```env
APPS_DIR=apps
```

## Directory Structure

```
<APPS_DIR>/
├── auth/
│   └── models/
│       ├── __init__.py
│       ├── user.py
│       └── permission.py
├── driver/
│   └── models/
│       ├── __init__.py
│       └── driver.py
└── ...
```

## Usage

### Generate Migration

```bash
alembic revision --autogenerate -m "Add new model"
```

Alembic will automatically detect all models from all apps in `APPS_DIR`.

### Apply Migration

```bash
alembic upgrade head
```

## How Models Are Discovered

The `core/models.py` file uses `get_app_paths("models")` which:

- Reads `APPS_DIR` from settings
- Scans each app for a `models/` directory
- Imports all `.py` files (except `__init__.py`)
- Registers them with SQLModel metadata

## Troubleshooting

If models aren't being detected:

1. **Check APPS_DIR**: Ensure it's set correctly in `.env`
2. **Check model files**: Models must inherit from `BaseModel` or `SQLModel`
3. **Check imports**: Run `python -c "import core.models"` to see what's loaded
4. **Check table=True**: Ensure your models have `table=True` for database tables

## Example Model

```python
from sqlmodel import Field
from core.database import BaseModel

class Driver(BaseModel, table=True):
    """Driver model."""
    
    __tablename__ = "drivers"
    
    name: str = Field()
    license_number: str = Field()
```

This model will be automatically discovered and included in migrations.
