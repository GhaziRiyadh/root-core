"""
Kafka client wrapper for producing and consuming events.

This module provides a high-level interface to Kafka using aiokafka,
with automatic serialization, error handling, and retry logic.
"""
import asyncio
import json
import logging
from typing import Callable, List, Optional, Dict, Any
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError

from core.config import settings
from core.messaging.events import BaseEvent, deserialize_event

logger = logging.getLogger(__name__)


class KafkaClient:
    """Kafka client for producing and consuming events."""
    
    def __init__(
        self,
        bootstrap_servers: str = None,
        client_id: str = None,
    ):
        self.bootstrap_servers = bootstrap_servers or settings.KAFKA_BOOTSTRAP_SERVERS
        self.client_id = client_id or settings.PROJECT_NAME
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumers: Dict[str, AIOKafkaConsumer] = {}
        self._running = False
    
    async def start(self):
        """Start the Kafka client (producer and consumers)."""
        if self._running:
            return
        
        try:
            # Initialize producer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=f"{self.client_id}-producer",
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                compression_type="gzip",
                acks='all',  # Wait for all replicas
                retries=3,
            )
            await self.producer.start()
            self._running = True
            logger.info(f"Kafka producer started: {self.bootstrap_servers}")
        except KafkaError as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            raise
    
    async def stop(self):
        """Stop the Kafka client."""
        if not self._running:
            return
        
        # Stop producer
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
        
        # Stop all consumers
        for consumer_id, consumer in self.consumers.items():
            await consumer.stop()
            logger.info(f"Kafka consumer stopped: {consumer_id}")
        
        self.consumers.clear()
        self._running = False
    
    async def publish(
        self,
        topic: str,
        event: BaseEvent,
        key: Optional[str] = None,
    ) -> bool:
        """
        Publish an event to a Kafka topic.
        
        Args:
            topic: Kafka topic name
            event: Event to publish
            key: Optional partition key
            
        Returns:
            True if published successfully
        """
        if not self._running or not self.producer:
            raise RuntimeError("Kafka client not started")
        
        try:
            # Serialize event
            event_data = event.model_dump()
            
            # Send to Kafka
            key_bytes = key.encode('utf-8') if key else None
            await self.producer.send_and_wait(
                topic,
                value=event_data,
                key=key_bytes,
            )
            
            logger.debug(f"Published event {event.event_id} to topic {topic}")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            return False
    
    async def subscribe(
        self,
        topics: List[str],
        group_id: str,
        handler: Callable[[BaseEvent], None],
        consumer_id: Optional[str] = None,
    ):
        """
        Subscribe to Kafka topics and process events.
        
        Args:
            topics: List of topic names to subscribe to
            group_id: Consumer group ID
            handler: Async function to handle events
            consumer_id: Optional unique consumer identifier
        """
        consumer_id = consumer_id or f"{group_id}-{'-'.join(topics)}"
        
        if consumer_id in self.consumers:
            logger.warning(f"Consumer {consumer_id} already exists")
            return
        
        try:
            # Create consumer
            consumer = AIOKafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                client_id=f"{self.client_id}-{consumer_id}",
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
                enable_auto_commit=True,
            )
            
            await consumer.start()
            self.consumers[consumer_id] = consumer
            logger.info(f"Consumer {consumer_id} subscribed to {topics}")
            
            # Start consuming in background
            asyncio.create_task(self._consume_loop(consumer, handler, consumer_id))
            
        except KafkaError as e:
            logger.error(f"Failed to create consumer {consumer_id}: {e}")
            raise
    
    async def _consume_loop(
        self,
        consumer: AIOKafkaConsumer,
        handler: Callable[[BaseEvent], None],
        consumer_id: str,
    ):
        """Internal loop for consuming messages."""
        try:
            async for msg in consumer:
                try:
                    # Deserialize event
                    event = deserialize_event(msg.value)
                    
                    # Handle event
                    await handler(event)
                    
                    logger.debug(
                        f"Consumer {consumer_id} processed event {event.event_id} "
                        f"from {msg.topic}"
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Error processing event in consumer {consumer_id}: {e}",
                        exc_info=True
                    )
                    # Continue processing other messages
                    
        except asyncio.CancelledError:
            logger.info(f"Consumer {consumer_id} cancelled")
        except Exception as e:
            logger.error(f"Consumer {consumer_id} error: {e}", exc_info=True)


# Global Kafka client instance
_kafka_client: Optional[KafkaClient] = None


def get_kafka_client() -> KafkaClient:
    """Get the global Kafka client instance."""
    global _kafka_client
    if _kafka_client is None:
        _kafka_client = KafkaClient()
    return _kafka_client
