# Kafka Infrastructure Setup

This guide explains how to set up and use the Kafka infrastructure for event-driven microservices.

## Quick Start

### 1. Start Kafka Locally

```bash
docker-compose -f docker-compose.kafka.yml up -d
```

This starts:

- **Zookeeper** on port 2181
- **Kafka** on port 9092
- **Kafka UI** on port 8080 (<http://localhost:8080>)

### 2. Configure Your Application

Add to your `.env`:

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CONSUMER_GROUP=core-consumer-group
KAFKA_AUTO_OFFSET_RESET=earliest
```

### 3. Install Dependencies

```bash
poetry add aiokafka
# or
pip install aiokafka
```

## Usage Examples

### Publishing Events

```python
from core.messaging.event_bus import get_event_bus
from core.messaging.events import DomainEvent

# Get event bus instance
event_bus = get_event_bus()

# Start event bus
await event_bus.start()

# Create and publish an event
event = DomainEvent(
    event_type="user.created",
    service_name="user-service",
    data={
        "user_id": "123",
        "email": "user@example.com",
        "name": "John Doe"
    },
    aggregate_id="123",
    aggregate_type="User"
)

await event_bus.publish("user.events", event, key="123")
```

### Subscribing to Events

```python
from core.messaging.event_bus import get_event_bus
from core.messaging.events import BaseEvent

async def handle_user_event(event: BaseEvent):
    """Handle user events."""
    print(f"Received event: {event.event_type}")
    print(f"Data: {event.data}")
    
    if event.event_type == "user.created":
        # Handle user creation
        user_id = event.data.get("user_id")
        print(f"New user created: {user_id}")

# Get event bus
event_bus = get_event_bus()
await event_bus.start()

# Subscribe to topics
await event_bus.subscribe(
    topics=["user.events"],
    handler=handle_user_event,
    group_id="notification-service"
)
```

### Using Event Handlers

```python
from core.messaging.event_bus import get_event_bus
from core.messaging.events import BaseEvent

# Register handlers for specific event types
event_bus = get_event_bus()

@event_bus.register_handler("user.created")
async def on_user_created(event: BaseEvent):
    user_id = event.data.get("user_id")
    # Send welcome email
    print(f"Sending welcome email to user {user_id}")

@event_bus.register_handler("user.deleted")
async def on_user_deleted(event: BaseEvent):
    user_id = event.data.get("user_id")
    # Clean up user data
    print(f"Cleaning up data for user {user_id}")

# Dispatch events to registered handlers
await event_bus.dispatch(event)
```

## Event Types

### BaseEvent

Foundation for all events. Contains:

- `event_id`: Unique identifier
- `event_type`: Type of event (e.g., "user.created")
- `timestamp`: When the event occurred
- `service_name`: Service that published the event
- `version`: Event schema version
- `data`: Event payload
- `metadata`: Additional metadata

### DomainEvent

For domain state changes:

- Inherits from `BaseEvent`
- Adds `aggregate_id` and `aggregate_type`
- Example: UserCreated, OrderPlaced, PaymentProcessed

### IntegrationEvent

For inter-service communication:

- Inherits from `BaseEvent`
- Adds `correlation_id` and `causation_id`
- Example: UserRegistered, OrderShipped

### CommandEvent

For commands/actions:

- Inherits from `BaseEvent`
- Adds `command_name`, `reply_to`, `timeout_ms`
- Example: CreateUser, ProcessPayment

## Topic Naming Convention

Use the pattern: `<domain>.<event_type>`

Examples:

- `user.events` - All user-related events
- `order.events` - All order-related events
- `payment.events` - All payment-related events
- `notification.commands` - Notification commands

## Monitoring

Access Kafka UI at <http://localhost:8080> to:

- View topics and messages
- Monitor consumer groups
- Check broker health
- Debug event flow

## Best Practices

1. **Event Versioning**: Always include version in events
2. **Idempotency**: Make event handlers idempotent
3. **Error Handling**: Use try-catch in handlers
4. **Dead Letter Queue**: Handle failed events (coming in Phase 2)
5. **Partition Keys**: Use meaningful keys for ordering (e.g., user_id)

## Troubleshooting

### Kafka not connecting

```bash
# Check if Kafka is running
docker ps | grep kafka

# View Kafka logs
docker logs core-kafka

# Restart Kafka
docker-compose -f docker-compose.kafka.yml restart
```

### Events not being consumed

- Check consumer group ID is unique per service
- Verify topic exists in Kafka UI
- Check offset reset strategy

## Next Steps

- [ ] Integrate event bus with BaseService
- [ ] Add dead letter queue handling
- [ ] Implement event replay functionality
- [ ] Add schema registry for event validation
