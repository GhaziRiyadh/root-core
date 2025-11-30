"""
Auth Service - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.messaging.event_bus import get_event_bus
# from events.consumers import start_consumers

# Import routers
from routers import (
    auth_router,
    user_router,
    role_router,
    permission_router,
    group_router,
    userrole_router,
    usergroup_router,
    userpermission_router,
    grouprole_router,
    rolepermissions_router,
)

# Create FastAPI app
app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description="Authentication and Authorization microservice"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    """Start event consumers on startup."""
    print("Starting auth service...")
    # await start_consumers()
    print("Event consumers started")

@app.on_event("shutdown")
async def shutdown():
    """Stop event bus on shutdown."""
    print("Stopping auth service...")
    event_bus = get_event_bus()
    await event_bus.stop()
    print("Service stopped")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "auth-service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

# Include routers
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(user_router.router, prefix="/users", tags=["Users"])
app.include_router(role_router.router, prefix="/roles", tags=["Roles"])
app.include_router(permission_router.router, prefix="/permissions", tags=["Permissions"])
app.include_router(group_router.router, prefix="/groups", tags=["Groups"])
app.include_router(userrole_router.router, prefix="/user-roles", tags=["User Roles"])
app.include_router(usergroup_router.router, prefix="/user-groups", tags=["User Groups"])
app.include_router(userpermission_router.router, prefix="/user-permissions", tags=["User Permissions"])
app.include_router(grouprole_router.router, prefix="/group-roles", tags=["Group Roles"])
app.include_router(rolepermissions_router.router, prefix="/role-permissions", tags=["Role Permissions"])
