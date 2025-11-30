# Dynamic Multi-Database Configuration

## Overview

The framework now supports **dynamic database discovery** - each app can automatically have its own database without manual configuration!

## How It Works

The system automatically discovers app databases using this priority:

1. **Environment Variable**: `<APP_NAME>_DATABASE_URL`
2. **App's database.py**: Custom database configuration per app
3. **Default**: Falls back to main `DATABASE_URL`

## Usage

### Initialize All App Databases

```bash
# Automatically discover and initialize all app databases
python cli.py db-init --all-apps
```

### Initialize Specific App Database

```bash
# Initialize just the auth app database
python cli.py db-init --app auth

# Initialize driver app database
python cli.py db-init --app driver
```

### List All App Databases

```bash
# See all configured app databases
python cli.py db-list
```

## Configuration Methods

### Method 1: Environment Variables (Simplest)

Add to your `.env`:

```env
# Default database
DATABASE_URL=postgresql://user:pass@localhost:5432/main_db

# App-specific databases (optional)
AUTH_DATABASE_URL=postgresql://user:pass@localhost:5432/auth_db
USER_DATABASE_URL=postgresql://user:pass@localhost:5432/user_db
DRIVER_DATABASE_URL=postgresql://user:pass@localhost:5432/driver_db
```

### Method 2: App's database.py (Most Flexible)

Create `database.py` in your app:

```python
# apps/auth/database.py
DATABASE_URL = "postgresql://user:pass@localhost:5432/auth_db"
```

The framework automatically discovers and uses it!

### Method 3: No Configuration (Uses Default)

If an app doesn't have a specific database configured, it uses the default `DATABASE_URL`.

## Using App-Specific Databases in Code

### In Repositories

```python
# apps/auth/repositories/user_repository.py
from core.multi_database import get_app_session

class UserRepository(BaseRepository[User]):
    model = User
    
    async def get_all(self):
        # Automatically uses auth database
        async with get_app_session('auth') as session:
            result = await session.execute(select(User))
            return result.scalars().all()
```

### Auto-Detect Current App

```python
# apps/auth/repositories/user_repository.py
from core.multi_database import get_app_session
from core.utils.utils import get_current_app

class UserRepository(BaseRepository[User]):
    model = User
    
    async def get_all(self):
        # Auto-detect which app this repository belongs to
        app_name = get_current_app(__file__) or 'auth'
        
        async with get_app_session(app_name) as session:
            result = await session.execute(select(User))
            return result.scalars().all()
```

## Docker Compose Example

Run multiple databases easily:

```yaml
# docker-compose.databases.yml
version: '3.8'

services:
  auth-db:
    image: postgres:15
    environment:
      POSTGRES_DB: auth_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
  
  user-db:
    image: postgres:15
    environment:
      POSTGRES_DB: user_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5433:5432"
  
  driver-db:
    image: postgres:15
    environment:
      POSTGRES_DB: driver_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5434:5432"
```

Start databases:

```bash
docker-compose -f docker-compose.databases.yml up -d
```

Update `.env`:

```env
AUTH_DATABASE_URL=postgresql://user:password@localhost:5432/auth_db
USER_DATABASE_URL=postgresql://user:password@localhost:5433/user_db
DRIVER_DATABASE_URL=postgresql://user:password@localhost:5434/driver_db
```

## Complete Workflow

### 1. Start Databases

```bash
docker-compose -f docker-compose.databases.yml up -d
```

### 2. Configure Apps

```env
# .env
AUTH_DATABASE_URL=postgresql://user:password@localhost:5432/auth_db
DRIVER_DATABASE_URL=postgresql://user:password@localhost:5433/driver_db
```

### 3. Initialize All Databases

```bash
python cli.py db-init --all-apps
```

### 4. Create Migrations

```bash
# Create migration for auth app
python cli.py db-migrate "Add user table"
```

### 5. Apply Migrations

```bash
# Apply to all apps
python cli.py db-upgrade
```

## Benefits

✅ **Zero Configuration**: Apps work with default database by default  
✅ **Flexible**: Each app can have its own database when needed  
✅ **Auto-Discovery**: Framework finds app databases automatically  
✅ **Gradual Migration**: Start with one database, split as you grow  
✅ **Microservices Ready**: Each app already has database isolation  

## Migration Path

### Phase 1: Single Database (Now)

```bash
# All apps use default database
python cli.py db-init
```

### Phase 2: Separate Databases (Transition)

```bash
# Add app-specific database URLs to .env
# Initialize all app databases
python cli.py db-init --all-apps
```

### Phase 3: Microservices (Future)

```bash
# Each service has its own .env and database
cd services/auth-service
python cli.py db-init
```

## Example: Adding Driver Database

### Step 1: Add to .env

```env
DRIVER_DATABASE_URL=postgresql://user:password@localhost:5434/driver_db
```

### Step 2: Initialize

```bash
python cli.py db-init --app driver
```

### Step 3: Use in Code

```python
# apps/driver/repositories/driver_repository.py
from core.multi_database import get_app_session

async def get_drivers():
    async with get_app_session('driver') as session:
        result = await session.execute(select(Driver))
        return result.scalars().all()
```

Done! The driver app now has its own database! 🎉
