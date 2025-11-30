"""
Modular Monolith Gateway
Mounts all services as sub-applications in a single process.
"""
from fastapi import FastAPI
import uvicorn

# Import service apps
# Note: Ensure 'services' is in your PYTHONPATH or this file is in the root
from services.auth_service.main import app as auth_app
# from services.user_service.main import app as user_app

app = FastAPI(
    title="Core Gateway",
    description="Modular Monolith Gateway mounting all services",
    version="1.0.0"
)

# Mount services
# Requests to /auth/... will be handled by auth_service
app.mount("/auth", auth_app)
# app.mount("/users", user_app)

@app.get("/")
def root():
    return {
        "message": "Gateway is running",
        "services": ["auth"]
    }

if __name__ == "__main__":
    uvicorn.run("main_gateway:app", host="0.0.0.0", port=8000, reload=True)
