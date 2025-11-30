"""
App detector utility for auto-detecting which app a file belongs to.

This module provides automatic detection of the current app based on file paths,
enabling repositories and services to automatically use the correct database.

Example:
    # Auto-detect app from file path
    from core.utils.app_detector import get_current_app
    
    app_name = get_current_app(__file__)
    # Returns: 'auth' if file is in apps/auth/
"""
import os
from typing import Optional
from functools import lru_cache
from core.config import settings


@lru_cache(maxsize=128)
def get_current_app(file_path: str) -> Optional[str]:
    """
    Auto-detect which app a file belongs to based on its path.
    
    Args:
        file_path: Absolute path to the file (use __file__)
        
    Returns:
        App name if detected, None otherwise
        
    Example:
        >>> get_current_app('/path/to/apps/auth/repositories/user_repository.py')
        'auth'
        
        >>> get_current_app('/path/to/apps/driver/services/driver_service.py')
        'driver'
    """
    # Normalize path
    file_path = os.path.abspath(file_path)
    file_path = file_path.replace('\\', '/')
    
    # Get apps directory
    apps_dir = settings.APPS_DIR
    
    # Check if file is in apps directory
    if apps_dir in file_path:
        # Extract app name from path
        # Example: /path/to/apps/auth/repositories/file.py -> auth
        parts = file_path.split(f'{apps_dir}/')
        
        if len(parts) > 1:
            # Get the part after apps_dir
            after_apps = parts[1]
            # Get the first directory (app name)
            app_name = after_apps.split('/')[0]
            return app_name
    
    return None


def get_app_from_module(module_path: str) -> Optional[str]:
    """
    Extract app name from a module path.
    
    Args:
        module_path: Python module path (e.g., 'apps.auth.repositories.user_repository')
        
    Returns:
        App name if detected, None otherwise
        
    Example:
        >>> get_app_from_module('apps.auth.repositories.user_repository')
        'auth'
    """
    apps_dir = settings.APPS_DIR.replace('/', '.')
    
    if apps_dir in module_path:
        parts = module_path.split(f'{apps_dir}.')
        if len(parts) > 1:
            app_name = parts[1].split('.')[0]
            return app_name
    
    return None


def clear_cache():
    """Clear the app detection cache."""
    get_current_app.cache_clear()
