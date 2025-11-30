# Security Module Refactoring

## Overview

The `core/security.py` file has been split into a modular package structure for better organization and maintainability.

## New Structure

```
core/security/
├── __init__.py          # Package exports
├── models.py            # Auth data models (Token, TokenData, Auth)
├── cache.py             # Auth caching logic
├── password.py          # Password hashing utilities
├── tokens.py            # JWT token creation
├── auth_class.py        # Auth class system (BaseAuth, DefaultAuth, auth())
├── user.py              # User authentication and retrieval
└── permissions.py       # Permission decorators
```

## File Breakdown

### `models.py`

- `Token`: JWT token response model
- `TokenData`: JWT token payload
- `Auth`: Authentication context

### `cache.py`

- `CURRENT_AUTH`: Context variable for current auth
- `get_cached_auth()`: Get cached authentication
- `set_cached_auth()`: Cache authentication

### `password.py`

- `verify_password()`: Verify password against hash
- `get_password_hash()`: Hash a password

### `tokens.py`

- `create_access_token()`: Create JWT access token

### `auth_class.py`

- `BaseAuth`: Base authentication class
- `DefaultAuth`: Default implementation
- `auth()`: Get current auth instance
- `get_auth_class()`: Load configured auth class

### `user.py`

- `get_user()`: Get user by username
- `authenticate_user()`: Authenticate with username/password
- `get_current_user()`: Get current user from JWT
- `get_current_user_or_none()`: Get current user or None
- `get_current_active_user()`: Get current user or raise 401

### `permissions.py`

- `require_permissions()`: Permission decorator

## Migration Guide

### No Changes Required

All imports remain the same:

```python
# Before (single file)
from core.security import (
    auth,
    BaseAuth,
    DefaultAuth,
    verify_password,
    get_password_hash,
    create_access_token,
    get_user,
    authenticate_user,
    get_current_user,
    require_permissions,
)

# After (package) - SAME IMPORTS!
from core.security import (
    auth,
    BaseAuth,
    DefaultAuth,
    verify_password,
    get_password_hash,
    create_access_token,
    get_user,
    authenticate_user,
    get_current_user,
    require_permissions,
)
```

The `__init__.py` file re-exports everything, so existing code continues to work without modification.

## Benefits

1. **Better Organization**: Related code is grouped together
2. **Easier Navigation**: Smaller files are easier to understand
3. **Maintainability**: Changes are isolated to specific modules
4. **Testing**: Easier to test individual components
5. **Extensibility**: Easier to add new features without cluttering a single file

## Old File

The original `core/security.py` can be safely deleted after verifying all imports work correctly.

## Verification

Run your tests to ensure everything still works:

```bash
# Test imports
poetry run python -c "from core.security import auth, BaseAuth, require_permissions; print('✓ Imports work')"

# Run your test suite
poetry run pytest
```
