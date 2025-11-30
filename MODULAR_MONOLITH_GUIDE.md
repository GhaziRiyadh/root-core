# Modular Monolith with `app.mount()`

## Overview

Instead of running each service in separate Docker containers, you can mount all services as sub-applications in a single FastAPI gateway. This creates a **Modular Monolith** architecture.

## Architecture Comparison

### Microservices (Docker)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ auth-service│     │ user-service│     │driver-service│
│   :8001     │     │   :8002     │     │   :8003     │
│  + auth-db  │     │  + user-db  │     │ + driver-db │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Modular Monolith (app.mount)

```
┌────────────────────────────────────────┐
│         Gateway (:8000)                │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │/auth     │ │/users    │ │/drivers│ │
│  │service   │ │service   │ │service │ │
│  └──────────┘ └──────────┘ └────────┘ │
└────────────────────────────────────────┘
         │           │           │
    ┌────┴───┐  ┌────┴───┐  ┌────┴───┐
    │auth-db │  │user-db │  │driver-db│
    └────────┘  └────────┘  └─────────┘
```

## Implementation

### 1. Gateway File (`main_gateway.py`)

```python
from fastapi import FastAPI
import uvicorn

# Import service apps
from services.auth_service.main import app as auth_app
from services.user_service.main import app as user_app
from services.driver_service.main import app as driver_app

app = FastAPI(
    title="Core Gateway",
    description="Modular Monolith Gateway",
    version="1.0.0"
)

# Mount services at different paths
app.mount("/auth", auth_app)
app.mount("/users", user_app)
app.mount("/drivers", driver_app)

@app.get("/")
def root():
    return {
        "message": "Gateway is running",
        "services": ["auth", "users", "drivers"]
    }

if __name__ == "__main__":
    uvicorn.run("main_gateway:app", host="0.0.0.0", port=8000, reload=True)
```

### 2. Running the Gateway

```bash
# Start the gateway
python main_gateway.py

# Or with uvicorn directly
uvicorn main_gateway:app --reload --port 8000
```

### 3. API Endpoints

All service endpoints are now accessible through the gateway:

```bash
# Auth service endpoints
GET  http://localhost:8000/auth/
GET  http://localhost:8000/auth/health
POST http://localhost:8000/auth/login
GET  http://localhost:8000/auth/users/

# User service endpoints
GET  http://localhost:8000/users/
GET  http://localhost:8000/users/health
GET  http://localhost:8000/users/list

# Driver service endpoints
GET  http://localhost:8000/drivers/
GET  http://localhost:8000/drivers/health
```

## Pros and Cons

### ✅ Advantages of Modular Monolith

1. **Simpler Deployment**: Single process to deploy and manage
2. **Easier Development**: No need for Docker, Kafka, or service discovery
3. **Shared Resources**: Can share database connections, caching, etc.
4. **Faster Communication**: In-process calls instead of HTTP/gRPC
5. **Lower Resource Usage**: One Python process instead of multiple containers
6. **Easier Debugging**: Single process to debug and trace

### ❌ Disadvantages

1. **No Independent Scaling**: Can't scale services separately
2. **Shared Failure Domain**: If one service crashes, all crash
3. **No Technology Diversity**: All services must use Python/FastAPI
4. **Deployment Coupling**: Must redeploy everything for any change
5. **Resource Contention**: Services compete for CPU/memory in same process
6. **Database Coupling**: Still need separate databases but harder to enforce boundaries

## When to Use Each Approach

### Use Modular Monolith When

- **Development/Testing**: Faster iteration during development
- **Small Teams**: Easier to manage with limited DevOps resources
- **Low Traffic**: Don't need independent scaling
- **Prototyping**: Validating architecture before full microservices
- **Monorepo**: All code in one repository anyway

### Use True Microservices (Docker) When

- **Production**: Need reliability and independent scaling
- **High Traffic**: Different services have different load patterns
- **Large Teams**: Multiple teams owning different services
- **Technology Diversity**: Want to use different languages/frameworks
- **Independent Deployment**: Need to deploy services separately
- **Fault Isolation**: Critical that one service failure doesn't affect others

## Migration Path

You can start with a Modular Monolith and migrate to Microservices:

1. **Phase 1**: Develop with `app.mount()` for speed
2. **Phase 2**: Ensure services are truly independent (separate DBs, no direct imports)
3. **Phase 3**: Add Docker configs to each service
4. **Phase 4**: Deploy services independently when needed

## Fixed Circular Dependency Issue

During implementation, we encountered a circular import issue:

**Problem**: `core.bases.base_repository` imported from `core.apps.auth.utils.utils`, which created a cycle when `core.apps.auth` routers imported `CRUDApi`.

**Solution**: Created `core/security.py` to centralize authentication logic:

- Moved `get_current_active_user`, `require_permissions`, and `auth()` to `core/security.py`
- Updated `core/bases/base_router.py` to import from `core.security`
- Updated `core/bases/base_repository.py` to import from `core.security`

This breaks the cycle by ensuring core modules don't depend on app-specific code.

## Recommendation

For your use case, I recommend:

**Development**: Use `app.mount()` (Modular Monolith)

- Faster development iteration
- Easier debugging
- Simpler local setup

**Production**: Use Docker (True Microservices)

- Better scalability
- Fault isolation
- Independent deployment
- Production-ready architecture

The code structure supports both approaches, so you can switch between them as needed!
