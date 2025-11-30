"""
Service create command - generates a complete microservice structure.

This command creates everything needed for a microservice:
- Service directory structure
- Dockerfile
- docker-compose.yml
- Database configuration
- Kafka event handlers
- FastAPI application
- README.md
"""
import os
import typer
from core.bases.base_command import BaseCommand
from core.commands.utils import to_snake_case, write_file, ensure_package


class ServiceCreateCommand(BaseCommand):
    def execute(
        self,
        service_name: str = typer.Argument(..., help="Service name (e.g., 'auth', 'user')"),
        port: int = typer.Option(8000, help="Service port"),
        db_port: int = typer.Option(5432, help="Database port"),
    ):
        """
        Create a complete microservice structure.
        # Create configuration files
        self._create_env_files(service_dir, service_name_snake, port, db_port)
        self._create_docker_files(service_dir, service_name_snake, port, db_port)
        
        # Create application files
        self._create_main_file(service_dir, service_name_snake)
        self._create_database_file(service_dir, service_name_snake, db_port)
        
        # Create event handlers
        self._create_event_files(service_dir, service_name_snake)
        
        # Create README
        self._create_readme(service_dir, service_name_snake, port, db_port)
        
        # Create requirements
        self._create_requirements(service_dir)
        
        print(f"\nMicroservice created: {service_dir}")
        print(f"\nNext steps:")
        print(f"   1. cd {service_dir}")
        print(f"   2. Update .env with your configuration")
        print(f"   3. docker-compose up -d")
        print(f"   4. Access at http://localhost:{port}")
    
    def _create_structure(self, service_dir: str, service_name: str):
        """Create directory structure."""
        print("\nCreating directory structure...")
        
        directories = [
            service_dir,
            f"{service_dir}/models",
            f"{service_dir}/repositories",
            f"{service_dir}/services",
            f"{service_dir}/routers",
            f"{service_dir}/schemas",
            f"{service_dir}/events",
            f"{service_dir}/migrations",
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            ensure_package(directory)
        
        print(f"   Created {len(directories)} directories")
    
    def _create_env_files(self, service_dir: str, service_name: str, port: int, db_port: int):
        """Create .env and .env.example files."""
        print("\nCreating environment files...")
        
        env_content = f"""# Service Configuration
SERVICE_NAME={service_name}-service
SERVICE_PORT={port}

# Database
DATABASE_URL=postgresql://user:password@{service_name}-db:{db_port}/{service_name}_db
ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@{service_name}-db:{db_port}/{service_name}_db

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9093
KAFKA_CONSUMER_GROUP={service_name}-service-consumer

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1000

# Project Info
PROJECT_NAME="{service_name.title()} Service"
PROJECT_VERSION="1.0.0"
PROJECT_DESCRIPTION="{service_name.title()} microservice"
"""
        
        write_file(f"{service_dir}/.env.example", env_content)
        write_file(f"{service_dir}/.env", env_content)
        
        print("   Created .env and .env.example")
    
    def _create_docker_files(self, service_dir: str, service_name: str, port: int, db_port: int):
        """Create Dockerfile and docker-compose.yml."""
        print("\nCreating Docker files...")
        
        # Dockerfile
        dockerfile_content = """FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"""
        
        # docker-compose.yml
        compose_content = f"""version: '3.8'

services:
  {service_name}-service:
    build: .
    container_name: {service_name}-service
    ports:
      - "{port}:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@{service_name}-db:5432/{service_name}_db
      - ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@{service_name}-db:5432/{service_name}_db
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9093
    depends_on:
      - {service_name}-db
    networks:
      - microservices
    volumes:
      - .:/app
    restart: unless-stopped

  {service_name}-db:
    image: postgres:15
    container_name: {service_name}-db
    environment:
      POSTGRES_DB: {service_name}_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "{db_port}:5432"
    volumes:
      - {service_name}-db-data:/var/lib/postgresql/data
    networks:
      - microservices
    restart: unless-stopped

volumes:
  {service_name}-db-data:

networks:
  microservices:
    external: true
"""
        
        write_file(f"{service_dir}/Dockerfile", dockerfile_content)
        write_file(f"{service_dir}/docker-compose.yml", compose_content)
        
        print("   Created Dockerfile and docker-compose.yml")
    
    def _create_main_file(self, service_dir: str, service_name: str):
        """Create main.py FastAPI application."""
        print("\nCreating FastAPI application...")
        
        main_content = f'''"""
{service_name.title()} Service - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.messaging.event_bus import get_event_bus
from events.consumers import start_consumers

