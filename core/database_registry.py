"""
Dynamic database registry for multi-database support.

This module provides automatic discovery and management of app-specific databases.
Each app can have its own database, discovered through:
1. Environment variable: <APP_NAME>_DATABASE_URL
2. App's database.py file
3. Default DATABASE_URL

Example:
    # Auto-discover and use app-specific database
    from core.database_registry import get_app_session
    
    async with get_app_session('auth') as session:
        # This uses the auth app's database
        result = await session.execute(select(User))
"""
import os
import importlib
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy import create_engine, Engine
from contextlib import asynccontextmanager
from core.config import settings

# Global registry of database engines per app
_async_engines: Dict[str, AsyncEngine] = {}
_sync_engines: Dict[str, Engine] = {}


def discover_app_database(app_name: str) -> str:
    """
    Discover database URL for a specific app.
    
    Priority:
    1. Environment variable: <APP_NAME>_DATABASE_URL
    2. App's database.py: apps/<app_name>/database.py
    3. Default: DATABASE_URL from settings
    
    Args:
        app_name: Name of the app (e.g., 'auth', 'driver')
        
    Returns:
        Database URL string
        
    Example:
        >>> discover_app_database('auth')
        'postgresql://localhost:5432/auth_db'
    """
    # 1. Check environment variable
    env_key = f"{app_name.upper()}_DATABASE_URL"
    db_url = os.getenv(env_key)
    
    if db_url:
        print(f"   📌 Using {env_key} from environment")
        return db_url
    
    # 2. Check app's database.py
    try:
        apps_dir = settings.APPS_DIR
        module_path = f"{apps_dir}.{app_name}.database"
        db_module = importlib.import_module(module_path)
        
        if hasattr(db_module, 'DATABASE_URL'):
            print(f"   📌 Using DATABASE_URL from {module_path}")
            return db_module.DATABASE_URL
    except (ImportError, AttributeError):
        pass
    
    # 3. Fallback to default
    print(f"   📌 Using default DATABASE_URL for {app_name}")
    return settings.ASYNC_DATABASE_URI


def get_async_engine(app_name: str) -> AsyncEngine:
    """
    Get or create async engine for an app.
    
    Engines are cached and reused for performance.
    
    Args:
        app_name: Name of the app
        
    Returns:
        AsyncEngine instance
    """
    if app_name not in _async_engines:
        db_url = discover_app_database(app_name)
        _async_engines[app_name] = create_async_engine(
            db_url,
            echo=False,
            pool_pre_ping=True,
        )
    
    return _async_engines[app_name]


def get_sync_engine(app_name: str) -> Engine:
    """
    Get or create sync engine for an app.
    
    Engines are cached and reused for performance.
    
    Args:
        app_name: Name of the app
        
    Returns:
        Engine instance
    """
    if app_name not in _sync_engines:
        db_url = discover_app_database(app_name)
        # Convert async URL to sync
        sync_url = db_url.replace('+asyncpg', '').replace('+aiosqlite', '')
        _sync_engines[app_name] = create_engine(
            sync_url,
            echo=False,
            pool_pre_ping=True,
        )
    
    return _sync_engines[app_name]


@asynccontextmanager
async def get_app_session(app_name: str):
    """
    Get async database session for a specific app.
    
    Args:
        app_name: Name of the app
        
    Yields:
        AsyncSession instance
        
    Example:
        async with get_app_session('auth') as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
    """
    engine = get_async_engine(app_name)
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


def discover_all_app_databases() -> Dict[str, str]:
    """
    Discover all app databases.
    
    Returns:
        Dict mapping app names to their database URLs
        
    Example:
        >>> discover_all_app_databases()
        {
            'auth': 'postgresql://localhost:5432/auth_db',
            'driver': 'postgresql://localhost:5433/driver_db',
            'user': 'postgresql://localhost:5432/main_db'
        }
    """
    from core.utils.utils import get_apps
    
    apps = get_apps()
    app_databases = {}
    
    for app_name in apps.keys():
        db_url = discover_app_database(app_name)
        app_databases[app_name] = db_url
    
    return app_databases


def register_database(app_name: str, db_url: str):
    """
    Manually register a database for an app.
    
    This is useful for testing or custom configurations.
    
    Args:
        app_name: Name of the app
        db_url: Database URL
        
    Example:
        register_database('test_app', 'sqlite:///test.db')
    """
    # Create engines immediately
    _async_engines[app_name] = create_async_engine(db_url)
    sync_url = db_url.replace('+asyncpg', '').replace('+aiosqlite', '')
    _sync_engines[app_name] = create_engine(sync_url)


async def close_all_engines():
    """Close all database engines (cleanup)."""
    for engine in _async_engines.values():
        await engine.dispose()
    
    for engine in _sync_engines.values():
        engine.dispose()
    
    _async_engines.clear()
    _sync_engines.clear()
