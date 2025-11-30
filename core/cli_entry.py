import typer
from typing import List, Type
from core.bases.base_command import BaseCommand
from core.commands.clean_command import CleanCommand

app = typer.Typer(help="Core Framework CLI")


class CLIEntry:
    def __init__(self):
        self.app = app
        self._register_default_commands()

    def _register_default_commands(self):
        self.register_command(CleanCommand)

    def register_command(self, command_class: Type[BaseCommand]):
        """Register a command class with the CLI."""
        instance = command_class(command_name=command_class.__name__.lower().replace("command", ""))
        
        # Create a wrapper function to be used as the command handler
        def command_wrapper():
            instance.execute()
            
        # Register the command with Typer
        self.app.command(name=instance.command_name)(command_wrapper)

    def run(self):
        """Run the CLI application."""
        self.app()

cli = CLIEntry()
