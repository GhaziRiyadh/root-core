# Dynamic Multi-Database Implementation Plan

## Goal

Enable each app to have its own database dynamically without hardcoding app names or database URLs. The framework should automatically discover and use app-specific databases.

## Problem Statement

Currently:

- All apps share one database (`DATABASE_URL`)
- Adding a new app requires manual configuration
- Not scalable for microservices architecture
- Hard to isolate data per service

## Proposed Solution

Create a **dynamic discovery system** that:

1. Automatically detects which app a repository/service belongs to
2. Looks for app-specific database configuration
3. Falls back to default database if no app-specific config exists
4. Requires zero configuration for simple cases

## Architecture

### Discovery Priority (in order)

```
1. Environment Variable: <APP_NAME>_DATABASE_URL
   ↓ (if not found)
2. App's database.py: apps/<app_name>/database.py
   ↓ (if not found)
3. Default: DATABASE_URL from .env
```

### File Structure

```
apps/
├── auth/
│   ├── database.py (optional)     # Custom DB config
│   ├── models/
│   ├── repositories/
│   └── services/
├── driver/
│   ├── database.py (optional)
│   └── ...
└── user/
    └── ...
```

## Implementation Steps

### Phase 1: Core Infrastructure

#### 1.1 Create `core/database_registry.py`

**Purpose**: Central registry for managing multiple database connections

**Functions**:

- `register_database(app_name, db_url)` - Register a database for an app
- `get_database_url(app_name)` - Get database URL for an app
- `get_engine(app_name)` - Get SQLAlchemy engine for an app
- `get_session(app_name)` - Get async session for an app
- `discover_databases()` - Auto-discover all app databases

**Key Features**:

- Lazy loading (create engine only when needed)
- Caching (reuse engines)
- Thread-safe
- Support for both sync and async engines

#### 1.2 Update `core/database.py`

**Changes**:

- Keep existing `engine` and `get_session()` for backward compatibility
- Add `get_app_session(app_name)` for app-specific sessions
- Import and expose database registry functions

### Phase 2: Auto-Discovery Mechanism

#### 2.1 Create Discovery Function

**Logic**:

```python
def discover_app_database(app_name: str) -> Optional[str]:
    # 1. Check environment variable
    env_key = f"{app_name.upper()}_DATABASE_URL"
    if env_key in os.environ:
        return os.getenv(env_key)
    
    # 2. Check app's database.py
    try:
        module = importlib.import_module(f"apps.{app_name}.database")
        if hasattr(module, 'DATABASE_URL'):
            return module.DATABASE_URL
    except ImportError:
        pass
    
    # 3. Fallback to default
    return settings.DATABASE_URL
```

#### 2.2 Auto-Detection of Current App

**Create**: `core/utils/app_detector.py`

**Function**: `get_current_app(file_path: str) -> Optional[str]`

**Logic**:

- Parse file path to extract app name
- Example: `apps/auth/repositories/user_repository.py` → `auth`
- Cache results for performance

### Phase 3: Repository Integration

#### 3.1 Update `BaseRepository`

**Add**:

- `app_name` property (auto-detected or explicit)
- Use app-specific session automatically

**Example**:

```python
class BaseRepository:
    app_name: Optional[str] = None  # Auto-detected if None
    
    def _get_app_name(self):
        if self.app_name:
            return self.app_name
        # Auto-detect from file path
        return get_current_app(__file__)
    
    async def get_session(self):
        app = self._get_app_name()
        return get_app_session(app)
```

### Phase 4: CLI Commands Enhancement

#### 4.1 Update `db-init` Command

**Add Options**:

- `--app <name>` - Initialize specific app database
- `--all-apps` - Initialize all discovered app databases
- `--discover` - Show discovered databases without initializing

**Logic**:

```python
if all_apps:
    databases = discover_all_app_databases()
    for app_name, db_url in databases.items():
        create_database(db_url)
        run_migrations(app_name)
elif app:
    db_url = discover_app_database(app)
    create_database(db_url)
    run_migrations(app)
else:
    # Default behavior (backward compatible)
    create_database(settings.DATABASE_URL)
    run_migrations()
```

#### 4.2 Add `db-list` Command

