"""
Base event classes for event-driven architecture.

This module defines the core event types used throughout the microservices:
- BaseEvent: Foundation for all events
- DomainEvent: Events representing domain state changes
- IntegrationEvent: Events for inter-service communication
- CommandEvent: Events representing commands/actions
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base class for all events in the system."""
    
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    service_name: str
    version: str = "1.0"
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DomainEvent(BaseEvent):
    """
    Events that represent domain state changes.
    
    These events are published when something significant happens
    in the domain (e.g., UserCreated, OrderPlaced, PaymentProcessed).
    """
    aggregate_id: Optional[str] = None
    aggregate_type: Optional[str] = None


class IntegrationEvent(BaseEvent):
    """
    Events for inter-service communication.
    
    These events are used to notify other services about changes
    that might affect them (e.g., UserRegistered, OrderShipped).
    """
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None


class CommandEvent(BaseEvent):
    """
    Events representing commands or actions to be executed.
    
    These events instruct a service to perform an action
    (e.g., CreateUser, ProcessPayment, SendNotification).
    """
    command_name: str
    reply_to: Optional[str] = None  # Topic for reply
    timeout_ms: int = 30000  # Default 30 seconds


# Event type registry for deserialization
EVENT_TYPE_REGISTRY: Dict[str, type] = {
    "base": BaseEvent,
    "domain": DomainEvent,
    "integration": IntegrationEvent,
    "command": CommandEvent,
}


def register_event_type(event_type: str, event_class: type):
    """Register a custom event type for deserialization."""
    EVENT_TYPE_REGISTRY[event_type] = event_class


def deserialize_event(event_data: dict) -> BaseEvent:
    """Deserialize event data into the appropriate event class."""
    event_type = event_data.get("event_type", "base")
    event_class = EVENT_TYPE_REGISTRY.get(event_type, BaseEvent)
    return event_class(**event_data)
