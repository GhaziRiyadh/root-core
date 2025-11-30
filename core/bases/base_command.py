from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """Base command class."""

    def __init__(self, command_name: str):
        self.command_name = command_name

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the command."""
        pass
