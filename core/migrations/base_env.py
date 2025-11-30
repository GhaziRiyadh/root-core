"""
Base migration environment for Alembic.

This module provides reusable migration logic that can be imported
by any `migrations/env.py` file, enabling app-specific database migrations.

Usage in migrations/env.py:
    import os
    from core.migrations.base_env import run_migrations_offline, run_migrations_online
    from alembic import context
    
    app_name = os.getenv('ALEMBIC_APP')
    
    if context.is_offline_mode():
        run_migrations_offline(app_name)
    else:
        run_migrations_online(app_name)
"""
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel
from core.config import settings
from core.database_registry import discover_app_database


def get_migration_config(app_name=None):
    """
    Get migration configuration for an app.
    
    Args:
        app_name: Name of the app (e.g., 'auth', 'driver')
                 If None, uses default database
    
    Returns:
        Alembic config object
    """
    config = context.config
    
    if app_name:
        # Use app-specific database
        db_url = discover_app_database(app_name)
        config.set_main_option("sqlalchemy.url", db_url)
        
        print(f"🔧 Using database for app: {app_name}")
        print(f"   URL: {db_url}")
        
        # Import app-specific models
        _import_app_models(app_name)
    else:
        # Use default database and import all models
        config.set_main_option("sqlalchemy.url", settings.DATABASE_URI)
        
        print(f"🔧 Using default database")
        print(f"   URL: {settings.DATABASE_URI}")
        
        # Import all models
        import core.models
    
    return config


def _import_app_models(app_name: str):
    """
    Import models for a specific app.
    
    Args:
        app_name: Name of the app
    """
    try:
        # Try to import app's models module
        import importlib
        apps_dir = settings.APPS_DIR.replace('/', '.')
        models_module = f"{apps_dir}.{app_name}.models"
        
        importlib.import_module(models_module)
        print(f"   ✅ Imported models from {models_module}")
    except ImportError as e:
        print(f"   ⚠️  Could not import models for {app_name}: {e}")
        # Fall back to importing all models
        import core.models


def run_migrations_offline(app_name=None):
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    
    Args:
        app_name: Optional app name for app-specific migrations
    """
    config = get_migration_config(app_name)
    url = config.get_main_option("sqlalchemy.url")
    
    context.configure(
        url=url,
        target_metadata=SQLModel.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online(app_name=None):
    """
    Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine
    and associate a connection with the context.
    
    Args:
        app_name: Optional app name for app-specific migrations
    """
    config = get_migration_config(app_name)
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=SQLModel.metadata
        )
        
        with context.begin_transaction():
            context.run_migrations()
