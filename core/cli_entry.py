import typer
from typing import Type
from core.bases.base_command import BaseCommand
from core.commands.clean_command import CleanCommand
from core.commands.app_create_command import AppCreateCommand
from core.commands.model_command import ModelCommand
from core.commands.full_command import FullCommand
from core.commands.list_apps_command import ListAppsCommand
from core.commands.delete_app_command import DeleteAppCommand
from core.commands.delete_model_command import DeleteModelCommand
from core.commands.generate_permissions_command import GeneratePermissionsCommand

app = typer.Typer(help="Core Framework CLI")


class CLIEntry:
    def __init__(self):
        self.app = app
        self._register_default_commands()

    def _register_default_commands(self):
        self.register_command(CleanCommand)
        self.register_command(AppCreateCommand)
        self.register_command(ModelCommand)
        self.register_command(FullCommand)
        self.register_command(ListAppsCommand)
        self.register_command(DeleteAppCommand)
        self.register_command(DeleteModelCommand)
        self.register_command(GeneratePermissionsCommand)

    def register_command(self, command_class: Type[BaseCommand]):
        """Register a command class with the CLI."""
        # Use the class name as the command name, converted to kebab-case
        # e.g. AppCreateCommand -> app-create
        import re
        name = command_class.__name__.replace("Command", "")
        # Convert CamelCase to kebab-case
        name = re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()
        
        instance = command_class(command_name=name)
        
        # Register the command with Typer using the instance's execute method
        # Typer will inspect the execute method for arguments
        self.app.command(name=name)(instance.execute)

    def run(self):
        """Run the CLI application."""
        self.app()

cli = CLIEntry()