**Purpose**: List all discovered app databases

**Output**:

```
📊 Discovered Databases:

🔹 auth
   URL: postgresql://localhost:5432/auth_db
   Source: Environment variable (AUTH_DATABASE_URL)

🔹 driver
   URL: postgresql://localhost:5433/driver_db
   Source: apps/driver/database.py

🔹 user
   URL: postgresql://localhost:5432/main_db
   Source: Default (DATABASE_URL)
```

### Phase 5: Migration Management

#### 5.1 App-Specific Migrations

**Options**:

**Option A: Separate Migration Folders**

```
migrations/
├── auth/
│   └── versions/
├── driver/
│   └── versions/
└── user/
    └── versions/
```

**Option B: Single Folder with Naming Convention**

```
migrations/versions/
├── auth_001_initial.py
├── driver_001_initial.py
# .env
DATABASE_URL=postgresql://localhost:5432/main_db

# App-specific databases
AUTH_DATABASE_URL=postgresql://localhost:5432/auth_db
DRIVER_DATABASE_URL=postgresql://localhost:5433/driver_db
```

### Example 2: App's database.py

```python
# apps/auth/database.py
DATABASE_URL = "postgresql://localhost:5432/auth_db"

# Optional: Custom engine configuration
ENGINE_OPTIONS = {
    "pool_size": 10,
    "max_overflow": 20,
}
```

### Example 3: No Configuration (Uses Default)

```python
# apps/user/ (no database.py)
# Automatically uses DATABASE_URL from .env
```

## Usage Examples

### For Developers

```python
# apps/auth/repositories/user_repository.py
class UserRepository(BaseRepository[User]):
    model = User
    # app_name auto-detected as 'auth'
    # Automatically uses auth database
```

### For DevOps

```bash
# Initialize all app databases
python cli.py db-init --all-apps

# Initialize specific app
python cli.py db-init --app auth

# List all databases
python cli.py db-list

# Create migration for specific app
ALEMBIC_APP=auth python cli.py db-migrate "Add user table"
```

## Migration Path

### Phase 1: Current State (Single Database)

- All apps use `DATABASE_URL`
- No changes needed

### Phase 2: Gradual Separation

- Add `AUTH_DATABASE_URL` to `.env`
- Run `python cli.py db-init --app auth`
- Auth app now uses separate database
- Other apps still use default

### Phase 3: Full Separation

- Add database URLs for all apps
- Run `python cli.py db-init --all-apps`
- Each app has its own database

### Phase 4: Microservices

- Each service has its own `.env`
- Services run independently
- No code changes needed

## Benefits

✅ **Zero Configuration**: Works with default database out of the box  
✅ **Flexible**: Apps can opt-in to separate databases  
✅ **Auto-Discovery**: Framework finds databases automatically  
✅ **Backward Compatible**: Existing code continues to work  
✅ **Scalable**: Easy to add new apps  
✅ **Microservices Ready**: Natural path to service separation  

## Risks & Mitigation

### Risk 1: Performance (Multiple Connections)

**Mitigation**:

- Lazy loading (create connections only when needed)
- Connection pooling per app
- Configurable pool sizes

### Risk 2: Migration Complexity

**Mitigation**:

- Clear documentation
- Helper commands (`db-list`, `db-init --all-apps`)
- Gradual migration path

### Risk 3: Data Consistency

**Mitigation**:

- Use Kafka events for cross-app data sync
- Implement saga pattern for distributed transactions
- Document best practices

## Next Steps

1. **Review this plan** - Get approval before implementation
2. **Create Phase 1** - Database registry infrastructure
3. **Create Phase 2** - Auto-discovery mechanism
4. **Create Phase 3** - Repository integration
5. **Create Phase 4** - CLI commands
6. **Create Phase 5** - Migration management
7. **Test** - Verify with real apps
8. **Document** - Update docs with examples

## Questions for Review

1. Is the discovery priority correct? (env var → app file → default)
2. Should we support app-specific engine configuration?
3. Prefer separate migration folders per app or single folder?
4. Any additional CLI commands needed?
5. Should repositories auto-detect app name or require explicit config?

---

**Ready to proceed?** Please review and approve before I start implementation.