# Create FastAPI app
app = FastAPI(
    title="{service_name.title()} Service",
    version="1.0.0",
    description="{service_name.title()} microservice"
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
    print("Starting {service_name} service...")
    await start_consumers()
    print("Event consumers started")

@app.on_event("shutdown")
async def shutdown():
    """Stop event bus on shutdown."""
    print("Stopping {service_name} service...")
    event_bus = get_event_bus()
    await event_bus.stop()
    print("Service stopped")

@app.get("/")
async def root():
    """Root endpoint."""
    return {{
        "service": "{service_name}-service",
        "status": "running",
        "version": "1.0.0"
    }}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {{"status": "healthy"}}

# Include routers here
# from routers import example_router
# app.include_router(example_router.router)
'''
        
        write_file(f"{service_dir}/main.py", main_content)
        
        print("   Created main.py")
    
    def _create_database_file(self, service_dir: str, service_name: str, db_port: int):
        """Create database.py configuration."""
        print("\nCreating database configuration...")
        
        db_content = f'''"""
Database configuration for {service_name} service.
"""
# Service-specific database URL
DATABASE_URL = "postgresql://user:password@{service_name}-db:{db_port}/{service_name}_db"

# Engine options (optional)
ENGINE_OPTIONS = {{
    "pool_size": 10,
    "max_overflow": 20,
    "pool_pre_ping": True,
}}
'''
        
        write_file(f"{service_dir}/database.py", db_content)
        
        print("   Created database.py")
    
    def _create_event_files(self, service_dir: str, service_name: str):
        """Create Kafka event handlers."""
        print("\nCreating event handlers...")
        
        # Publishers
        publishers_content = f'''"""
Event publishers for {service_name} service.
"""
from core.messaging.event_bus import get_event_bus
from core.messaging.events import DomainEvent


async def publish_example_event(data: dict):
    """
    Publish an example event.
    
    Args:
        data: Event data
    """
    event_bus = get_event_bus()
    
    event = DomainEvent(
        event_type="{service_name}.example",
        service_name="{service_name}-service",
        data=data
    )
    
    await event_bus.publish("{service_name}.events", event)
'''
        
        # Consumers
        consumers_content = f'''"""
Event consumers for {service_name} service.
"""
from core.messaging.event_bus import get_event_bus
from core.messaging.events import BaseEvent


async def handle_{service_name}_event(event: BaseEvent):
    """
    Handle {service_name} events.
    
    Args:
        event: Received event
    """
    print(f"📨 Received event: {{event.event_type}}")
    print(f"   Data: {{event.data}}")
    
    # Add your event handling logic here
    if event.event_type == "{service_name}.example":
        # Handle example event
        pass


async def start_consumers():
    """Start all event consumers."""
    event_bus = get_event_bus()
    await event_bus.start()
    
    # Subscribe to topics
    await event_bus.subscribe(
        topics=["{service_name}.events"],
        handler=handle_{service_name}_event,
        group_id="{service_name}-service-consumer"
    )
    
    print(f"Subscribed to {service_name}.events")
'''
        
        write_file(f"{service_dir}/events/publishers.py", publishers_content)
        write_file(f"{service_dir}/events/consumers.py", consumers_content)
        
        print("   Created event publishers and consumers")
    
    def _create_readme(self, service_dir: str, service_name: str, port: int, db_port: int):
        """Create README.md."""
        print("\nCreating README...")
        
        readme_content = f"""# {service_name.title()} Service

Microservice for {service_name} functionality.

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Update .env with your configuration
```

### 2. Start Service

```bash
# Create Docker network (first time only)
docker network create microservices

# Start service and database
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Access Service

- **API**: http://localhost:{port}
- **Docs**: http://localhost:{port}/docs
- **Health**: http://localhost:{port}/health

## Development

### Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Migration message"

# Apply migrations
alembic upgrade head
```

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn main:app --reload --port {port}
```

## Architecture

```
{service_name}-service/
├── main.py              # FastAPI application
├── database.py          # Database configuration
├── models/              # Database models
├── repositories/        # Data access layer
├── services/            # Business logic
├── routers/             # API endpoints
├── schemas/             # Pydantic schemas
└── events/              # Kafka event handlers
    ├── publishers.py    # Event publishing
    └── consumers.py     # Event consuming
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SERVICE_NAME` | Service name | `{service_name}-service` |
| `SERVICE_PORT` | Service port | `{port}` |
| `DATABASE_URL` | Database connection | `postgresql://...` |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka servers | `kafka:9093` |

## API Endpoints

### Health Check
```bash
GET /health
```

### Root
```bash
GET /
```

## Events

### Published Events
- `{service_name}.example` - Example event

### Consumed Events
- `{service_name}.events` - {service_name.title()} events

## Docker

### Build Image
```bash
docker build -t {service_name}-service .
```

### Run Container
```bash
docker run -p {port}:8000 {service_name}-service
```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=.
```

## Deployment

### Kubernetes
```bash
kubectl apply -f k8s/
```

### Docker Swarm
```bash
docker stack deploy -c docker-compose.yml {service_name}
```

## Monitoring

- **Logs**: `docker-compose logs -f {service_name}-service`
- **Database**: `docker exec -it {service_name}-db psql -U user -d {service_name}_db`
- **Kafka**: Check Kafka UI at http://localhost:8080

## Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs {service_name}-service

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Database connection issues
```bash
# Check database is running
docker ps | grep {service_name}-db

# Test connection
docker exec -it {service_name}-db psql -U user -d {service_name}_db
```

## License

MIT
"""
        
        write_file(f"{service_dir}/README.md", readme_content)
        
        print("   Created README.md")
    
    def _create_requirements(self, service_dir: str):
        """Create requirements.txt."""
        print("\nCreating requirements.txt...")
        
        requirements_content = """# Core dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
alembic==1.12.1
asyncpg==0.29.0
psycopg2-binary==2.9.9

# Kafka
aiokafka==0.10.0

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
"""
        
        write_file(f"{service_dir}/requirements.txt", requirements_content)
        
        print("   Created requirements.txt")
