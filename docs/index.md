# Core Framework Documentation

Welcome to the Core Framework documentation. This framework provides a foundation for building microservices with FastAPI, Kafka, and PostgreSQL.

## Quick Start

### Create a New Microservice

```bash
# Generate complete microservice structure
python cli.py service-create auth --port 8001 --db-port 5433

# Navigate to service
cd services/auth-service

# Start service and database
docker-compose up -d
```

### Initialize Database

```bash
# Initialize all app databases
python cli.py db-init --all-apps

# Initialize specific app
python cli.py db-init --app auth

# List discovered databases
python cli.py db-list
```

## Core Guides

### 📚 [Microservices Architecture](microservices.md)

Complete guide to building microservices:

- Architecture overview
- Service structure
- Database per service
- Event-driven communication with Kafka
- Docker & Kubernetes deployment
- Best practices

### 🗄️ [Database Management](database-commands.md)

Database commands and multi-database support:

- `db-init` - Create and initialize databases
- `db-migrate` - Generate migrations
- `db-upgrade` / `db-downgrade` - Apply/rollback migrations
- `db-list` - List all app databases

### 📡 [Kafka Setup](kafka-setup.md)

Event-driven messaging with Kafka:

- Local Kafka setup with Docker
- Publishing and consuming events
- Event types and schemas
- Topic naming conventions

### 🔄 [Migrations](migrations.md)

Database migration management:

- Auto-discovery of models
- App-specific migrations
- Alembic integration

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Kafka Event Bus                         │
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
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## Key Features

✅ **Microservices Ready** - Each service is independent with its own database  
✅ **Event-Driven** - Services communicate via Kafka  
✅ **Auto-Discovery** - Dynamic database and command discovery  
✅ **Docker Ready** - Complete Docker setup for each service  
✅ **Database Per Service** - Isolated data with automatic migrations  
✅ **CLI Tools** - Powerful commands for service and database management  

## CLI Commands

### Service Management

```bash
# Create new microservice
python cli.py service-create <name> [--port PORT] [--db-port DB_PORT]
```

### Database Management

```bash
# Initialize databases
python cli.py db-init [--app NAME] [--all-apps]

# Create migration
python cli.py db-migrate "Migration message"

# Apply migrations
python cli.py db-upgrade

# List databases
python cli.py db-list
```

### App Management

```bash
# Create app (legacy - use service-create for microservices)
python cli.py app-create <name>

# List apps
python cli.py list-apps
```

## Development Workflow

### 1. Create Service

```bash
python cli.py service-create payment --port 8004 --db-port 5435
```

### 2. Configure Environment

```bash
cd services/payment-service
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Infrastructure

```bash
# Start Kafka (from project root)
docker-compose -f docker-compose.kafka.yml up -d

# Create Docker network
docker network create microservices
```

### 4. Start Service

```bash
# From service directory
docker-compose up -d
```

### 5. Develop

```bash
# Add models, services, routers
# Publish and consume events
# Test endpoints at http://localhost:8004/docs
```

## Project Structure

```
root-core/
├── core/                      # Core framework
│   ├── messaging/             # Kafka integration
│   ├── migrations/            # Base migration environment
│   ├── commands/              # CLI commands
│   └── database_registry.py   # Multi-database support
├── services/                  # Microservices
│   ├── auth-service/
│   ├── user-service/
│   └── ...
├── apps/                      # Legacy apps (migrate to services)
├── docs/                      # Documentation
└── cli.py                     # CLI entry point
```

## Best Practices

1. **Database Isolation** - Each service owns its data
2. **Event-Driven** - Use Kafka for inter-service communication
3. **Idempotent Handlers** - Make event handlers idempotent
4. **Version APIs** - Use versioning (v1, v2) for APIs
5. **Health Checks** - Implement `/health` endpoints
6. **Monitoring** - Add logging, metrics, and tracing

## Resources

- [Microservices Guide](microservices.md) - Complete architecture guide
- [Database Commands](database-commands.md) - Database management
- [Kafka Setup](kafka-setup.md) - Event messaging setup
- [Migrations](migrations.md) - Database migrations

## Support

For issues or questions, refer to the documentation or check the project repository.
