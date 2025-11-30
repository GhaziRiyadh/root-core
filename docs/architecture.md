# Core Architecture

The project follows a layered architecture to separate concerns and ensure scalability.

## Service Layer (`core/bases/base_service.py`)

The `BaseService` class contains the business logic. It sits between the API (Router) and the Data (Repository) layers.

### Responsibilities

- **Validation**: Validates input data before passing it to the repository.
- **Business Rules**: Enforces business logic.
- **Response Formatting**: Formats data for the API response.
- **Error Handling**: Catches repository errors and raises service-level exceptions.

### Key Methods

- **`create`, `update`, `soft_delete`, `restore`, `force_delete`**: Standard CRUD operations with validation hooks.
- **`get_by_id`, `get_all`, `get_list`**: Retrieval methods.
- **`bulk_create`, `bulk_update`**: Bulk operations.
- **`_validate_create`, `_validate_update`, `_validate_delete`**: Hooks for custom validation logic.

## Exception Handling (`core/exceptions.py`)

The project uses a centralized exception handling mechanism. Custom exceptions are defined in `core/exceptions.py` and mapped to appropriate HTTP status codes.

### Common Exceptions

- **`NotFoundException`** (404): Resource not found.
- **`ValidationException`** (422): Data validation failed.
- **`UnauthorizedException`** (401): Authentication failed.
- **`ForbiddenException`** (403): Permission denied.
- **`ServiceException`** (500): Internal server error.

## Middleware (`core/bases/base_middleware.py`)

The `BaseMiddleware` class allows you to intercept requests and responses.

### Usage

Inherit from `BaseMiddleware` and implement the `dispatch` method.

```python
class MyMiddleware(BaseMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Pre-processing
        response = await call_next(request)
        # Post-processing
        return response
```
