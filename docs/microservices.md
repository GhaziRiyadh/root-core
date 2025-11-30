# Microservices Architecture Guide

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Service Structure](#service-structure)
4. [Database Management](#database-management)
5. [Event-Driven Communication](#event-driven-communication)
6. [Service Development](#service-development)
7. [Deployment](#deployment)
8. [Best Practices](#best-practices)

## Overview

This framework supports building microservices architecture with:

- **Independent Services**: Each service is a separate FastAPI application
- **Database Per Service**: Each service has its own database
- **Event-Driven**: Services communicate via Kafka
- **Docker Ready**: Each service has its own Dockerfile
- **Auto-Discovery**: Dynamic database and command discovery

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (Optional)                   │
│                  - Request routing                           │
│                  - Authentication                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Kafka Event Bus                         │
│  Topics: user.events, order.events, notification.events     │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Auth Service │ │ User Service │ │Driver Service│ │ Other Services│
│ Port: 8001   │ │ Port: 8002   │ │ Port: 8003   │ │ Port: 800X   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Auth DB    │ │   User DB    │ │  Driver DB   │ │  Service DB  │
│  Port: 5432  │ │  Port: 5433  │ │  Port: 5434  │ │  Port: 543X  │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## Service Structure

Each microservice follows this structure:

```
services/
└── auth-service/
    ├── .env                    # Service-specific environment variables
    ├── .env.example            # Environment template
    ├── Dockerfile              # Docker image definition
    ├── docker-compose.yml      # Service + database setup
    ├── main.py                 # FastAPI application entry point
    ├── README.md               # Service documentation
    ├── requirements.txt        # Python dependencies
    ├── alembic.ini             # Migration configuration
    ├── migrations/             # Database migrations
    │   ├── env.py
    │   └── versions/
    ├── models/                 # Database models
    │   ├── __init__.py
    │   └── user.py
    ├── repositories/           # Data access layer
    │   ├── __init__.py
    │   └── user_repository.py
    ├── services/               # Business logic
    │   ├── __init__.py
    │   └── user_service.py
    ├── routers/                # API endpoints
    │   ├── __init__.py
    │   └── user_router.py
    ├── schemas/                # Pydantic schemas
    │   ├── __init__.py
    │   └── user.py
    ├── events/                 # Kafka event handlers
    │   ├── __init__.py
    │   ├── publishers.py       # Event publishing
    │   └── consumers.py        # Event consuming
    └── database.py             # Database configuration
```

## Database Management

### Database Per Service

Each service has its own database:

**Configuration** (`.env`):

```env
# Service name
SERVICE_NAME=auth-service

# Database
DATABASE_URL=postgresql://user:pass@auth-db:5432/auth_db
ASYNC_DATABASE_URL=postgresql+asyncpg://user:pass@auth-db:5432/auth_db

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9093
```

**Database Configuration** (`database.py`):

```python
DATABASE_URL = "postgresql://user:pass@auth-db:5432/auth_db"
```

### Migrations

Each service has its own migrations:

```bash
# Initialize Alembic
alembic init migrations

# Create migration
python cli.py db-migrate "Add user table"

# Apply migrations
python cli.py db-upgrade
```

**migrations/env.py**:

```python
import os
from core.migrations.base_env import run_migrations_offline, run_migrations_online
from alembic import context

# Service-specific migrations
app_name = os.getenv('ALEMBIC_APP', 'auth')

if context.is_offline_mode():
    run_migrations_offline(app_name)
else:
    run_migrations_online(app_name)
```

## Event-Driven Communication

### Publishing Events

**events/publishers.py**:

```python
from core.messaging.event_bus import get_event_bus
from core.messaging.events import DomainEvent

async def publish_user_created(user_id: str, email: str):
    \"\"\"Publish user created event.\"\"\"
    event_bus = get_event_bus()
    
    event = DomainEvent(
        event_type="user.created",
        service_name="auth-service",
        data={
            "user_id": user_id,
            "email": email
        },
        aggregate_id=user_id,
        aggregate_type="User"
    )
    
    await event_bus.publish("user.events", event, key=user_id)
```

### Consuming Events

**events/consumers.py**:

```python
from core.messaging.event_bus import get_event_bus
from core.messaging.events import BaseEvent

async def handle_user_event(event: BaseEvent):
    \"\"\"Handle user events.\"\"\"
    if event.event_type == "user.created":
        user_id = event.data.get("user_id")
        # Handle user creation
        print(f"User created: {user_id}")

async def start_consumers():
    \"\"\"Start event consumers.\"\"\"
    event_bus = get_event_bus()
    await event_bus.start()
    
    # Subscribe to topics
    await event_bus.subscribe(
        topics=["user.events"],
        handler=handle_user_event,
        group_id="auth-service-consumer"
    )
```

## Service Development

### Creating a New Service

```bash
# Generate service structure
python cli.py service-create auth

# This creates:
# - services/auth-service/ directory
# - Dockerfile
# - docker-compose.yml
# - All necessary files
```

### Service Entry Point

**main.py**:

```python
from fastapi import FastAPI
from core.app import CoreApp
from core.messaging.event_bus import get_event_bus
from events.consumers import start_consumers

# Create FastAPI app
core_app = CoreApp(
    title="Auth Service",
    version="1.0.0",
    description="Authentication and authorization service"
)
app = core_app.get_app()

@app.on_event("startup")
async def startup():
    \"\"\"Start event consumers on startup.\"\"\"
    await start_consumers()

@app.on_event("shutdown")
async def shutdown():
    \"\"\"Stop event bus on shutdown.\"\"\"
    event_bus = get_event_bus()
    await event_bus.stop()

# Include routers
from routers import user_router
app.include_router(user_router.router)
```

### Docker Configuration

**Dockerfile**:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  auth-service:
    build: .
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@auth-db:5432/auth_db
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9093
    depends_on:
      - auth-db
      - kafka
    networks:
      - microservices

  auth-db:
    image: postgres:15
    environment:
      POSTGRES_DB: auth_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - auth-db-data:/var/lib/postgresql/data
    networks:
      - microservices

volumes:
  auth-db-data:

networks:
  microservices:
    external: true
```

## Deployment

### Local Development

```bash
# Start Kafka (from root)
docker-compose -f docker-compose.kafka.yml up -d

# Create network
docker network create microservices

# Start service
cd services/auth-service
docker-compose up -d

# View logs
docker-compose logs -f auth-service
```

### Production Deployment

**Kubernetes** (recommended):

```yaml
# k8s/auth-service/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: your-registry/auth-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: auth-db-secret
              key: url
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "kafka:9092"
```

## Best Practices

### 1. Database Isolation

- ✅ Each service has its own database
- ✅ No shared tables between services
- ❌ Don't access other service's databases directly

### 2. Event-Driven Communication

- ✅ Use Kafka events for inter-service communication
- ✅ Make event handlers idempotent
- ✅ Version your events
- ❌ Don't make synchronous HTTP calls between services (use events)

### 3. Data Consistency

- ✅ Accept eventual consistency
- ✅ Use saga pattern for distributed transactions
- ✅ Implement compensation logic
- ❌ Don't expect immediate consistency

### 4. Service Independence

- ✅ Each service can be deployed independently
- ✅ Each service has its own CI/CD pipeline
- ✅ Services can use different tech stacks
- ❌ Don't create tight coupling between services

### 5. Monitoring & Observability

- ✅ Implement distributed tracing
- ✅ Centralized logging (ELK stack)
- ✅ Metrics collection (Prometheus)
- ✅ Health check endpoints

### 6. API Design

- ✅ Version your APIs (v1, v2)
- ✅ Use API Gateway for external access
- ✅ Implement rate limiting
- ✅ Document with OpenAPI/Swagger

## Common Patterns

### Saga Pattern (Distributed Transactions)

```python
# Order Service
async def create_order(order_data):
    # 1. Create order
    order = await order_repository.create(order_data)
    
    # 2. Publish event
    await publish_event("order.created", order)
    
    # 3. Wait for confirmation events
    # - payment.processed
    # - inventory.reserved
    
    # 4. If all confirmed, publish order.confirmed
    # 5. If any failed, publish order.cancelled and compensate
```

### CQRS (Command Query Responsibility Segregation)

```python
# Write Model (Command)
class CreateUserCommand:
    async def execute(self, user_data):
        user = await user_repository.create(user_data)
        await publish_event("user.created", user)
        return user

# Read Model (Query)
class UserQueryService:
    async def get_user(self, user_id):
        # Read from optimized read database
        return await read_db.get_user(user_id)
```

### Circuit Breaker

```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
async def call_external_service():
    # If this fails 5 times, circuit opens
    # After 60 seconds, circuit tries again
    pass
```

## Troubleshooting

### Service Can't Connect to Database

```bash
# Check database is running
docker ps | grep db

# Check connection string
echo $DATABASE_URL

# Test connection
docker exec -it auth-db psql -U user -d auth_db
```

### Events Not Being Consumed

```bash
# Check Kafka is running
docker ps | grep kafka

# Check consumer group
docker exec -it kafka kafka-consumer-groups --bootstrap-server localhost:9092 --list

# View topic messages
docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic user.events --from-beginning
```

### Service Won't Start

```bash
# Check logs
docker-compose logs auth-service

# Check environment variables
docker-compose config

# Rebuild image
docker-compose build --no-cache
```

## Next Steps

1. **Create Your First Service**: Use `python cli.py service-create <name>`
2. **Define Your Events**: Plan event schema and topics
3. **Implement Business Logic**: Add models, services, and routers
4. **Setup CI/CD**: Automate testing and deployment
5. **Monitor**: Setup logging, metrics, and tracing

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Microservices Patterns](https://microservices.io/patterns/)
