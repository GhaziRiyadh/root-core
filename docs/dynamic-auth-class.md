# Dynamic Auth Class System

## Overview

The authentication system has been refactored to use a class-based approach, allowing you to configure different authentication implementations via `settings.AUTH_CLASS`.

## Configuration

### Settings

Add to your `.env` file:

```bash
# Use the default auth implementation
AUTH_CLASS=core.security.DefaultAuth

# Or use a custom implementation
AUTH_CLASS=services.auth_service.auth.CustomAuth
```

### Config File

The setting is defined in `core/config.py`:

```python
AUTH_CLASS: str = EnvManager.get(
    "AUTH_CLASS", "core.security.DefaultAuth"
)
```

## Usage

### Basic Usage

The `auth()` function now returns a class instance instead of an `Auth` object:

```python
from core.security import auth

# Get current user
user = auth().user

# Get current token
token = auth().token

# Get full auth object
auth_obj = auth().auth_object
```

### Custom Auth Class

Create your own auth class by extending `BaseAuth`:

```python
# services/auth_service/auth.py
from core.security import BaseAuth, Auth
from typing import Optional, Dict, Any

class CustomAuth(BaseAuth):
    """Custom authentication implementation with additional features."""
    
    @property
    def user_id(self) -> Optional[int]:
        """Get the current user ID."""
        if self.user:
            return self.user.get("id")
        return None
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.user is not None
    
    @property
    def permissions(self) -> list:
        """Get user permissions."""
        if self.user:
            return self.user.get("permissions", [])
        return []
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        return permission in [p.get("action") for p in self.permissions]
```

Then configure it in `.env`:

```bash
AUTH_CLASS=services.auth_service.auth.CustomAuth
```

## API Reference

class DefaultAuth(BaseAuth):
    """Default authentication implementation."""
    pass

```

## Migration Guide

### Before (Function-based)

```python
from core.security import auth

# auth() returned an Auth object directly
current_auth = auth()
user = current_auth.user
token = current_auth.token
```

### After (Class-based)

```python
from core.security import auth

# auth() returns a BaseAuth instance
user = auth().user
token = auth().token
auth_obj = auth().auth_object  # Get the Auth object if needed
```

## Benefits

1. **Extensibility**: Easy to add custom auth logic per service
2. **Type Safety**: Better IDE support and type hints
3. **Flexibility**: Different services can use different auth implementations
4. **Backward Compatible**: Existing code using `auth().user` still works

## Example: Service-Specific Auth

```python
# services/admin_service/auth.py
from core.security import BaseAuth
from typing import Set, Optional

class AdminAuth(BaseAuth):
    """Admin-specific authentication with role checking."""
    
    @property
    def is_admin(self) -> bool:
        if self.user:
            roles = self.user.get("roles", [])
            return any(r.get("name") == "admin" for r in roles)
        return False
    
    def require_admin(self):
        if not self.is_admin:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
    
    def check_permissions(
        self,
        required_actions: Set[str],
        resource: str,
        app_name: Optional[str] = None
    ) -> bool:
        """Custom permission checking with admin bypass."""
        # Admins have all permissions
        if self.is_admin:
            return True
        
        # Otherwise use default permission checking
        return super().check_permissions(required_actions, resource, app_name)
```

Usage:

```python
from core.security import auth

# In admin service endpoints
def admin_only_endpoint():
    auth().require_admin()  # Raises 403 if not admin
    # ... admin logic

# The require_permissions decorator now uses auth().check_permissions()
# So custom auth classes can override permission logic
@require_permissions(PermissionAction.DELETE, resource="users")
async def delete_user(user_id: int):
    # This will use AdminAuth.check_permissions() if configured
    pass
```

## Notes

- The auth instance is a singleton per process
- The class is loaded dynamically based on `settings.AUTH_CLASS`
- Custom classes must inherit from `BaseAuth`
- The context is still managed via `contextvars` for async safety
