# Microservices Architecture with Kafka - Implementation Plan

## Goal Description

Transform the current monolithic FastAPI core framework into a microservices architecture with Kafka as the event broker for inter-service communication. This will enable:

- Independent deployment and scaling of services
- Event-driven architecture for loose coupling
- Asynchronous communication between services
- Better fault isolation and resilience

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (FastAPI)                    │
│                  - Request routing                           │
│                  - Authentication                            │
│                  - Rate limiting                             │
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
│              │ │              │ │              │ │              │
│ - JWT Auth   │ │ - User CRUD  │ │ - Driver Mgmt│ │ - Custom     │
│ - Permissions│ │ - Profiles   │ │ - Tracking   │ │   Logic      │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Auth DB    │ │   User DB    │ │  Driver DB   │ │  Service DB  │
│  (Postgres)  │ │  (Postgres)  │ │  (Postgres)  │ │  (Postgres)  │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## Phase 1: Core Infrastructure Setup

### 1.1 Kafka Integration

**Files to create:**

- `core/messaging/kafka_client.py` - Kafka producer/consumer wrapper
- `core/messaging/event_bus.py` - Event bus abstraction
- `core/messaging/events.py` - Base event classes
- `core/messaging/handlers.py` - Event handler registry

**Configuration:**

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CONSUMER_GROUP=core-service-group
KAFKA_AUTO_OFFSET_RESET=earliest
```

### 1.2 Service Registry Pattern

**Files to create:**

- `core/service_registry.py` - Service discovery and registration
- `core/health_check.py` - Health check endpoints for services

### 1.3 API Gateway

**Files to create:**

- `gateway/main.py` - API Gateway entry point
- `gateway/router.py` - Request routing logic
- `gateway/middleware/` - Gateway-specific middleware

## Phase 2: Event-Driven Communication

### 2.1 Base Event System

**Create base classes:**

```python
# core/messaging/events.py
class BaseEvent:
    event_type: str
    event_id: str
    timestamp: datetime
    service_name: str
    data: dict

class DomainEvent(BaseEvent):
    """Events that represent domain changes"""
    pass

class IntegrationEvent(BaseEvent):
    """Events for inter-service communication"""
    pass
```

### 2.2 Event Publisher

**Extend BaseService:**

```python
# core/bases/base_service.py
class BaseService:
    async def publish_event(self, event: BaseEvent):
        """Publish event to Kafka"""
        await event_bus.publish(event)
```

### 2.3 Event Consumer

**Create consumer framework:**

```python
# core/messaging/consumer.py
class EventConsumer:
    async def subscribe(self, topics: List[str], handler: Callable):
        """Subscribe to Kafka topics"""
        pass
```

## Phase 3: Service Decomposition

### 3.1 Extract Services from Apps

Each app in `APPS_DIR` becomes a microservice:

```
services/
├── auth-service/
│   ├── main.py
│   ├── models/
│   ├── services/
│   ├── events/
│   └── Dockerfile
├── user-service/
│   ├── main.py
│   ├── models/
│   ├── services/
│   ├── events/
│   └── Dockerfile
├── driver-service/
│   └── ...
└── shared/
    └── core/  # Shared core library
```

### 3.2 Service Template

**Create service generator command:**

```python
# core/commands/create_service_command.py
class CreateServiceCommand(BaseCommand):
    def execute(self, service_name: str):
        """Generate microservice structure"""
        # Create service directory
        # Generate Dockerfile
        # Generate docker-compose.yml
        # Setup Kafka consumers
```

## Phase 4: Data Management

### 4.1 Database Per Service

Each service gets its own database:

- Separate connection strings
- Independent migrations
- No shared tables

### 4.2 Saga Pattern for Distributed Transactions

**Files to create:**

- `core/saga/saga_orchestrator.py`
- `core/saga/saga_step.py`
- `core/saga/compensation.py`

### 4.3 Event Sourcing (Optional)

**For critical services:**

- `core/event_sourcing/event_store.py`
- `core/event_sourcing/aggregate.py`

## Phase 5: Service Communication Patterns

### 5.1 Synchronous (REST)

- Service-to-service HTTP calls for immediate responses
- Use service discovery for endpoints

### 5.2 Asynchronous (Kafka)

- Event-driven for eventual consistency
- Command/Event separation

### 5.3 Request-Reply Pattern

**Using Kafka:**

```python
# core/messaging/request_reply.py
class RequestReplyClient:
    async def send_request(self, topic: str, request: dict) -> dict:
        """Send request and wait for reply"""
        pass
