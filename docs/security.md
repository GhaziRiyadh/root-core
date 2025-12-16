# Security System Documentation

The Core Project now uses a swappable Security system, allowing you to customize authentication and authorization logic by providing your own implementation of the `BaseSecurity` class.

## Configuration

To use a custom security class, update your `.env` file or environment variables:

```env
SECURITY_CLASS=path.to.your.CustomSecurity
```

The default value is `core.apps.auth.utils.security.DefaultSecurity`.

## Architecture

The system relies on an abstract base class `BaseSecurity` defined in `core.apps.auth.utils.security`.

### BaseSecurity Interface

Any custom security class must inherit from `BaseSecurity` and implement the following methods:

- `verify_password(self, plain_password: str, hashed_password: str) -> bool`
- `get_password_hash(self, password: str) -> str`
- `get_user(self, username: Optional[str]) -> Optional[Any]`
- `authenticate_user(self, username: str, password: str) -> Optional[Any]`
- `create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str`
- `get_current_user(self, token: str) -> Any`
- `get_current_user_or_none(self, request: Request) -> Any`
- `auth(self) -> Auth`

## Custom Implementation Example

Here is an example of how to create a custom security class.

1. **Create your class file**, e.g., `apps/my_app/security_impl.py`.

```python
from typing import Any, Optional
from datetime import timedelta
from fastapi import Request
from core.apps.auth.utils.security import BaseSecurity, Auth, DefaultSecurity

class LDAPSecurity(DefaultSecurity):
    """
    Example custom security that overrides authentication to use LDAP
    (hypothetically), but keeps default token handling.
    """

    async def authenticate_user(self, username: str, password: str) -> Optional[Any]:
        # Custom logic here, e.g., call LDAP service
        print(f"Authenticating {username} via Custom LDAP...")
        
        # For demonstration, we just call super (default logic)
        return await super().authenticate_user(username, password)

    # You can override other methods as needed, or inherit from BaseSecurity
    # directly if you want to replace everything.
```

2. **Update Configuration**:

```env
SECURITY_CLASS=apps.my_app.security_impl.LDAPSecurity
```

## Internal Utils

The module `core.apps.auth.utils.utils` now acts as a proxy. You should continue to import functions from there in your code:

```python
from core.apps.auth.utils.utils import get_current_user, verify_password

# These calls are automatically routed to your configured Security Class
```
