# Unified Security Manager

## Overview

All security functionality is now contained in a single `SecurityManager` class that can be easily extended and overridden.

## Benefits

1. **Single Class**: All security logic in one place
2. **Easy to Override**: Extend `SecurityManager` and override any method
3. **Clean API**: Simple, consistent interface
4. **Backward Compatible**: Existing imports still work
5. **Service-Specific**: Each service can have its own security implementation

## Usage

### Basic Usage

```python
from core.security_manager import security

# Access current user
user = security().user

# Check permissions
has_perm = security().check_permissions({"read"}, "users")

# Create token
token = security().create_access_token({"sub": "username"})
```

### Custom Security Class

```python
# services/admin_service/security.py
from core.security_manager import SecurityManager
from typing import Set, Optional

class AdminSecurity(SecurityManager):
    """Custom security for admin service."""
    
    @property
    def is_admin(self) -> bool:
        """Check if current user is admin."""
        if self.user:
            roles = self.user.get("roles", [])
            return any(r.get("name") == "admin" for r in roles)
        return False
    
    def check_permissions(
        self,
        required_actions: Set[str],
        resource: str,
        app_name: Optional[str] = None
    ) -> bool:
        """Admins bypass all permission checks."""
        if self.is_admin:
            return True
        return super().check_permissions(required_actions, resource, app_name)
    
    async def get_user(self, username: Optional[str]):
        """Custom user retrieval with admin-specific logic."""
        user = await super().get_user(username)
        if user:
            # Add admin-specific data
            user["admin_metadata"] = await self._get_admin_metadata(user)
        return user
    
    async def _get_admin_metadata(self, user):
        """Get admin-specific metadata."""
        # Custom logic here
        return {"last_admin_action": "..."}
```

Configure in `.env`:

```bash
AUTH_CLASS=services.admin_service.security.AdminSecurity
```

## All Overridable Methods

### Authentication

- `get_user(username)` - Get user by username
- `authenticate_user(username, password)` - Authenticate user
- `get_current_user(token)` - Get user from JWT
- `get_current_user_or_none(request)` - Get user or None
- `get_current_active_user()` - Get user or raise 401

### Authorization

- `check_permissions(actions, resource, app_name)` - Check permissions
- `_get_user_permissions(user, resource, app_name)` - Extract permissions

### Password

- `verify_password(plain, hashed)` - Verify password
- `get_password_hash(password)` - Hash password

### Tokens

- `create_access_token(data, expires_delta)` - Create JWT

### Cache

- `get_cached_auth(token)` - Get cached auth
- `set_cached_auth(token, auth)` - Cache auth

## Migration from Old System

### Before (Multiple Files)

```python
from core.security import (
    auth,
    verify_password,
    create_access_token,
    require_permissions,
)
```

### After (Single Class)

```python
from core.security_manager import (
    security,  # or auth() for backward compat
    verify_password,  # convenience function
    create_access_token,  # convenience function
    require_permissions,  # convenience function
)

# Or use the class directly
from core.security_manager import security

user = security().user
security().check_permissions(...)
```

## Example: Multi-Tenant Security

```python
class MultiTenantSecurity(SecurityManager):
    """Security with tenant isolation."""
    
    @property
    def tenant_id(self) -> Optional[int]:
        """Get current tenant ID."""
        if self.user:
            return self.user.get("tenant_id")
        return None
    
    async def get_user(self, username: Optional[str]):
        """Get user with tenant filtering."""
        user = await super().get_user(username)
        if user and user.get("tenant_id") != self.tenant_id:
            return None  # User from different tenant
        return user
    
    def check_permissions(self, required_actions, resource, app_name=None):
        """Check permissions with tenant scope."""
        # Only check permissions within current tenant
        if not self.tenant_id:
            return False
        return super().check_permissions(required_actions, f"{resource}:{self.tenant_id}", app_name)
```

## Configuration

Update `core/config.py`:

```python
AUTH_CLASS: str = EnvManager.get(
    "AUTH_CLASS", "core.security_manager.SecurityManager"
)
```

Update `.env`:

```bash
# Use default
AUTH_CLASS=core.security_manager.SecurityManager

# Or custom
AUTH_CLASS=services.auth_service.security.CustomSecurity
```

## Complete Example

```python
# services/api_service/security.py
from core.security_manager import SecurityManager
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

class APISecurity(SecurityManager):
    """API-specific security with rate limiting and logging."""
    
    def __init__(self):
        super().__init__()
        self.rate_limiter = RateLimiter()
    
    async def get_current_user(self, token: str):
        """Get user with rate limiting."""
        # Check rate limit
        if not self.rate_limiter.check(token):
            raise HTTPException(429, "Rate limit exceeded")
        
        # Log access
        logger.info(f"Token access: {token[:10]}...")
        
        return await super().get_current_user(token)
    
    def check_permissions(self, required_actions, resource, app_name=None):
        """Check permissions with audit logging."""
        result = super().check_permissions(required_actions, resource, app_name)
        
        # Audit log
        logger.info(f"Permission check: user={self.user.get('username')}, "
                   f"resource={resource}, actions={required_actions}, "
                   f"result={result}")
        
        return result
```

## Notes

- The `SecurityManager` class is a singleton per process
- All methods can be overridden
- The class is loaded dynamically based on `settings.AUTH_CLASS`
- Backward compatible with existing `auth()` function
- All convenience functions delegate to the global `security()` instance
