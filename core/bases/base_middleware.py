from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class BaseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 🔹 Place pre-processing logic here (before the request)
        # Example: print request info
        print(f"➡️ {request.method} {request.url.path}")

        response = await call_next(request)

        # 🔹 Post-processing logic (after response)
        response.headers["X-Custom-Middleware"] = "BaseMiddleware"
        print(f"⬅️ {response.status_code}")

        return response
