"""
Simplified Modular Monolith Gateway Demo
Demonstrates app.mount() without requiring all dependencies
"""
from fastapi import FastAPI
import uvicorn

# Create a simplified auth service app
auth_app = FastAPI(title="Auth Service")

@auth_app.get("/")
def auth_root():
    return {"service": "auth", "status": "running"}

@auth_app.get("/health")
def auth_health():
    return {"status": "healthy"}

@auth_app.get("/users")
def auth_users():
    return {"users": ["admin", "user1", "user2"]}

# Create a simplified user service app
user_app = FastAPI(title="User Service")

@user_app.get("/")
def user_root():
    return {"service": "users", "status": "running"}

@user_app.get("/health")
def user_health():
    return {"status": "healthy"}

@user_app.get("/list")
def user_list():
    return {"profiles": ["profile1", "profile2"]}

# Create main gateway
app = FastAPI(
    title="Core Gateway",
    description="Modular Monolith Gateway - Demo",
    version="1.0.0"
)

# Mount services
app.mount("/auth", auth_app)
app.mount("/users", user_app)

@app.get("/")
def root():
    return {
        "message": "✅ Modular Monolith Gateway is running!",
        "architecture": "app.mount() - All services in one process",
        "services": {
            "auth": "http://localhost:8080/auth/",
            "users": "http://localhost:8080/users/"
        },
        "endpoints": {
            "auth": [
                "GET /auth/ - Service info",
                "GET /auth/health - Health check",
                "GET /auth/users - List users"
            ],
            "users": [
                "GET /users/ - Service info",
                "GET /users/health - Health check",
                "GET /users/list - List profiles"
            ]
        }
    }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Modular Monolith Gateway Starting...")
    print("="*60)
    print("\n📍 Gateway URL: http://localhost:8080")
    print("\n📦 Mounted Services:")
    print("   • Auth Service:  http://localhost:8080/auth/")
    print("   • User Service:  http://localhost:8080/users/")
    print("\n💡 Try these endpoints:")
    print("   curl http://localhost:8080/")
    print("   curl http://localhost:8080/auth/users")
    print("   curl http://localhost:8080/users/list")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run("main_gateway_demo:app", host="0.0.0.0", port=8080, reload=True)
