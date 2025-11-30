"""
Database configuration for auth service.
"""
# Service-specific database URL
DATABASE_URL = "postgresql://user:password@auth-db:5432/auth_db"

# Engine options (optional)
ENGINE_OPTIONS = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_pre_ping": True,
}
