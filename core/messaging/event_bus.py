"""
Event bus abstraction for publishing and subscribing to events.

This module provides a high-level interface for event-driven communication,
abstracting away the underlying messaging infrastructure (Kafka).
"""
import logging
from typing import Callable, List, Type
from core.messaging.events import BaseEvent
from core.messaging.kafka_client import get_kafka_client

logger = logging.getLogger(__name__)


class EventBus:
    """
    Event bus for publishing and subscribing to domain events.
    
    This provides a clean abstraction over the Kafka client,
    making it easy to switch messaging systems if needed.
    """
    
    def __init__(self):
        self.kafka_client = get_kafka_client()
        self._handlers = {}
    
    async def start(self):
        """Start the event bus."""
        await self.kafka_client.start()
        logger.info("Event bus started")
    
    async def stop(self):
        """Stop the event bus."""
        await self.kafka_client.stop()
        logger.info("Event bus stopped")
    
    async def publish(
        self,
        topic: str,
        event: BaseEvent,
        key: str = None,
    ) -> bool:
        """
        Publish an event to a topic.
        
        Args:
            topic: Topic name (e.g., 'user.events', 'order.events')
            event: Event to publish
            key: Optional partition key (e.g., user_id, order_id)
            
        Returns:
            True if published successfully
        """
        logger.info(
            f"Publishing {event.event_type} event {event.event_id} to {topic}"
        )
        return await self.kafka_client.publish(topic, event, key)
    
    async def subscribe(
        self,
        topics: List[str],
        handler: Callable[[BaseEvent], None],
        group_id: str = None,
    ):
        """
        Subscribe to topics and handle events.
        
        Args:
            topics: List of topic names to subscribe to
            handler: Async function to handle events
            group_id: Consumer group ID (defaults to service name)
        """
        from core.config import settings
        group_id = group_id or f"{settings.PROJECT_NAME}-consumer-group"
        
        logger.info(f"Subscribing to topics {topics} with group {group_id}")
        await self.kafka_client.subscribe(topics, group_id, handler)
    
    def register_handler(
        self,
        event_type: str,
        handler: Callable[[BaseEvent], None],
    ):
        """
        Register a handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Async function to handle the event
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Registered handler for event type: {event_type}")
    
    async def dispatch(self, event: BaseEvent):
        """
        Dispatch an event to registered handlers.
        
        This is useful for handling events received from subscriptions.
        """
        handlers = self._handlers.get(event.event_type, [])
        
        if not handlers:
            logger.warning(f"No handlers registered for event type: {event.event_type}")
            return
        
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(
                    f"Error in handler for {event.event_type}: {e}",
                    exc_info=True
                )


# Global event bus instance
_event_bus: EventBus = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
