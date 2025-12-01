# Database Management Commands

The framework provides CLI commands for database management using Alembic migrations.

## Commands

### `db-init` - Initialize Database

Creates the database and runs migrations.

```bash
# Create database and run all migrations
poetry run python cli.py db-init

# Only create database, skip migrations
poetry run python cli.py db-init --no-migrate

# Only run migrations, skip database creation
poetry run python cli.py db-init --no-create-db
```

**What it does:**

1. Reads `DATABASE_URL` from `.env`
2. Creates the database if it doesn't exist (PostgreSQL, MySQL, or SQLite)
3. Runs `alembic upgrade head` to apply all migrations

### `db-migrate` - Create Migration

Creates a new Alembic migration file.

```bash
# Auto-generate migration from model changes
poetry run python cli.py db-migrate "Add user table"

# Create empty migration (manual)
poetry run python cli.py db-migrate "Custom migration" --no-autogenerate
```

**What it does:**

1. Runs `alembic revision --autogenerate -m "message"`
2. Creates a new migration file in `migrations/versions/`
3. Detects model changes automatically

### `db-upgrade` - Upgrade Database

Applies migrations to upgrade the database.

```bash
# Upgrade to latest
poetry run python cli.py db-upgrade

# Upgrade to specific revision
poetry run python cli.py db-upgrade abc123

# Upgrade one step
poetry run python cli.py db-upgrade +1
```

### `db-downgrade` - Downgrade Database

Rolls back migrations.

```bash
# Downgrade one step
poetry run python cli.py db-downgrade -1

# Downgrade to specific revision
poetry run python cli.py db-downgrade abc123

# Downgrade to base (remove all)
poetry run python cli.py db-downgrade base
```

## Workflow Example

### 1. Initial Setup

```bash
# Create database and apply existing migrations
poetry run python cli.py db-init
```

### 2. Add New Model

Create a new model in your module:

```python
# core/apps/driver/models/driver.py
from sqlmodel import Field
from core.database import BaseModel

class Driver(BaseModel, table=True):
    __tablename__ = "drivers"
    
    name: str = Field()
    license_number: str = Field()
```

### 3. Generate Migration

```bash
# Auto-generate migration
poetry run python cli.py db-migrate "Add driver table"
```

### 4. Apply Migration

```bash
# Apply the new migration
poetry run python cli.py db-upgrade
```

### 5. Rollback (if needed)

```bash
# Undo last migration
poetry run python cli.py db-downgrade -1
```

## Database Support

### PostgreSQL

```env
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
```

The command will:

- Connect to the `postgres` database
- Create `mydb` if it doesn't exist
- Run migrations on `mydb`

### MySQL

```env
DATABASE_URL=mysql://user:password@localhost:3306/mydb
```

The command will:

- Connect to MySQL server
- Create `mydb` if it doesn't exist
- Run migrations on `mydb`

### SQLite

```env
DATABASE_URL=sqlite:///./database.db
```

The command will:

- Create the database file if it doesn't exist
- Run migrations

## Troubleshooting

### "Alembic not found"

```bash
pip install alembic
```

### "Alembic not initialized"

```bash
alembic init migrations
```

Then update `migrations/env.py` to import `core.models`.

### Database already exists

The command will skip creation and just run migrations.

### Migration conflicts

If you have multiple developers:

1. Pull latest code
2. Run `python cli.py db-upgrade` to apply their migrations
3. Create your migration
4. Resolve any conflicts in the migration file

## Tips

- **Always backup** before running migrations in production
- **Test migrations** in development first
- **Review generated migrations** - auto-generate isn't perfect
- **Use descriptive messages** for migrations
- **Don't edit applied migrations** - create a new one instead