```

## Phase 6: Observability & Monitoring

### 6.1 Distributed Tracing

**Add OpenTelemetry:**

```python
# core/tracing/tracer.py
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
```

### 6.2 Centralized Logging

**Use ELK Stack:**

- Elasticsearch for storage
- Logstash for processing
- Kibana for visualization

### 6.3 Metrics

**Add Prometheus:**

```python
# core/metrics/prometheus.py
from prometheus_client import Counter, Histogram
```

## Phase 7: Deployment & DevOps

### 7.1 Docker Compose

**Create `docker-compose.yml`:**

```yaml
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
  
  kafka:
    image: confluentinc/cp-kafka:latest
  
  api-gateway:
    build: ./gateway
  
  auth-service:
    build: ./services/auth-service
  
  user-service:
    build: ./services/user-service
```

### 7.2 Kubernetes (Production)

**Create Helm charts:**

- `k8s/gateway/`
- `k8s/services/auth/`
- `k8s/kafka/`

## Implementation Checklist

### Phase 1: Infrastructure (Week 1-2)

- [ ] Setup Kafka locally (Docker)
- [ ] Create Kafka client wrapper
- [ ] Implement event bus abstraction
- [ ] Create base event classes
- [ ] Setup service registry pattern

### Phase 2: Event System (Week 2-3)

- [ ] Implement event publisher in BaseService
- [ ] Create event consumer framework
- [ ] Add event handler registry
- [ ] Implement event serialization/deserialization
- [ ] Add dead letter queue handling

### Phase 3: Service Extraction (Week 3-5)

- [ ] Create service template generator
- [ ] Extract Auth service
- [ ] Extract User service
- [ ] Extract first domain service (Driver/Passenger)
- [ ] Setup service-to-service communication

### Phase 4: Data Layer (Week 5-6)

- [ ] Separate databases per service
- [ ] Implement saga pattern
- [ ] Handle distributed transactions
- [ ] Setup data replication where needed
- [ ] Implement CQRS for read models

### Phase 5: API Gateway (Week 6-7)

- [ ] Create API Gateway service
- [ ] Implement request routing
- [ ] Add authentication/authorization
- [ ] Setup rate limiting
- [ ] Add circuit breaker pattern

### Phase 6: Observability (Week 7-8)

- [ ] Add distributed tracing
- [ ] Setup centralized logging
- [ ] Implement metrics collection
- [ ] Create monitoring dashboards
- [ ] Setup alerting

### Phase 7: Testing & Deployment (Week 8-10)

- [ ] Write integration tests
- [ ] Create Docker images for all services
- [ ] Setup docker-compose for local development
- [ ] Create Kubernetes manifests
- [ ] Setup CI/CD pipelines

## Migration Strategy

### Option 1: Strangler Fig Pattern (Recommended)

1. Keep existing monolith running
2. Extract one service at a time
3. Route new features to microservices
4. Gradually migrate existing features
5. Retire monolith when complete

### Option 2: Big Bang

1. Extract all services simultaneously
2. Deploy all at once
3. Higher risk, faster completion

## Key Considerations

### Challenges

- **Data Consistency**: Use eventual consistency and saga pattern
- **Service Discovery**: Implement service registry or use Kubernetes DNS
- **Network Latency**: Cache frequently accessed data
- **Debugging**: Implement comprehensive logging and tracing
- **Testing**: Requires contract testing and integration tests

### Best Practices

- **Event Versioning**: Version all events for backward compatibility
- **Idempotency**: Make all event handlers idempotent
- **Circuit Breakers**: Prevent cascading failures
- **Bulkheads**: Isolate resources per service
- **Retry Logic**: Implement exponential backoff

## Technology Stack

### Core

- **FastAPI**: Web framework
- **Kafka**: Event broker
- **PostgreSQL**: Database per service
- **Redis**: Caching and session storage

### Infrastructure

- **Docker**: Containerization
- **Kubernetes**: Orchestration
- **Helm**: Package management
- **Istio**: Service mesh (optional)

### Observability

- **OpenTelemetry**: Distributed tracing
- **Prometheus**: Metrics
- **Grafana**: Dashboards
- **ELK Stack**: Logging

## Next Steps

1. **Review this plan** with the team
2. **Setup local Kafka** environment
3. **Create proof of concept** with one service
4. **Define event schemas** for your domain
5. **Start with Phase 1** implementation

## Resources

- Kafka Python Client: `aiokafka`
- Service Mesh: Istio or Linkerd
- API Gateway: Kong or custom FastAPI
- Monitoring: Prometheus + Grafana
